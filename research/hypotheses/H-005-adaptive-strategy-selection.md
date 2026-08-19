# H-005: 自适应策略选择（Adaptive Strategy Selection）优于固定策略的质量-成本权衡

- **状态**: UNVALIDATED（2026-08-19 注册，依据 Master Prompt v2.0 §8-§14 与架构审计 REPORT-2026-08-19-architecture-audit.md §9）
- **关联问题**: RQ-5（P(SearchStrategy | Query, Context, History) 可否学习）、RQ-6（策略选择是否可度量、可归因）
- **关联实验**: EXP-004（预注册见 `research/experiments/EXP-004-adaptive-strategy-selection.md`）
- **前置证据**: EXP-002 十格扫描 + EXP-003 格点级复核表明"最优策略依赖信息 regime"
  （9/10 格 A ≥ C，1 格 C 显著 &gt; A 且代价 3.7×）——regime 异质性存在**初步迹象**，
  但异质性的**幅度、可预测性、可利用性**均未量化。

## 假设

存在可廉价测量的查询/证据状态特征 s（如种子邻域密度、top-邻相似度 margin、
局部歧义统计），使得一个基于 s 的策略选择器 π(a|s)（a ∈ {A, B, C}），
在效用函数

```text
U = F1@k − λ · (similarity_calls / N)
```

（λ 为配置参数；延迟第一版只记录不优化）下，**显著优于任何固定策略**
（恒选 A / 恒选 B / 恒选 C），且选择器自身开销计入 U。

## 理由（为什么可能成立）

- 已有证据表明最优策略并非全局恒定：B 的 4–5× 效率节省在全部档位成立，
  而 A 的质量优势在 9/10 格成立、C 在 overlap-mid/noise-mid 格点占优
  ——存在"按状态切换"的理论空间；
- 三策略代价结构差异巨大（EXP-001: sim_calls 22 / 95 / 1326），
  效用函数对成本敏感时"何时用便宜策略"本身就有价值。

## 可证伪预测（在 BM-001 合成语料 + EXP-002 十格网格 + medium 档上）

1. **Headroom 存在**：逐查询 Oracle（事后最优）的 U 显著高于最优固定策略
   （EXP-004a；若 headroom ≈ 0 则假设在本 regime 无空间，廉价证伪）；
2. **状态可测**：廉价特征 s 对"逐查询最优策略"的预测准确率显著高于先验多数类；
3. **控制器有效**：基于 s 的简单规则控制器（v1 起步：单特征）的 U 显著高于
   最优固定策略（统计闸门：配对随机化检验 p&lt;0.05 + bootstrap CI 不含 0 +
   跨 seed 一致 ≥80% + 最小效应 ≥0.01，复用 `src/cognitive_os/stats.py`）。

## 证伪条件

- EXP-004a 显示 headroom 低于预注册阈值（异质性不足以支撑自适应）→ REFUTED
  （**该负结果本身有价值**：说明当前语料规模/策略差异下自适应为时过早）；
- 或 headroom 存在但廉价特征不可测（EXP-004b 预测力不显著）→ 假设按
  "状态可测性"子句证伪，修订方向为更富特征或更强的状态表示；
- 或控制器统计闸门未过（EXP-004c）→ 按原表述证伪，仅记录 headrom 观察。

## 备注

- **Incremental Feature Introduction**（Master Prompt §10）：每引入一个状态变量
  必须单独回答"是否改善策略选择"，禁止一次性堆特征。
- 本假设**不含**跨查询学习（Strategy Memory 是后续独立假设）、
  **不含** LLM 参与、**不含**真实 embedding——边界与宪法 §2 一致。
- 效用参数 λ 全部入 config（Master Prompt §14：禁止硬编码）。
- 编号说明：H-004 按 `engineering_plan.md` E2 Gate 预留给 H-003 目标拆分
  （事件聚类 vs 链恢复），本假设顺延为 H-005（见审计报告 §8.1 裁决）。
