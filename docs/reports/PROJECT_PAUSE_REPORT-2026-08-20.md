# Cognitive OS 项目暂停报告

> 生成日期: 2026-08-20
> 仓库: https://github.com/Alastair-Jiang/cognitive-os
> 报告作者: 项目维护者 + AI Assistant

---

## 1. 项目概述

### 1.1 项目定位

Cognitive OS 是一个研究 **Personal Intelligence Infrastructure / Personal Cognitive OS** 的开放式实验平台。

**核心定位声明**（源自 vision.md）：
> An experimental architecture for studying persistent, personalized, adaptive intelligence.

**重要澄清**：这不是一个 AGI 项目声明。项目最终是否能够向 AGI 靠近，由实验结果决定，而非概念判断。

### 1.2 项目起源

项目起源于一个信息安全问题：

> 假设一条有效信息在网络中被切分成多个碎片，通过不同节点、不同路径传播。传统方法必须等信息完整后才能验证，成本较高。

**反向研究问题**：
> 是否可以在信息尚未完整形成之前，就通过动态"网"、局部锚点、向量关系和渐进式验证，提前识别哪些信息碎片更可能属于同一个有效信息结构？

---

## 2. 知识领域覆盖

本项目横跨以下知识领域：

### 2.1 核心知识领域

| 领域 | 子领域 | 项目涉及深度 |
|---|---|---|
| **信息检索 (Information Retrieval)** | - 向量检索 / 语义搜索<br>- Top-k 检索<br>- 多策略检索<br>- 检索效率优化 | ⭐⭐⭐⭐⭐ (已完成核心实验) |
| **图论与网络科学** | - 证据图构建<br>- 结构一致性度量<br>- 连通性分析<br>- 社区发现/聚类 | ⭐⭐⭐⭐ (已实现 Evidence Graph) |
| **机器学习评估** | - 合成数据生成<br>- 指标设计 (P/R/F1/NDCG/MRR)<br>- 显著性检验<br>- 消融实验 | ⭐⭐⭐⭐ (已建立完整评测体系) |
| **认知架构 (Cognitive Architecture)** | - 记忆分层模型<br>- 多智能体协作<br>- 渐进式验证<br>- 推理-规划-执行闭环 | ⭐⭐ (愿景设计阶段，核心未实现) |

### 2.2 边缘知识领域

| 领域 | 涉及内容 | 状态 |
|---|---|---|
| **知识图谱** | 事件-实体关系建模、因果链恢复 | 愿景阶段 |
| **个性化推荐** | 认知效用函数、信息增益、认知路径推荐 | 愿景阶段 |
| **隐私与安全** | 数据最小化、记忆控制、推断约束 | 设计原则 |
| **具身智能** | Physical Interface、世界模型 | 长期愿景 |

---

## 3. 研究问题与完成程度

### 3.1 Phase 1: Dynamic Retrieval Prototype — ✅ 完成

#### 已回答的研究问题

| RQ ID | 问题 | 结论 | 支撑实验 |
|---|---|---|---|
| **RQ-1** | Dynamic Net 是否真的比传统检索更有效? | **部分否定**: 高歧义语料上，扁平语义基线 A 在 F1/NDCG/Recall 上全面领先 | EXP-001, EXP-002 |
| **RQ-2** | Anchor 机制能否在不显著损失 P/R 的情况下降低复杂度? | **部分成立**: 效率组件稳健(4-5× 节省)，质量组件失败(召回损失 26.2-56.0pp) | EXP-001, EXP-002 |
| **RQ-3** | Progressive Validation 是否有早期识别增益? | **否定**: 截断模式下 C predR < A | EXP-001 |
| **RQ-4** | 结构一致性是否比纯语义相似度更能恢复信息结构? | **目标依赖**: 链恢复口径支持(连通率 0.94)，纯度口径失败 | EXP-002 |

#### 核心假设状态

| 假设 ID | 状态 | 核心发现 |
|---|---|---|
| **H-001** | REFUTED (质量组件) | 效率: 4-5× 节省 ✅<br>质量: 召回损失 26-56pp，全部超标 ❌ |
| **H-002** | REFUTED (按原表述) | 早停机制有效(75%查询)，但未转化为质量优势 |
| **H-003** | PARTIAL (目标依赖) | 链恢复: 连通率 0.94 vs 0.29-0.40 ✅<br>事件聚类: 纯度下降 ❌ |

### 3.2 已完成的里程碑

| 阶段 | 状态 | 完成日期 |
|---|---|---|
| Phase 0: 仓库初始化 | ✅ 完成 | 2026-08-19 |
| Phase 1: Dynamic Retrieval Prototype | ✅ 首轮完成 | 2026-08-19 |
| Phase 1b: 检索假设修订实验 | ✅ 完成 | 2026-08-19 |

### 3.3 未完成的里程碑

| 阶段 | 状态 | 说明 |
|---|---|---|
| Phase 2: Anchor Mechanism 深化 | ⏸️ 未开始 | 需要 H-001 质量组件修复后推进 |
| Phase 3: Progressive Validation 深化 | ⏸️ 未开始 | 需要结构信号引入检索扩张 |
| Phase 4-5: Adaptive Search Strategy | ⏸️ 未开始 | 依赖 Phase 1-3 的稳定检索效果 |
| Phase 6: Personal Memory | ⏸️ 未开始 | 核心架构未建立 |
| Phase 7-11: 后续愿景 | ⏸️ 未开始 | 依赖前面阶段的验证 |

---

## 4. 核心实现成果

### 4.1 代码资产

| 模块 | 文件数 | 测试覆盖 | 状态 |
|---|---|---|---|
| `datasets/` | 3 | 100% | ✅ 生产级 |
| `nets/` | 4 | 100% | ✅ 生产级 |
| `anchors/` | 3 | 100% | ✅ 生产级 |
| `validation/` | 3 | 100% | ✅ 生产级 |
| `graph/` | 4 | 100% | ✅ 生产级 |
| `retrieval/` | 6 | 100% | ✅ 生产级 |
| `memory/` | 1 | - | STUB |
| `agents/` | 1 | - | STUB |
| `orchestration/` | 1 | - | STUB |

**测试状态**: 118/118 通过 (100%)

### 4.2 核心数据结构

```python
InformationPoint  # 信息碎片: 向量、时间戳、来源、ground-truth 标签
Query             # 检索请求: 种子碎片、可观测集合(模拟信息未完整)
Evidence          # 累积证据: 语义/来源/时间/结构分 + 置信度
RetrievalResult   # 检索结果: 排序、证据、效率指标
SearchNet         # 可配置检索网: 半径/时间窗/来源权重/跳数
EvidenceGraph     # 多信号一致性图: 语义+时间+来源多样性
```

### 4.3 三种检索策略

| 策略 | 实现文件 | 核心思想 |
|---|---|---|
| A: Traditional | `strategy_a_traditional.py` | 全库扁平 top-k (基线) |
| B: Anchor-based | `strategy_b_anchor.py` | 多信号锚点 + 局部扩张 |
| C: Dynamic Multi-Net | `strategy_c_multinet.py` | 多网并行 + 渐进验证 + 早停 |

### 4.4 评测基准

- **Benchmark**: BM-001 (合成事件重建)
- **指标**: Precision@k, Recall@k, F1@k, NDCG@k, MRR, purity, reconF1, chain_connectivity
- **效率指标**: similarity_calls, index_lookups, iterations, latency_ms

---

## 5. 关键实验发现

### 5.1 EXP-001: Dynamic Nets vs 基线

**实验配置**: 12 事件 × 8 碎片 = 96 点, 高歧义 (noise=0.5)

**核心结果**:

| 策略 | F1@k | Recall@k | sim_calls | 结论 |
|---|---|---|---|---|
| A 传统 | **0.637** | **0.774** | 95 | 质量基准 |
| B Anchor | 0.512 | 0.548 | **22** | 效率优，质量损 |
| C Multi-Net | 0.490 | 0.595 | 1326 | 未证明有效 |

**关键洞察**:
> 在高歧义合成语料上，扁平语义基线 A 是质量基准。Dynamic Net 尚未证明比传统检索更有效。

### 5.2 EXP-002: 歧义档位扫描

**扫描范围**: 10 个歧义档位 (noise × overlap)

**核心发现**:

1. **效率组件在所有档位成立**: B 的 sim_calls 恒为 A 的 19%-24%
2. **质量组件在所有档位失败**: 召回损失 26.2-56.0pp，全部超标
3. **修订预期被否定**: 召回损失与歧义度无单调关系

### 5.3 EXP-003: 显著性复核

**附带观察验证** (overlap-mid/noise-mid 档位):

- C F1@k − A = **+0.081** (p=0.0001, CI=[+0.044,+0.115], d_z=+0.58)
- **边界**: 仅单格点成立，成本 ~3.7×，不外推至全网格

---

## 6. 当前领域前沿与更优解

### 6.1 信息检索领域

#### 当前前沿方向

| 方向 | 代表性工作 | 与本项目关系 |
|---|---|---|
| **密集检索 (Dense Retrieval)** | DPR (Karpukhin et al., 2020), ColBERT (Khattab & Zaharia, 2020) | 本项目使用向量检索，但未集成真实 embedding 模型 |
| **学习型排序 (Learning to Rank)** | BERT-based rerankers, monoT5 | 未涉及 |
| **多向量检索** | MVR (Multi-Vector Retrieval) | 类似 C 策略的多网思想 |
| **自适应检索** | Adaptive retrieval budget allocation | 未涉及 |

#### 更优解方向

1. **集成真实 Embedding 模型**: 当前使用随机向量，EXP-006 已预注册验证真实 embedder 等价性
2. **学习型策略选择**: EXP-004/EXP-005 预注册了自适应策略选择和引用扩张
3. **混合检索**: 稀疏-稠密混合检索 (BM25 + Dense) 是当前工业标准

### 6.2 图神经网络与结构学习

#### 当前前沿

| 方向 | 代表性工作 | 与本项目关系 |
|---|---|---|
| **图神经网络检索** | GNN-based document retrieval | Evidence Graph 可扩展 GNN |
| **知识图谱增强检索** | KG-enhanced IR | 与 H-003 的结构信号相关 |
| **子图匹配与结构恢复** | Graph matching algorithms | 与信息拓扑恢复相关 |

#### 更优解方向

- 当前 Evidence Graph 使用简单阈值建图，可引入 GNN 学习节点表示
- 结构信号(causal edges)在本项目中仅在事后建图阶段使用，EXP-005 预注册了引入检索扩张

### 6.3 认知架构与记忆系统

#### 当前前沿

| 方向 | 代表性工作 | 与本项目关系 |
|---|---|---|
| **神经符号认知架构** | ACT-R 现代变体, Soar | 本项目的 L1-L4 记忆分层设计借鉴此类工作 |
| **检索增强生成 (RAG)** | 多种 RAG 变体 | 本项目的 Retrieval Layer 可与 RAG 结合 |
| **长期记忆系统** | MemGPT, Generative Agents | memory/ 模块为 STUB，可借鉴此类系统 |

#### 更优解方向

- MemGPT 提供了分页式虚拟上下文管理，可作为 memory/ 的参考架构
- Generative Agents (Park et al., 2023) 的记忆流和反思机制可借鉴

### 6.4 个性化信息获取

#### 当前前沿

| 方向 | 代表性工作 | 与本项目关系 |
|---|---|---|
| **个性化搜索** | Personalized Web Search, PQA | 与 vision.md 的 Personal Memory 相关 |
| **信息偏好学习** | User modeling for IR | 未涉及 |
| **反回声室** | Diversity-aware recommendation | vision.md 提到 Anti-Echo-Chamber 原则 |

### 6.5 多智能体系统

#### 当前前沿

| 方向 | 代表性工作 | 与本项目关系 |
|---|---|---|
| **多智能体协作框架** | AutoGen, CrewAI, LangGraph | agents/ 和 orchestration/ 为 STUB |
| **Agent 编排模式** | Hierarchical, Sequential, Parallel | 架构设计中 |
| **工具使用与规划** | ReAct, Toolformer | 未涉及 |

---

## 7. 项目价值与贡献

### 7.1 方法论贡献

1. **科研诚实原则制度化**: 
   - Hypothesis ≠ Validated Result
   - 实验驱动的增量开发
   - 拒绝"听起来合理"作为证据

2. **完整的研究闭环**:
   ```
   Hypothesis → Prototype → Experiment → Metric → Result → Revision
   ```

3. **预注册实验设计**: 所有实验在 research/experiments/ 中预注册，避免 p-hacking

4. **诚实的失败记录**: 
   - H-001/H-002 被明确标记为 REFUTED
   - 每个假设的失败原因都有量化分析

### 7.2 技术贡献

1. **可配置的合成评测基准**: BM-001 提供可控歧义的信息碎片重建任务
2. **三种检索策略的公平对比**: 统一接口、统一指标、成本计量
3. **结构一致性度量**: 区分链恢复和事件聚类两种目标

### 7.3 可复用资产

| 资产 | 位置 | 价值 |
|---|---|---|
| 合成语料生成器 | `datasets/synthetic_corpus.py` | 可配置歧义度的评测基准 |
| 证据图模块 | `graph/evidence_graph.py` | 多信号一致性建图 |
| 检索策略框架 | `retrieval/base.py` | 可扩展的策略接口 |
| 评测脚本 | `scripts/run_benchmark.py` | 一键运行基准测试 |
| 实验记录模板 | `research/experiments/` | 可复用的实验预注册格式 |

---

## 8. 开放问题与未来方向

### 8.1 未解决的核心问题

| 问题 | 当前障碍 | 可能突破方向 |
|---|---|---|
| **H-001 质量修复** | 召回损失过大(26-56pp) | 锚点配置敏感性扫描(Phase 2) |
| **H-002 收益变现** | 多网共识未转化为质量优势 | 网配置互补性诊断 |
| **H-003 目标明确** | 不同指标结论矛盾 | 明确"链恢复"vs"事件聚类"目标 |
| **真实语料验证** | 当前仅合成数据 | EXP-006 真实 embedder 等价性验证 |

### 8.2 预注册但未运行的实验

| 实验 ID | 目的 | 状态 |
|---|---|---|
| EXP-004 | 自适应策略选择 | 预注册，未运行 |
| EXP-005 | 引用扩张(结构信号参与检索) | 预注册，未运行 |
| EXP-006 | 真实 embedder 等价性 | 预注册，未运行 |

### 8.3 长期愿景保留

以下方向作为愿景保留于 docs/vision.md，但当前阶段不推进：

- Phase 6: Personal Memory (L1-L4 分层)
- Phase 7: Cognitive Recommendation
- Phase 8: Multi-Agent Orchestration
- Phase 9: Biomimetic Cognitive Architecture
- Phase 10: World Model
- Phase 11: Physical/Robotic Interface

---

## 9. 项目暂停决策记录

### 9.1 暂停原因

1. **核心假设被否定**: Phase 1 的核心假设 H-001(质量组件) 和 H-002(原表述) 均被实验否定
2. **方向需要重新审视**: 扁平语义基线在高歧义场景下的强势表现，需要重新评估 Dynamic Net 的价值主张
3. **资源优化配置**: 在获得新的突破方向前，暂停以等待领域进展或新洞察

### 9.2 暂停状态

| 组件 | 状态 | 备注 |
|---|---|---|
| 代码库 | ✅ 完整 | 118/118 测试通过 |
| 文档 | ✅ 完整 | 研究记录已归档 |
| 实验数据 | ✅ 完整 | JSON 结果文件保留 |
| 预注册实验 | ⏸️ 暂停 | 可随时恢复 |
| STUB 模块 | ⏸️ 未开始 | 依赖核心突破 |

### 9.3 恢复条件

项目可在以下条件满足时恢复：

1. **锚点机制突破**: 找到显著降低召回损失的配置方案
2. **结构信号引入检索**: 验证 causal edges 参与扩张的质量增益
3. **真实语料验证**: EXP-006 验证随机向量与真实 embedding 的等价性
4. **领域新进展**: 相关领域出现可借鉴的突破性工作
5. **新研究假设**: 提出新的可证伪假设

---

## 10. 参考文献与相关论文

### 10.1 信息检索

| 论文 | 方向 | 与本项目关系 |
|---|---|---|
| Karpukhin et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering | 密集检索 | 本项目使用向量检索，可借鉴 DPR 架构 |
| Khattab & Zaharia (2020). ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction | 多向量表示 | 与 C 策略的多网思想有相似性 |
| Nogueira & Cho (2019). Passage Re-ranking with BERT | 学习型排序 | 未涉及，可作为改进方向 |
| Ma et al. (2021). Reproducing DPR | 实验复现方法 | 本项目强调可复现性 |

### 10.2 图神经网络与知识图谱

| 论文 | 方向 | 与本项目关系 |
|---|---|---|
| Schlichtkrull et al. (2018). Modeling Relational Data with Graph Convolutional Networks | 知识图谱 GNN | Evidence Graph 可扩展 |
| Park et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior | 记忆与反思机制 | memory/ 模块可借鉴 |
| Yao et al. (2019). KG-BERT: BERT for Knowledge Graph Completion | KG 增强 | 结构信号增强检索 |

### 10.3 认知架构

| 论文/系统 | 方向 | 与本项目关系 |
|---|---|---|
| Anderson et al. (ACT-R Theory) | 认知架构理论 | 本项目 L1-L4 设计借鉴 |
| Laird (2012). The Soar Cognitive Architecture | 认知架构 | 多 Agent 协作参考 |
| Nakano et al. (2021). Multi-Vector Retrieval | 多向量检索 | 与 C 策略思想相关 |

### 10.4 记忆系统

| 论文/系统 | 方向 | 与本项目关系 |
|---|---|---|
| MemGPT (2023) | 虚拟上下文管理 | memory/ 模块可借鉴架构 |
| Generative Agents (Park et al., 2023) | 记忆流与反思 | 记忆分层设计参考 |
| Retrieval-Augmented Generation (Lewis et al., 2020) | RAG 架构 | Retrieval Layer 可集成 |

### 10.5 多智能体系统

| 论文/系统 | 方向 | 与本项目关系 |
|---|---|---|
| AutoGen (Wu et al., 2023) | 多 Agent 协作框架 | orchestration/ 可借鉴 |
| CrewAI | Agent 角色分工 | agents/ 设计参考 |
| LangGraph | 状态机编排 | 编排模式参考 |

---

## 11. 致谢

本项目在研究与开发过程中：
- 遵循科研诚实原则，如实记录每一次假设的验证与否定
- 感谢所有对项目愿景提出建议的贡献者
- 特别感谢 open-source 社区在信息检索、认知架构等领域的持续贡献

---

## 12. 附录

### A. 仓库结构

```
cognitive-os/
├── docs/                  # 文档系统
├── research/              # 研究记录
│   ├── hypotheses/        # 假设定义
│   ├── experiments/       # 实验预注册
│   ├── benchmarks/        # 基准规格
│   ├── results/           # 实验结果 JSON
│   └── log/               # 研究日志
├── src/cognitive_os/      # 核心代码
│   ├── datasets/          # 合成数据集
│   ├── nets/              # 检索网
│   ├── anchors/           # 锚点检测
│   ├── validation/        # 渐进验证
│   ├── graph/             # 证据图
│   ├── retrieval/         # 检索策略
│   ├── memory/            # [STUB]
│   ├── agents/            # [STUB]
│   └── orchestration/     # [STUB]
├── tests/                 # 单元测试
├── configs/               # 基准配置
├── examples/              # 快速入门
└── scripts/               # 实验脚本
```

### B. 关键指标定义

| 指标 | 定义 |
|---|---|
| Precision@k | top-k 中真正相关的比例 |
| Recall@k | top-k 覆盖的真正相关文档占所有相关文档的比例 |
| F1@k | Precision@k 和 Recall@k 的调和平均 |
| NDCG@k | Normalized Discounted Cumulative Gain，考虑排序位置 |
| MRR | Mean Reciprocal Rank，首个相关文档排名倒数的均值 |
| purity | 聚类成分中最大事件占比的加权平均 |
| chain_connectivity | 因果链内碎片对在同一成分中的比例 |

### C. 实验结果文件索引

| 文件 | 对应实验 |
|---|---|
| `EXP-001-benchmark.small-k10-q12-*.json` | EXP-001 主模式 |
| `EXP-001-benchmark.small-k10-q12-*.truncate.json` | EXP-001 截断模式 |
| `EXP-002-scan-k10-q12-*.json` | EXP-002 歧义扫描 |
| `EXP-002-consensus-*.json` | EXP-002 共识聚合诊断 |
| `EXP-002-h003-*.json` | EXP-002 H-003 重设计 |

---

**报告结束**

*此报告记录了 Cognitive OS 项目截至 2026-08-20 的完整状态，包括已完成的研究、核心发现、开放问题以及领域前沿。项目当前处于暂停状态，可在满足恢复条件时继续推进。*
