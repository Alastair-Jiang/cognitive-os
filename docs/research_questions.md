# Research Questions — 研究问题清单

> 每条研究问题都带状态: `UNVALIDATED`(未验证, 即 Hypothesis) /
> `PARTIAL`(部分证据) / `VALIDATED`(已有本仓库实验支持) /
> `REFUTED`(被实验否定)。
> 状态只能由 research/ 下的实验记录更新, 不允许凭直觉修改。

## Phase 1: Dynamic Retrieval(当前阶段)

> 状态更新(2026-08-19, 依据 EXP-001): 首轮实验已在高歧义合成语料上完成,
> 结论见各 RQ 状态。**扁平语义基线 A 在质量指标上是基准。**

### RQ-1 [PARTIAL] Dynamic Net 是否真的比传统检索更有效?
- **现状(EXP-001)**: 在高歧义档位上, 多网动态检索(C)F1@k=0.490 < 基线 A=0.637,
  且成本为 14× → **未证明更有效**。渐进验证的早停机制有效(75% 查询提前停止),
  但未转化为质量收益。
- **关联实验**: EXP-001
- **下一步**: EXP-002 诊断网配置互补性与共识聚合; 歧义档位扫描。

### RQ-2 [PARTIAL] Anchor 机制能否在不显著损失 P/R 的情况下降低复杂度?
- **现状(EXP-001)**: 效率部分成立(B 的 sim_calls 为 A 的 23%, 4.3× 省);
  质量部分未达预注册容忍线(Recall 损失 22.6pp > 10pp)。MRR 反超(0.933 vs 0.794)。
- **下一步**: 检验召回损失是否随歧义降低而收敛。

### RQ-3 [NOT SUPPORTED] Progressive Validation 相比 Final Validation 是否有早期识别增益?
- **现状(EXP-001 截断模式)**: C predR=0.554 < A 0.614, 未超过基线。
- **下一步**: 需要更直接的早期识别测量与更强的结构信号。

### RQ-4 [NOT SUPPORTED(测量待重设计)] 结构一致性是否比纯语义相似度更能恢复事件结构?
- **现状(EXP-001)**: 多信号图纯度与纯语义图纯度差异 ≤ 0.013, 无显著性;
  但 top-10 建图被语义预筛, 来源信号信息量弱 → 测量未检验假设。
- **下一步**: 聚类级纯度评测 + 更强结构信号(因果/传播/上下文)。

## Phase 2: Adaptive Search Strategy

### RQ-5 [UNVALIDATED] 系统能否学习 P(SearchStrategy | Query, Context, History)?
- 从"学 Answer"走向"学 How to Search"。
- 需要先有稳定的检索效果度量, 再谈策略学习; 当前阶段不实现。

### RQ-6 [UNVALIDATED] 搜索策略选择本身是否可度量、可归因?
- 例如: 何时该用 Anchor 策略, 何时该用扁平策略?

## Phase 3: Personal Memory

### RQ-7 [UNVALIDATED] 分层记忆(L1-L4)能否在不引入回声室的前提下个性化搜索路径?
- 需要定义并度量"回声室程度"。

### RQ-8 [UNVALIDATED] 推断型记忆(思维策略/元认知)需要多少行为证据才可信?
- 约束: 不能把模型推断包装成用户事实。

## Phase 4: Multi-Agent Orchestration

### RQ-9 [UNVALIDATED] Capability Interface 能否做到模型可插拔(不写死厂商)?
- 验收: 同一 Agent 逻辑在切换 Provider 后行为一致。

## Phase 5: World Model / Physical Interface

### RQ-10 [UNVALIDATED] 统一关系空间能否承载"人/事件/时间/地点/因果"而不退化?
### RQ-11 [UNVALIDATED] Cognitive Core → Capability API → Physical Action 闭环的延迟/可靠性边界?

---

## 研究纪律

1. 任何 RQ 的状态变更必须指向 research/experiments/ 中的一条记录。
2. 未验证的想法永远标注 [H] / UNVALIDATED, 不得包装为已验证结论。
3. 实验无法复现的结论视为不存在。
