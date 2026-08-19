# BM-001: 合成事件重建 Benchmark

- **状态**: 规格已注册 (2026-08-19); 首轮运行见 results/ 与 EXP-001。
- **关联假设**: H-001, H-002, H-003
- **关联问题**: RQ-1, RQ-2, RQ-3, RQ-4

## 1. 目的

在**合成事件碎片信息空间**上, 公平比较三种检索策略:

| 策略 | 说明 |
|---|---|
| A: Traditional | 全库扁平 top-k(基线) |
| B: Anchor-based | 锚点 + 局部扩张 |
| C: Dynamic Multi-Net | 多网 + 渐进验证 + 早停 |

回答: Dynamic Net 是否真的比传统检索更有效(以实验为准, 不以直觉为准)。

## 2. 数据集(合成, 可复现)

生成器: `src/cognitive_os/datasets/synthetic_events.py`

关键设计(对应"苹果问题"):
- 每个事件有一个潜在主题向量; **事件之间共享潜在主题** → 语义相似但
  属于不同事件的点对存在(歧义);
- 碎片 = 事件主题 + 噪声 → 同事件碎片语义上更近, 但不平凡可分;
- 事件在时间窗内展开(碎片带时间戳)→ 支持"信息未完整"实验;
- 碎片来自不同来源, 来源有可靠性权重 → 锚点证据超出语义。

默认参数(configs/benchmark.small.json):
`n_events=12, fragments_per_event=8, embed_dim=24, n_topics=5,
topics_per_event=4, within_event_noise=0.5, time_horizon=100,
event_span=20, source_count=4, index_top_m=6, seed=20260819`

> 2026-08-19 修正(D-2): 原声明 `n_topics=8, topics_per_event=3,
> within_event_noise=0.25` 与 `configs/benchmark.small.json` 实际值漂移。
> 配置为 EXP-001/EXP-002/EXP-003 实际运行基准(§7.1 歧义扫描亦为
> n_topics=5), 以配置为准修正本文档; 由 `scripts/check_specs_consistency.py`
> 在 CI 中持续校验, 防止再次漂移。

## 3. 协议(预注册, 防止事后改口径)

1. 用固定 seed 生成语料与邻居索引;
2. 每事件采样 1 个种子碎片作为查询(随机, 独立 seed);
3. 三个策略使用**相同的查询集合、相同的 k**, 不针对测试集调参;
4. 每个策略记录: 排序结果 + `similarity_calls` / `index_lookups` /
   `iterations` / `latency_ms`;
5. 指标按查询平均; 原始数据全部写入 results/ 下 JSON;
6. 主模式: 全语料(信息完整); 次级模式 `--truncate <frac>`:
   查询时刻 = 事件开始 + frac × 事件跨度, 只暴露已观测碎片,
   度量 predictive recall(未观测同事件碎片被排进 top-k 的比例)。

## 4. 指标

### Retrieval
- Precision@k, Recall@k, F1@k, NDCG@k, MRR

### Efficiency
- similarity_calls(计算/API 成本代理), index_lookups, iterations, latency_ms

### Reconstruction(Evidence Graph 分析)
- 对 top-k 候选建图(语义+时间+来源多样性约束)
- 种子所在连通成分的 cluster purity、事件重建 P/R/F1
- 对比: 纯语义建图 vs 多信号建图的纯度(H-003)

### Reasoning(本 Benchmark 不涉及; 留待真实信息空间阶段)

## 5. 判定标准(对应各假设)

- H-001: B 的 similarity_calls < 0.5 × A, 且 Recall@k 损失 ≤ 10pp。
- H-002: C 的 F1@k ≥ A, 且存在早停触发的查询; truncate 模式下
  predictive recall@k 高于 A。
- H-003: 多信号建图纯度 > 纯语义建图纯度。

## 6. 局限(诚实记录)

- 合成数据具有已知结构, 结果**不能外推**到真实信息空间;
- 嵌入是随机向量, 非真实 embedding;
- 来源可靠性是生成时设定, 真实世界需估计该信号;
- **索引不对称**: A 策略是无索引的穷举扫描(Recall 上限参照);
  B/C 使用预构建的语义邻居索引(标准 IR 实践)。因此效率对比衡量的是
  "锚点+扩张 vs 穷举", 索引构建成本不计入查询时成本(单独标注);
- 预测性指标(predictive recall)使用全索引重跑, 衡量的是算法在
  完整空间结构下的排序行为, 是"提前识别"的受控代理指标, 非真实时间线;
- 本 Benchmark 只测量检索与结构重建, 不测量推理/引用质量。

## 7. EXP-002 扩展(2026-08-19 追加, 预注册)

### 7.1 歧义档位扫描(检验 H-001 召回损失曲线)

- 语料: 12 事件 × 8 碎片, embed_dim=24, n_topics=5, seed=20260819;
- 两轴: topics_per_event ∈ {2, 4, 5} × within_event_noise ∈ {0.15, 0.3, 0.5};
- 策略配置**固定**(medium 档模板), 不针对档位调参;
- 每档 12 查询(每事件 1 种子, query_seed=1), k=10;
- 判定: H-001 效率 = B sim_calls < 0.5 × A; 质量 = Recall 损失 ≤ 10pp。

### 7.2 共识聚合诊断(检验 C 策略的证据合并方式)

- ValidatorConfig.aggregation ∈ {max, mean}; 两者在相同查询/预算下对比
  F1 / MRR / sim_calls / 早停率; 默认 max(最强网主导), mean = 平均发言。

### 7.3 H-003 测量重设计(结构信号 vs 语义相似度)

- 语料扩展: `causal_chains`(事件组织成 K 条链, 链内相邻事件碎片互相
  提及, meta.mentions)——与语义独立的真实引用结构(默认 0 关闭);
- 建图扩展: `EvidenceGraph.build(causal_edges=True)` 将引用作为硬边
  (权重 1.0, 不依赖语义阈值);
- 指标: mean_component_purity(聚类级事件纯度) / mean_chain_purity /
  chain_connectivity(链连通率, 辅助);
- 判定(主阈值 semantic_threshold=0.85, 全量层): +causal vs 纯语义,
  Δchain_purity ≥ +0.10 且 Δevent_purity ≥ −0.10 → PASS;
- 由于纯度口径可能不适用于非排他的链结构, 链连通率作为辅助证据,
  结论表述必须区分"事件聚类"与"链恢复"两个目标。
