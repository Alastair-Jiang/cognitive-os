# Research Questions — 研究问题清单

> 每条研究问题都带状态: `UNVALIDATED`(未验证, 即 Hypothesis) /
> `PARTIAL`(部分证据) / `VALIDATED`(已有本仓库实验支持) /
> `REFUTED`(被实验否定)。
> 状态只能由 research/ 下的实验记录更新, 不允许凭直觉修改。

## Phase 1: Dynamic Retrieval(当前阶段)

> 状态更新(2026-08-19, 依据 EXP-001 + EXP-002): 高歧义档位首轮实验 +
> 歧义档位扫描 + 共识诊断 + H-003 测量重设计均已完成。**扁平语义基线 A
> 在质量指标上是基准**(全部扫描档位)。

### RQ-1 [PARTIAL] Dynamic Net 是否真的比传统检索更有效?
- **现状(EXP-001 + EXP-002)**: 高歧义档位上 C F1@k=0.490 < A 0.637,
  成本 14×; 共识聚合诊断(mean vs max)无实质改善 → 未证明更有效。
  ⚠️ EXP-002 附带观察 → **EXP-003 已复核**(2026-08-19, SUPPORTED, 仅格点级):
  overlap-mid/noise-mid 档位 5 seed × 12 查询下 C F1@k − A = +0.081
  (p=0.0001, 95% CI [+0.044,+0.115], d_z=+0.58); 边界: 成本 ~3.7×,
  仅单格点成立, 不外推全网格(详见 EXP-003 与 H-002 状态注记)。
- **关联实验**: EXP-001, EXP-002, EXP-003
- **下一步**: Phase 2 网配置互补性; EXP-004 自适应策略选择(H-005, 预注册未运行)。

### RQ-2 [REFUTED(质量组件)] Anchor 机制能否在不显著损失 P/R 的情况下降低复杂度?
- **现状(EXP-001 + EXP-002 扫描)**: 效率组件稳健成立(B sim_calls 为 A 的
  19%-24%, 与歧义度无关); 质量组件在全部 10 个档位失败(召回损失
  26.2-56.0pp), 且损失与歧义度无单调关系——“歧义低→收敛”预期被否定。
- **下一步**: Phase 2 anchor 配置敏感性扫描(复杂度-质量权衡曲线)。

### RQ-3 [NOT SUPPORTED] Progressive Validation 相比 Final Validation 是否有早期识别增益?
- **现状(EXP-001 截断模式)**: C predR=0.554 < A 0.614, 未超过基线。
- **下一步**: 将结构信号(引用边)引入检索扩张后的早期识别测量。

### RQ-4 [PARTIAL(目标依赖)] 结构一致性是否比纯语义相似度更能恢复信息结构?
- **现状(EXP-002 重设计)**: 因果链语料上, 引用结构边的链连通率 0.940 vs
  纯语义 0.398——**链恢复口径支持**; 但纯度口径 FAIL(引用硬桥接稀释
  排他性纯度)。结论: 指标选取决定结论, 目标需明确化(事件聚类 vs 链恢复)。
- **下一步**: 引用边参与检索的实验 + H-003 目标拆分(详见 H-003)。

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
