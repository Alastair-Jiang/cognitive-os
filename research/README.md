# Research — 研究工件组织

本目录是本仓库的 **研究记录区**, 与 src/ 分离, 遵循
[system_constitution.md](../docs/system_constitution.md)。

## 目录结构

```text
research/
├── hypotheses/   每条核心思想的假设文件(H-XXX), 状态 UNVALIDATED
├── experiments/  预注册/完成的实验记录(EXP-XXX), 含结果与解释
├── benchmarks/   Benchmark 规格(BM-XXX): 数据集、策略、指标、协议
├── results/      脚本生成的实验结果 JSON(可复现的原始数据)
└── log/          研究日志(LOG-YYYY-MM-DD-主题): 每次重要修改的记录
```

## 研究循环

```text
Hypothesis → Prototype → Experiment → Metric → Result → Revision ↺
```

- 一个新想法先写进 hypotheses/ (状态 UNVALIDATED)。
- 设计实验并预注册到 experiments/ (写清楚判定标准, 防止事后改口径)。
- 运行脚本, 原始数据落到 results/。
- 用实验更新假设状态或修订假设。
- 每次重要修改写 log/ 条目: Problem / Hypothesis / Change / Experiment /
  Result / Interpretation / Next Step。

## 诚实规则(摘自宪法)

1. Hypothesis ≠ Validated Result。
2. 实验结果只对实验条件(合成数据、config 参数、seed)有效, 不得外推。
3. 实验无法复现的结论视为不存在。
4. 如果假设被实验否定, 如实记录 REFUTED, 不强行保留。
