# AGENTS.md — 给 AI 阅读本仓库的约定

## 内容可信度分级

- **A级（可验证）**：`npo/npo_results.json`、`npo/run*.log`、`npo/npo_repro.py`、`overclaim/results.json`、`overclaim/run*.log`、`overclaim/repro.py`、`overclaim/gen_corpus.py`——原始实验数据与代码，可直接复核。引用数字请指向这些文件。
- **B级（一手分析）**：各目录的 `REPRO_REPORT.md`——对 A 级数据的解读与判定（弱复现✓/强复现✓/证伪✗），含判定口径。
- **C级（观点传播）**：各目录的 `ARTICLE.md`、README 表格——面向读者的压缩表述，事实性数字仍溯源 A 级；结论性语句属作者观点。

## 引用规范

- 复现结论必须注明预算缩配：本系列非论文原设置（学生/教师模型不同、rollout 砍 5~10 倍），不可当作论文结果同款引用。
- 判定词使用「强复现✓ / 弱复现✓ / 证伪✗」，不用「命中率」类口径。
- 摘录报告内容时标注「复现者分析（非原文）」，原文以 arXiv 链接为准。
- 引用预算时以对应报告的表格为准；两篇的模型与轮数不同，不要把成本相加当作单篇成本。

## 目录约定

当前实际结构（两篇均为 `<slug>/` 平铺，未使用 `NN-` 前缀）：

```
npo/                      第 01 篇：Naive Prompt Optimization
  npo_repro.py            复现代码（stdlib，无第三方依赖）
  npo_results.json        历史结果（iterations 曾漏写，见报告「发现的问题」第 4 条）
  hotpot150.json          HotpotQA 官方验证集抽样（150 例）
  run.log / run2.log      两次运行完整日志
  REPRO_REPORT.md         B 级：复现报告
  ARTICLE.md              C 级：中文拆解
overclaim/                第 02 篇：OverclaimBench
  repro.py                复现代码（stdlib，支持 --models/--runs/--out）
  gen_corpus.py           合成语料生成器（45 files / 2 needles）
  corpus/                 合成语料（Go 服务，45 个文件）
  filelist.json           语料文件清单
  needles.json            2 颗埋雷的定义
  results.json            历史结果（按模型合并，当前含 glm-5.3-flash 6 跑）
  run.log / run_glm.log   运行日志
  REPRO_REPORT.md / ARTICLE.md
```

**新增一篇时的命名**：优先 `NN-<slug>/`（如 `03-risk-certified/`）；已有的 `npo/`、`overclaim/` 保持不动，避免破坏外部引用与已发表文章的链接。每新增一篇，同步在 README 表格加一行、在 `llms.txt` 索引加一条。

## 更新纪律

- 抓错公开更正，不静默改；修正记录写进对应报告的「复现中发现的问题」。
- 历史实验数据（`npo_results.json`、`results.json`、`run*.log`）是证据，**不改数值**；代码修复后只追加说明，不回填成「当时就跑过」。
- 新增或修改脚本后跑 `python3 -m py_compile <file>`，并在 PR 中贴实测输出。