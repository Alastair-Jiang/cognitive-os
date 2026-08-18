# System Constitution — 系统宪法(行为约束)

> 本文是**最高优先级的行为约束**。任何代码、文档、实验记录、
> commit message 都不得违反本文。违者视为缺陷, 需修复。

## 1. 科研诚实: Hypothesis ≠ Validated Result

- "听起来合理"不是证据。
- 未经验证的思想只能标注为 Hypothesis / [H] / UNVALIDATED。
- 只有经过 research/experiments/ 中可复现实验支持的结果才能写为
  Validated Result / [V]。
- **禁止**将未经验证的思想包装为:
  - "Novel breakthrough" / "AGI architecture" / "Human-level intelligence"
  - "Proven efficient" / "显著优于" (无实验支撑时)
- 实验无法复现的结论视为不存在。

## 2. 实验纪律: Research-driven Incremental Development

每一个核心思想必须形成闭环:

```text
Hypothesis → Prototype → Experiment → Metric → Result → Revision
```

- 任何新概念不能因为"听起来合理"就直接进入核心架构。
- 不要一开始就实现全部功能。**不要为了"看起来先进"而增加复杂度。**
- 一个功能只有在它能被实验证伪或证实时才值得进入核心。

## 3. 检索效率的诚实计量

- 所有检索策略必须记录: `similarity_calls`(计算成本/API 调用代理)、
  `index_lookups`、`iterations`、`latency_ms`。
- 索引构建成本与查询时成本分开标注, 不得混报。

## 4. 用户数据与推断控制

- **最小化数据收集**: 只收集完成任务所需的数据。
- **Memory Control**: 用户必须能够 View / Edit / Delete / Export 自己的记忆。
- **Data Ownership**: 明确数据归属和使用边界。
- **Inference Control**: 模型推断 ≠ 用户事实。系统不能把推断包装成用户事实
  (例如 L3/L4 记忆必须来自行为证据, 而非猜测)。
- **Anti-Echo-Chamber**: 系统应主动保留 Counter Evidence、Diverse Sources、
  Contradictory Views、Uncertainty、Alternative Hypotheses。

## 5. 权限与高危领域

- Agent 权限分级: Level 0 Answer only → Level 1 Search → Level 2 修改数字文件
  → Level 3 调用外部服务 → Level 4 物理世界动作。权限越高, 确认与审计越严格。
- 高危领域(医疗/金融/法律/保险/物理安全)必须: 人工确认 + 证据要求 + 风险控制。

## 6. Capability Interface 原则

- 核心架构不写死任何模型厂商。
- 模型接入一律通过 Capability Adapter。
- 核心是能力接口, 不是模型依赖。

## 7. 研究日志纪律

每次重要修改必须记录(见 research/log/ 模板):

```text
Problem / Hypothesis / Change / Experiment / Result / Interpretation / Next Step
```

禁止只写 "Added feature X"。应写:
"We hypothesized X would reduce retrieval latency while preserving recall.
Experiment Y showed ..."

## 8. Commit 纪律

Commit message 尽量表达研究意义:

```text
feat(retrieval): add anchor-based candidate expansion
experiment(net): benchmark dynamic search against baseline
fix(validation): prevent premature candidate elimination
research(memory): evaluate long-term user preference storage
docs(architecture): define cognitive graph abstraction
```

避免大量使用: `update` / `fix` / `test` / `new` / `final` / `final2`。

## 9. 反虚荣复杂度

- 如果一个模块没有实验支撑, 它就是 STUB, 不假装实现。
- 任何"听起来先进"但无法实验度量的概念, 留在 docs 的 Vision 里,
  不进核心代码。

## 10. 本宪法自身的修订

- 本宪法可修订, 但修订必须有 commit 级理由记录(不能静默改动)。
- 修改本文件需要同时在研究日志中记录修订动机。
