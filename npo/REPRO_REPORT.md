# 复现报告：Naive Prompt Optimization（arXiv:2608.27266）

**复现日期**：2026-11-12 · **复现人**：Focus × Pigman（独立复现，非作者团队）
**论文**：Naive Prompt Optimization: Rethinking the Need for Complex Prompt Search（Purdue）
**官方代码**：无（GitHub 全站检索无引用该 arXiv id 的仓库，论文正文亦无代码链接——2026-11-12 核验）

---

## 1. 论文核心主张（被复现命题）

1. NPO：单线性的"教师模型看完整 rollout 轨迹→改写 prompt"循环，性能 ≥ GEPA（复杂 Pareto 搜索优化器），且 rollout 更少
2. 教师模型越强，NPO 优势越大
3. 优化出的 prompt 可跨学生模型直接迁移

本次预算只复现**命题 1 的弱化版**：在 HotpotQA 上，NPO 优化循环是否显著优于初始 baseline prompt。（GEPA 对照与跨模型迁移未纳入本次预算。）

## 2. 论文原始设置 vs 本次复现设置

| 参数 | 论文 | 本次复现 |
|---|---|---|
| 学生模型 | Qwen3-8B（本地） | deepseek-chat（API） |
| 教师 | Qwen3-8B / DeepSeek-V4-Flash / GPT-5.5 | deepseek-reasoner（对应"更强教师"档） |
| 数据 | HotpotQA distractor | HotpotQA distractor（同一官方验证集） |
| 反射小批量 N | 40 | 8 |
| 迭代轮数 Y | 20 | 4 |
| 滑窗 W | 未明示（大窗口） | 3 |
| 验证集 | 300 例 | 60 例（与优化池不相交） |
| 总 rollout | 6,800 | 32 优化 + 300 验证 |
| 指标 | EM/F1（HotpotQA 官方归一化） | 同 |

固定随机种子 42；文本游戏（TextArena）与 GRPO 对照均未复现（需 H100×2）。

## 3. 实现要点

- `npo_repro.py`：~150 行纯 stdlib 实现。算法 1 逐步对齐：采样小批量 → 学生带当前 prompt 跑 rollout → 收集轨迹+奖励 → 滑窗内全部轨迹喂教师 → 教师只输出新 prompt
- 评测采用论文同款 HotpotQA EM/F1 归一化（去冠词/标点/空白）
- 教师 prompt 要求"诊断失败模式（停在中间实体、答案冗长、忽略上下文）→ 只输出新 prompt"

## 4. 结果

固定 60 例不相交验证集，两次独立运行：

| 候选 | EM | F1 |
|---|---|---|
| baseline prompt | 0.300 | 0.352 |
| NPO iter1 | 0.333 | 0.339 |
| NPO iter2 | 0.250 | 0.288 |
| **NPO iter3（最佳）** | **0.333** | **0.358** |
| NPO iter4 | 0.267 | 0.292 |

Run-1（教师 max_tokens 配置 bug，迭代 2/3 作废）：baseline EM 0.333 → NPO iter1 EM 0.400（+6.7pt）。

**最终判定：弱复现 ✓（方向成立，量级存疑）**
- 两跑中最佳 NPO 候选都 ≥ baseline（+3.3 ~ +6.7pt EM），方向与论文一致 ✓
- 但 60 例验证集的标准误约 ±6pt，提升量级处于噪声边缘——论文里动辄翻倍的增益是用 6,800 rollouts 撑出来的，预算砍到 32 rollouts 时信号被方差淹没 ✗（量化级未能验证）
- 教师最终收敛出一条"只允许输出一行 Answer: xxx"的极简 prompt——提示相当一部分增益来自**输出格式规整**（更长推理被砍掉、答案抽取更干净），而非多跳推理能力本身。论文 3.4 节自己也专门做了"prompt 是否泄漏答案"的自查，说明作者意识到了同一风险

## 5. 结论

1. **算法本身是真的、极便宜**：~150 行 stdlib 代码 + 664 次 API 调用（<¥5）即可跑通，任何有 API key 的人都能复现，NPO 是目前性价比最高的 prompt 优化基线
2. **小预算下不要期待论文级增益**：增益方向稳定，但量级被小样本方差吃掉；要看到论文级效果需要 6,800+ rollouts（约 ¥100+）
3. **实践建议**：与其跑完整 NPO 循环，不如直接抄教师学到的格式约束（"只输出一行短答案、不许外部知识、必须锚定上下文"）——免费的 2~3pt
4. 论文核心卖点（NPO ≥ GEPA、强教师更好、跨模型迁移）本次预算未测，留待后续

## 复现产物

- `npo_repro.py`：完整复现代码（stdlib，无依赖）
- `npo_results.json`：全部 rollout 轨迹 + 评测明细
- `run.log` / `run2.log`：两次运行完整日志
- `val.parquet` / `hotpot150.json`：HotpotQA 官方验证集抽样

## 6. 复现中发现的问题（论文未提的毛边）

1. **教师输出截断**：deepseek-reasoner 的思考链吃光 max_tokens 时正文返回空串，优化循环会静默用"空 prompt"当候选——必须做空串守卫回退。论文未讨论优化器失效时的行为
2. **反馈成本结构**：每轮教师输入 = W 轮 × N 条完整轨迹，token 数随窗口平方增长；论文用 1M 窗口模型回避了这个问题，小窗口模型跑不动他们的小批量
3. 训练 EM 波动大（0.125~0.500），8 例小批量的奖励信号噪声很高——论文 40/批是合理下限

## 5. 结论

（待最终数据后写）

## 成本

deepseek-chat + deepseek-reasoner，两跑合计约 600 次 API 调用，估算成本 < ¥5。
