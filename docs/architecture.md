# Architecture — 架构文档

> 状态: **演化中**。本文描述当前实现的结构与未来扩展的接口意图。
> 标记 [IMPLEMENTED] 的模块有可运行代码; 标记 [STUB] 的模块只有占位
> (见 roadmap.md, 明确不做"看起来先进"的空实现)。

## 1. 分层总览

```text
┌────────────────────────────────────────────────────────────┐
│  Orchestration (STUB)     多 Agent 编排, 未来阶段            │
├────────────────────────────────────────────────────────────┤
│  Agents (STUB)            Research/Search/Coding/... Agent  │
├────────────────────────────────────────────────────────────┤
│  Memory (STUB)            L1-L4 分层记忆, 未来阶段           │
├────────────────────────────────────────────────────────────┤
│  Retrieval Layer [IMPLEMENTED]                              │
│   Strategy A/B/C + Evidence Graph + Metrics                 │
├────────────────────────────────────────────────────────────┤
│  Nets / Anchors / Validation [IMPLEMENTED]                  │
│   多网搜索、锚点检测、渐进式验证                            │
├────────────────────────────────────────────────────────────┤
│  Datasets [IMPLEMENTED]  合成信息空间(带 ground truth)       │
└────────────────────────────────────────────────────────────┘
```

## 2. 当前数据流(第一版原型)

```text
Query(种子碎片)
   ↓
Strategy 选择(传统 / Anchor-based / Multi-Net)
   ↓
候选信息收集(检索网 / 锚点扩张)
   ↓
渐进式验证(置信度更新, 无硬性提前淘汰)
   ↓
Evidence Graph(多信号一致性建图)
   ↓
Ranked Result + 结构化指标
```

## 3. 核心抽象 [IMPLEMENTED]

| 抽象 | 位置 | 职责 |
|---|---|---|
| `InformationPoint` | `types.py` | 信息空间中的一个碎片: 向量、时间戳、来源、来源可靠性、ground-truth 事件标签(仅用于评测) |
| `Query` | `types.py` | 一次检索请求: 种子碎片、可选的可观测集合(模拟信息未完整) |
| `Evidence` | `types.py` | 候选点的累积证据: 语义/来源/时间/结构分 + 跨网共识 + 置信度 |
| `RetrievalResult` | `types.py` | 检索结果: 排序、证据、迭代次数、相似度计算次数、延迟 |
| `SearchNet` | `nets/search_net.py` | 一个可配置的检索网(半径/时间窗/来源权重/跳数) |
| `detect_anchors` | `anchors/anchor_detector.py` | 多信号综合的锚点检测(语义+来源+时间+局部密度) |
| `ProgressiveValidator` | `validation/progressive.py` | 渐进式验证循环: 跨网共识 + 置信度 + 早停, **禁止硬性提前淘汰** |
| `EvidenceGraph` | `graph/evidence_graph.py` | 多信号一致性图: 语义+时间+来源多样性, 支持结构一致性度量 |
| `RetrievalStrategy` | `retrieval/base.py` | 检索策略接口(A/B/C 三策略实现) |

## 4. 三种检索策略

| 策略 | 文件 | 思想 | 评测角色 |
|---|---|---|---|
| A: Traditional | `retrieval/strategy_a_traditional.py` | 全库扁平 top-k(基线) | 基线, 回答"新方法是否真的更有效" |
| B: Anchor-based | `retrieval/strategy_b_anchor.py` | 先找少量高置信 Anchor, 围绕其扩张 | 检验"锚点降低复杂度而不损失 P/R" |
| C: Dynamic Multi-Net | `retrieval/strategy_c_multinet.py` | 多网并行 + 渐进验证 + 早停 | 检验"多网渐进验证改进效率/质量" |

**效率计量(诚实原则)**: 每个策略都记录 `similarity_calls`(相似度计算次数,
作为 API 调用/计算成本的代理)、`index_lookups`、`iterations`(轮数)、
`latency_ms`。索引构建成本在评测中单独标注, 不计入查询时成本。

## 5. 设计原则(未来阶段也必须遵守)

### 5.1 Capability Interface, 不是 Model Dependency

未来接入模型时:

```text
Model Provider → Capability Adapter → Agent → Orchestrator
```

核心架构只依赖能力接口, 不写死任何厂商(OpenAI / DeepSeek / Anthropic /
本地模型一律通过 Adapter 接入)。

### 5.2 权限分级(Agent 行为)

```text
Level 0  Answer only
Level 1  Search
Level 2  Modify digital files
Level 3  Call external services
Level 4  Physical-world action
```

权限越高, 确认和审计越严格。

### 5.3 隐私与记忆控制

- 最小化数据收集 (Privacy by design)。
- 用户可以 View / Edit / Delete / Export 自己的记忆。
- 明确数据归属和使用边界 (Data Ownership)。
- 模型推断 ≠ 用户事实 (Inference Control)。
- 高危领域 (医疗/金融/法律/保险/物理安全) 必须人工确认 + 证据要求 + 风险控制。

## 6. 模块现状一览

| 模块 | 状态 | 说明 |
|---|---|---|
| `datasets/` | [IMPLEMENTED] | 合成信息空间, 可配置事件数/主题重叠/噪声/时间结构 |
| `nets/` | [IMPLEMENTED] | 检索网(单网搜索原语) |
| `anchors/` | [IMPLEMENTED] | 锚点检测 |
| `validation/` | [IMPLEMENTED] | 渐进式验证 |
| `graph/` | [IMPLEMENTED] | 证据图 + 结构一致性度量 |
| `retrieval/` | [IMPLEMENTED] | 三策略 + 指标 |
| `memory/` | [STUB] | 未来阶段, 见 roadmap 阶段 6 |
| `agents/` | [STUB] | 未来阶段, 见 roadmap 阶段 8 |
| `orchestration/` | [STUB] | 未来阶段, 见 roadmap 阶段 8 |

## 7. 已知边界(诚实记录)

- 第一版只做**合成数据**上的检索实验; 合成数据具有已知结构,
  结果不能外推到真实信息空间。
- 嵌入表示是随机生成的向量, 未使用任何真实 embedding 模型。
- "来源可靠性"是生成时设定的标量, 真实世界中该信号本身就需要估计。
- 因果一致性、事件传播关系等结构信号尚未建模(见 research_questions.md RQ-4)。
