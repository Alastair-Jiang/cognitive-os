# EXP-004: 自适应检索策略选择（Adaptive Retrieval Strategy Selection）

- **状态**: **预注册（未运行）**——判定标准先于运行写下（宪法 §2；提交历史可证）
- **关联假设**: H-005（`research/hypotheses/H-005-adaptive-strategy-selection.md`）
- **关联问题**: RQ-5, RQ-6
- **Benchmark 规格**: BM-001 + EXP-002 十格网格 + medium 档
- **触发**: Master Prompt v2.0 §8-§14（架构转向：从"哪个策略更强"转向"何时用哪个策略"）；
  架构审计 `docs/reports/REPORT-2026-08-19-architecture-audit.md` §9
- **编号裁决**: 本实验占用 EXP-004（按 Master Prompt 直接指令）；
  `engineering_plan.md` E2 原预留的引用扩张实验顺延为 EXP-005（待文档同步，见审计 §8.1）

## 背景

EXP-001/002/003 的诚实结论拼图：

1. A 是质量基线（9/10 格 + medium）；
2. B 的效率组件全局成立（4-5× 节省）但质量组件全局失败（召回损失 26-56pp）；
3. C 仅在 overlap-mid/noise-mid 格点显著优于 A（EXP-003, d_z=+0.58），代价 3.7×。

即：**最优策略依赖信息 regime，且三策略代价结构差异巨大**。这自然引出
Master Prompt §8 的架构转向——不再问"哪个策略更强"，而问：

> 系统能否根据当前 Query State 和 Evidence State，自主选择最合适的检索策略，
> 在质量与成本之间获得优于任何固定策略的权衡？

EXP-004 按三段子实验递进（每段独立可证伪，前段失败则后段不启动）：

```text
EXP-004a  Oracle headroom（异质性/上界测量）——最廉价的证伪点
EXP-004b  状态可测性（廉价特征能否预测逐查询最优策略）
EXP-004c  控制器 v0/v1（能否捕获 headroom 的显著比例）
```

## 效用函数（预注册）

```text
U(query, strategy) = F1@k − λ · (similarity_calls / N)
```

- **主判定 λ = 0.02**；敏感性扫描 λ ∈ {0, 0.01, 0.02, 0.05, 0.1}（全部入 config，
  禁止硬编码，Master Prompt §14）；
- λ=0.02 的量纲依据：small 语料 A 的 sim_calls/N ≈ 1.0、B ≈ 0.23、C ≈ 14
  （EXP-001 实测），λ=0.02 下 B 的成本优势 ≈ +0.015U、C 的成本劣势 ≈ −0.28U，
  与实测 F1 差距（0.1-0.2）同量级——成本"足以被感知但不淹没质量"；
- 延迟 latency_ms 只记录不优化（进程内计时噪声大，Master Prompt §13 延迟项
  留待真实 API 成本场景）；
- **控制器/特征计算自身的 similarity_calls 计入 U**（诚实成本，闸门 G4）。

## 设置（预注册）

### EXP-004a — Oracle Headroom

- **语料宇宙**: EXP-002 十格网格（`run_exp002_scan.py` 的 OVERLAP × NOISE
  全组合，基结构 12 事件 × 8 碎片, n_topics=5）+ medium 档（30×10, n_topics=6,
  tpe=4, noise=0.45），共 11 个 corpus 配置；
- **语料 seed × 3**: {20260819, 7, 42}（EXP-003 前 3 个 seed，延续口径；
  结果处于判定边界时扩展到 5 个 {+131, 9999} 并如实记录扩展）；
- **查询**: 每格 12 个（query_seed=1），k=10；
- **策略**: A/B/C 全部三策略（模板冻结：import
  `run_exp002_scan.SCAN_STRATEGY_TEMPLATE` 与 `build_strategies`，不复制——D-5 教训）；
- **逐查询记录**: 每策略的 F1@k、similarity_calls、U（含每查询原始值，供配对检验）。

**定义**（逐查询效用 U_q(s)）：

| 量 | 定义 |
|---|---|
| 全局最优固定 U_gf | max_s mean_q[U_q(s)]（全 11 配置池化） |
| 格点最优固定 U_cf | 每格 max_s mean_q[U_q(s)]（知道 regime、不知道查询） |
| Oracle U_or | mean_q max_s U_q(s)（逐查询事后最优） |
| **Headroom-H0** | U_cf − U_gf（regime 级空间：按格选策略能赚多少） |
| **Headroom-H1** | U_or − U_cf（查询级空间：逐查询选择还能再赚多少） |

### EXP-004b — 状态可测性（仅当 004a 通过 G1 后启动）

预注册**三个**廉价查询侧特征（Incremental Feature Introduction，
Master Prompt §10：逐个加入、逐个检验）：

| 特征 | 计算 | 成本上限 |
|---|---|---|
| f1 neighbor_sim_max | 种子 top-m 邻居相似度最大值 | m 次索引读（相似度已在索引内，0 sim_calls） |
| f2 neighbor_sim_spread | top-m 邻居相似度标准差 | 同上 |
| f3 neighbor_coherence | 种子 top-m 邻居两两相似度均值 | ≤ C(m,2) 次相似度计算，计入 U |

（种子时间位置、来源权重作为候选特征列入附录，未经新预注册不入判定。）

- 检验方式：逐查询最优策略标签（来自 004a 数据，**标签冻结在主判定 λ = 0.02**：λ 敏感性扫描
  全部入 config 仅作稳健性报告，标签来源不得随 λ 更换——预注册更正
  2026-08-19，运行前补锁定，防跨 λ 标签漂移破坏 G2 可比性）~ 特征的单变量关联
  （每特征一个列联/秩检验，纯标准库实现）+ 简单规则的可达到准确率；
- **数据划分防泄漏**: seed {20260819, 7} 为训练半区，{42}（及边界扩展 seed）为
  检验半区——**训练半区的数据不得参与特征选择与阈值标定后的最终判定**。

### EXP-004c — 控制器 v0/v1（仅当 004b 通过 G2 后启动）

- **v0（对照）**: 恒选 A（同时也报告恒选最优固定策略作第二对照）；
- **v1**: 基于**单个**特征的单阈值规则（特征与阈值在训练半区标定）；
- 控制器包装为策略选择器（建议落位 strategy_selector.py（src/cognitive_os/retrieval/ 下，R4 交付、G1 通过后才创建），
  **实验模块，不进核心**——宪法 §2，需 H-005 过闸后才考虑晋升）；
- 逐查询配对：U_controller − U_best_fixed（best fixed 取 U_cf，即最强固定基线）。

## 判定标准（预注册，先于运行写下）

统计口径沿用 `src/cognitive_os/stats.py` 四闸门（EXP-003 先例）：
q1 配对随机化检验 p&lt;0.05（R=10000, rng_seed=777）；
q2 bootstrap 95% CI 不含 0（B=10000, rng_seed=888）；
q3 跨 seed 一致性 ≥80%；
q4 最小效应 |mean_diff| ≥ 0.01。

### G1（004a · headroom 存在性）

- **G1-通过**: 主 λ 下，池化 Headroom-H1 ≥ 0.03 **且** ≥3/11 格的格内
  Headroom-H1 ≥ 0.02 → 进入 004b；
- **G1-regime**: H1 不达但 Headroom-H0 ≥ 0.03 → 假设按"查询级"表述证伪，
  修订方向为 **regime 级分类器**（更弱但更实际的目标），H-005 如实改写；
- **G1-失败**: H0、H1 均不达 → **H-005 REFUTED（当前语料宇宙无自适应空间）**。
  依据 Master Prompt §37：这是合格且有价值的负结果——说明在当前合成语料规模与
  策略差异下，自适应选择为时过早，Phase 2 应回到策略本身（锚点权衡曲线/引用扩张）。

（0.03/0.02 阈值依据：EXP-001/002 中 A-vs-C 的典型 F1 差为 0.1-0.15，
取其 1/5-1/4，高于单 seed 12 查询的测量噪声 ~0.03 的水平且池化后可分辨。）

### G2（004b · 状态可测性）

- 至少一个单特征规则在**检验半区**达到：最优策略预测准确率 ≥50%
  （先验多数类基线 ≈ 恒选 A 的占比，需在结果中如实报告），
  且该特征与最优策略标签的关联检验 p&lt;0.05（多重比较按特征数 Bonferroni 校正）；
- 不达 → H-005 按"状态可测性"子句证伪；Headroom 观察保留为开放问题。

### G3（004c · 控制器有效性）

- v1 vs 最强固定基线（U_cf）的逐查询配对差过全部四闸门 q1-q4 **且**
  mean_diff &gt; 0 → **H-005 SUPPORTED（控制器形态）**；
- 捕获率 mean_diff / Headroom-H1 ≥ 50% 作为次要指标如实报告（不设硬闸门）；
- 选择准确率、切换频率、逐格分解表全部入结果（Master Prompt §13 Controller Quality）。

### G4（诚实成本，全程）

- 特征计算与控制器开销的 similarity_calls 全部计入 U_controller；
- 结果 JSON 的 meta 必须含：schema_version、seeds、λ 主值与扫描集、
  stats_params、strategy_template 引用、timestamp（E0 口径，D-3 部分收口）。

## 结果（运行后回填，本轮留空）

- `research/results/EXP-004a-oracle-*.json`（待生成）
- `research/results/EXP-004b-features-*.json`（待生成）
- `research/results/EXP-004c-controller-*.json`（待生成）

## Next Step

1. **R2**: 实现 `run_exp004a_oracle.py`（scripts/ 下）（零 src 改动，import 复用
   SCAN_STRATEGY_TEMPLATE/build_strategies），跑 11 配置 × 3 seed，回填 G1；
2. **R3**: 文档一致性小 PR（含 D-8 修复与本实验编号裁决的 engineering_plan 同步）；
3. G1 通过 → 004b 特征检验；G1-regime → 改写 H-005 为 regime 级表述；
   G1 失败 → 如实记 REFUTED，headroom 线收缩归档。**排程纪律**（预注册更正 2026-08-19）：原句
   「研究重心回到…引用扩张」作废——EXP-005（引用扩张）是 E2 既定工程
   载体，与 EXP-004 并行、互不前置，其启动只依赖 H-004/EXP-005 预注册
   闸门，不依赖本实验 G1 失败。

---

**预注册声明**: 本文档全部判定标准（λ 主值、阈值 0.03/0.02/0.05、seed 划分、
闸门 G1-G4）先于任何 EXP-004 运行写下；运行后不得回改，边界扩展（seed 3→5）
必须如实在结果中标注。统计工具不输出判定，判定只在运行器 `decide()` 集中拼装
（分层纪律与 E0 一致）。
