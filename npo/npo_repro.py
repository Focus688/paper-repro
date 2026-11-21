#!/usr/bin/env python3
"""Minimal reproduction of 'Naive Prompt Optimization' (arXiv:2608.27266).

Budget-scaled from the paper's HotpotQA setting (minibatch 40 / 20 iterations /
300-example val) down to N=8 / Y=4 / 60-example val, to fit a small API budget.
Student: deepseek-chat. Teacher: deepseek-reasoner (the paper's "stronger
teacher" regime). Metric: official HotpotQA EM / F1.
"""
import json, os, re, string, sys, time, collections, urllib.request

BASE = "https://api.deepseek.com"
KEY = os.environ.get("DEEPSEEK_API_KEY")  # 延迟到 main 校验，保证 --check/--help 不需要 key
STUDENT = "deepseek-chat"
TEACHER = "deepseek-reasoner"
OUT = os.path.dirname(os.path.abspath(__file__))

with open(f"{OUT}/hotpot150.json") as f:
    DATA = json.load(f)
MINIBATCH_POOL = DATA[:60]   # optimization minibatches sampled from here
VAL = DATA[60:120]           # fixed, disjoint validation set
N, W, Y = 8, 3, 4

INITIAL_PROMPT = (
    "Answer the question using only the provided contexts. "
    "Think step by step, then give the final answer after 'Answer:' on the last line. "
    "Keep the final answer as short as possible (a name, date, or entity)."
)

def norm(s):
    s = re.sub(r"\b(a|an|the)\b", " ", s.lower())
    s = "".join(c for c in s if c not in string.punctuation)
    return " ".join(s.split())

def f1(pred, gold):
    pt, gt = norm(pred).split(), norm(gold).split()
    common = collections.Counter(pt) & collections.Counter(gt)
    o = sum(common.values())
    if o == 0: return 0.0
    return 2*o/(len(pt)+len(gt))

def em(pred, gold):
    return float(norm(pred) == norm(gold))

def chat(model, messages, temperature=1.0, retries=4):
    body = json.dumps({"model": model, "messages": messages,
                       "temperature": temperature, "max_tokens": 8000 if model == TEACHER else 2000}).encode()
    for a in range(retries):
        try:
            req = urllib.request.Request(f"{BASE}/chat/completions", data=body,
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
            r = json.loads(urllib.request.urlopen(req, timeout=180).read())
            return r["choices"][0]["message"]["content"], r["usage"]
        except Exception as e:
            print(f"  retry {a+1} {model}: {e}", flush=True)
            time.sleep(15*(a+1))
    raise RuntimeError("API failed")

def get_answer(text):
    m = re.findall(r"answer\s*[:：]\s*(.+)", text, re.I)
    line = m[-1].strip() if m else text.strip().splitlines()[-1]
    return line.strip("\"' .")

def run_student(prompt, exs):
    out = []
    for ex in exs:
        msgs = [{"role":"user","content": f"{prompt}\n\nQuestion: {ex['question']}\n\nAnswer:"}]
        txt, usage = chat(STUDENT, msgs)
        ans = get_answer(txt)
        out.append({"id": ex["id"], "question": ex["question"], "gold": ex["answer"],
                    "raw": txt[:1500], "pred": ans,
                    "em": em(ans, ex["answer"]), "f1": f1(ans, ex["answer"])})
    return out

def eval_val(prompt):
    res = run_student(prompt, VAL)
    return {"em": sum(r["em"] for r in res)/len(res),
            "f1": sum(r["f1"] for r in res)/len(res),
            "detail": res}

def teacher_revise(prompt, window):
    hist = []
    for it in window:
        hist.append(f"## Iteration {it['i']} prompt:\n{it['prompt']}")
        for r in it["rollouts"]:
            hist.append(f"- Q: {r['question']}\n  gold: {r['gold']} | model: {r['pred']} "
                        f"(EM={int(r['em'])}, F1={r['f1']:.2f})\n  trace: {r['raw'][:600]}")
    instr = (
        "You are an expert prompt optimizer. Below is the history of recent iterations: "
        "the system prompt used, rollout traces of a student LLM on HotpotQA multi-hop "
        "questions, and per-example EM/F1 vs gold answers. Diagnose failure modes "
        "(e.g. wrong entity, verbose answers, ignoring context, missing multi-hop chaining) "
        "and rewrite the prompt to fix them. Output ONLY the new prompt text, nothing else.\n\n"
        + "\n".join(hist)
    )
    txt, _ = chat(TEACHER, [{"role":"user","content":instr}], temperature=1.0)
    new = txt.strip()
    if new.startswith("```"):
        new = "\n".join(new.splitlines()[1:-1])
    if len(new) < 20:  # teacher returned empty/refusal -> keep current prompt
        print("  [warn] teacher produced empty revision, keeping current prompt", flush=True)
        return prompt
    return new

def check():
    """离线自检：数据完整性 + 结果文件可解析。不调用 API。"""
    errs, warns = [], []
    if len(DATA) != 150:
        errs.append(f"hotpot150.json 应有 150 题，实际 {len(DATA)}")
    need = {"id", "question", "answer"}
    for i, r in enumerate(DATA[:5]):
        lack = need - set(r)
        if lack:
            errs.append(f"第 {i} 条缺字段 {sorted(lack)}")
    ids = [r.get("id") for r in DATA]
    if len(set(ids)) != len(ids):
        errs.append("题目 id 有重复")
    if len(MINIBATCH_POOL) != 60 or len(VAL) != 60:
        errs.append(f"切分异常：pool={len(MINIBATCH_POOL)} val={len(VAL)}（应为 60/60）")
    fp = f"{OUT}/npo_results.json"
    if os.path.exists(fp):
        try:
            r = json.load(open(fp, encoding="utf-8"))
            if not isinstance(r, dict) or "log" not in r:
                errs.append("npo_results.json 结构异常（缺 log）")
            elif not r["log"].get("iterations"):
                warns.append("npo_results.json 的 iterations 为空——历史产物可能未落盘轨迹")
        except json.JSONDecodeError as e:
            errs.append(f"npo_results.json 不是合法 JSON: {e}")
    for w in warns:
        print("  WARN:", w)
    if errs:
        print("CHECK FAILED:")
        for e in errs:
            print("  -", e)
        return 1
    print(f"CHECK OK: {len(DATA)} 题，pool={len(MINIBATCH_POOL)} val={len(VAL)}")
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser(description="NPO budget-scaled reproduction")
    ap.add_argument("--check", action="store_true", help="只做离线自检，不调用 API")
    args = ap.parse_args()
    if args.check:
        return check()
    if not KEY:
        print("缺少 DEEPSEEK_API_KEY；用 --check 可做离线自检", flush=True)
        return 2
    import random
    rng = random.Random(42)
    log = {"initial_prompt": INITIAL_PROMPT, "iterations": []}
    cur = INITIAL_PROMPT
    window = []
    for i in range(Y):
        t0 = time.time()
        batch = rng.sample(MINIBATCH_POOL, N)
        rollouts = run_student(cur, batch)
        entry = {"i": i, "prompt": cur, "rollouts": rollouts,
                 "train_em": sum(r["em"] for r in rollouts)/N,
                 "train_f1": sum(r["f1"] for r in rollouts)/N}
        window.append(entry)
        print(f"[iter {i}] train EM={entry['train_em']:.3f} F1={entry['train_f1']:.3f}", flush=True)
        cur = teacher_revise(cur, window[-W:])
        entry["next_prompt"] = cur
        # 每轮轨迹必须落盘：REPRO_REPORT 承诺「全部 rollout 轨迹 + 评测明细」，
        # 旧版只把 entry 留在内存 window 里，npo_results.json 的 iterations 永远是空数组。
        log["iterations"].append(entry)
        json.dump({"log": log, "val_results": []},
                  open(f"{OUT}/npo_results.json", "w"), ensure_ascii=False, indent=2)
        print(f"[iter {i}] new prompt ({time.time()-t0:.0f}s):\n{cur}\n", flush=True)
    # final eval of every candidate on the fixed val set
    print("Evaluating all candidates on val set...", flush=True)
    results = []
    cands = [(0, "initial", INITIAL_PROMPT)] + [(e["i"]+1, "after_iter", e["next_prompt"]) for e in window]
    for tag, label, p in cands:
        v = eval_val(p)
        # detail = 逐题 EM/F1/预测/原始输出，必须随结果落盘，否则「可复核」只是口号
        results.append({"candidate": f"iter{tag}", "em": v["em"], "f1": v["f1"],
                        "detail": v["detail"]})
        print(f"val iter{tag}: EM={v['em']:.3f} F1={v['f1']:.3f}", flush=True)
        log.setdefault("prompts", []).append({"iter": tag, "prompt": p})
        json.dump({"log": log, "val_results": results},
                  open(f"{OUT}/npo_results.json","w"), ensure_ascii=False, indent=2)
    json.dump({"log": log, "val_results": results},
              open(f"{OUT}/npo_results.json","w"), ensure_ascii=False, indent=2)
    print("DONE", flush=True)

if __name__ == "__main__":
    raise SystemExit(main())
