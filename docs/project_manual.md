
# cognitive-os 项目说明书（技术报告 v0.1）

&gt; **日期**: 2026-08-19 · **仓库**: `Alastair-Jiang/cognitive-os` · **许可证**: MIT · **环境**: Python ≥ 3.10，零运行时依赖
&gt;
&gt; **读者约定**: 每节首段为「人话版」（非技术读者读完即可走）；正文面向研究者与工程师。徽章: ✅ 已验证（附出处） · 🟡 部分验证 · 🗺️ 蓝图中 · 🗓️ 待回填（表头已冻结，等实验数据）。
&gt;
&gt; **溯源原则**: 本文每个数字与判断都指向仓库内文件（文末引用列表 [n]）；无出处的句子不写；反驳过的假设如实记 REFUTED。

## 摘要

&gt; 人话版：把「在一堆碎片里提前找回完整信息」做成了一套可反复实验的平台。已证实：平铺基线质量最高、锚点法省 4–5 倍算力、多网法在一种特定噪声条件下显著领先 8.1 个百分点；其余全部老实标「蓝图」。

本仓库研究一个逆问题：**信息尚未成形时，能否通过动态「网」、局部锚点、向量关系与渐进验证，提前识别哪些碎片更可能属于同一有效信息结构** [2][12]。当前 v0.1 交付 = 合成事件-碎片语料 + 三策略检索引擎（A/B/C）+ 多信号证据图 + 纯标准库统计推断 + 预注册实验纪律。

**核心数字**（全部可溯源，见文末引用列表）:

| 量 | 值 | 出处 |
|---|---|---|
| 演示检索成本（sim_calls / idx_lookups，单查询） | A 95/0 · B 21/30 · C 406/1326 | `examples/quickstart.py`（2026-08-19 本机复跑） [9] |
| 演示质量（top-10 命中目标事件碎片） | A 7/7 · B 4/7 · C 6/7 | 同上 [9] |
| 锚点算力节省（10 格扫描） | 4–5× 稳定 ✅（质量侧不成立 ❌） | EXP-002 [5] |
| 链恢复连通率（+causal 建图） | 0.940，对照 0.398 / 0.294 | EXP-002 H-003 再设计 [5] |
| 主显著性结果（C−A，格点 tpe=4/noise=0.30） | mean_diff=+0.081，p=0.0001，95% CI [+0.044, +0.115]，d_z=+0.58（60 配对 × 5 seed） | EXP-003 [6][10] |
| 工程健康 | 单元测试 113/113 ✅；卫生扫描 126 文件 0 异常 ✅ | `tests/` [8] `scripts/hygiene_scan.py` [11] |
| 工程完成度 | E0 ✅ · E1–E4 🗺️ · E5 持续 ✅ | [1] |
| 研究进度 | PHASE 0/1/1b ✅ · PHASE 2 进行中 | [17] |

**定位自评**: 「检索层研究平台」已立住（第 5 章证据）；「个人信息 OS」整体仍是蓝图（第 8 章路线图）。两者不混写。

## 1 引言：问题与定位

&gt; 人话版：信息安全里有道老题——一条有效信息被拆成碎片、经不同节点散播，传统做法只能等碎片齐了再统一核验，代价巨大。我们倒过来问：能不能边传播边提前判断？

### 1.1 动机

一段有效信息在真实世界里几乎从不完整出现：它被拆成碎片，沿不同节点与路径传播（消息、引用、转述、日志）。传统验证范式是「先收集齐全、再整体核验」，代价随规模爆炸。本项目的切入点是**前向问题**：在信息远未齐备的时刻，利用局部结构线索（相似度、时序、来源、共现密度）提前把「同属一个事件的碎片」聚出来、把「同属一条因果链的事件」连起来 [12]。

### 1.2 定位声明

&gt; *An experimental architecture for studying persistent, personalized, adaptive intelligence.* —— README [12]

三条硬约束（宪法 §1–§2 [12]）:

1. 一切「更优 / 更高效」的主张必须指向 `research/` 内可复现的实验；
2. 假设 ≠ 验证结论，未验证的不得写成已交付（本文徽章制度即为此）；
3. 被反驳的假设如实记 REFUTED（第 7 章不回避）。

**这不是 AGI 项目**；是否接近 AGI 由实验结果回答，不由概念宣言回答 [12]。

### 1.3 本说明书回答的问题

| 问题 | 章 |
|---|---|
| 能干嘛、现在就能演示什么 | §2、§5.1 |
| 怎么实现的（架构与方法） | §3、§4 |
| 凭什么信（证据与数据） | §5 |
| 做不到什么（局限） | §7 |
| 下一步往哪走（路线图） | §8 |

## 2 涉及领域

&gt; 人话版：横跨五个领域——检索、认知架构、结构化记忆、统计、系统工程；每个领域只借「能被实验检验」的那部分，不背书整个领域。

| 领域 | 本项目使用的部分 | 落点 |
|---|---|---|
| 信息检索（IR） | F1@k / NDCG@k / Recall@k / MRR / predR 评估口径；成本-质量权衡作为一等公民 | `src/cognitive_os/metrics.py`，BM-001 [3] |
| 认知架构 | 持久个性化记忆作为研究问题（L1–L4 分层记忆蓝图，未实现） | `docs/system_constitution.md` §4 [12] |
| 结构化记忆 / 图方法 | 多信号证据图、因果硬边、连通率与聚类纯度两类口径的分离 | `src/cognitive_os/graph/evidence_graph.py` |
| 统计推断 | 配对随机化检验、bootstrap CI、跨 seed 一致性、多重比较校正 | `src/cognitive_os/stats.py` [7] |
| 平台 / LLM 系统工程 | 三协议抽象（ADR-0001）、零依赖红线（ADR-0002）、宪法治理与 ADR 流程 | `docs/adr/` [13][14] |

边界声明：各领域只在「落点」文件范围内生效。当前无 LLM 调用——语料是合成嵌入，Embedder 为恒等实现（真实嵌入接入是 E1 后的事 [13]）。

## 3 系统架构

&gt; 人话版：一条流水线——先造一批「事件-碎片」语料，再把它变成可检索的索引；三种候选策略在检索环节竞争，其余环节完全一致，最后统一建证据图、统一过统计闸门。谁赢谁输由数据说话。

```text
SyntheticEventCorpus（96 碎片 / 12 事件，可参数化）
  → Index（top-m 邻居表，O(N²) 暴力实现——D-9 规模上限已知）
  → 检索策略 A / B / C（成本计数器全程开着）
  → EvidenceGraph（多信号建图，+causal 硬边可选）
  → stats.py 四闸门 → decide() 三态判定 → research/results/*.json
```

### 3.1 组件清单

| 模块 | 职责 | 状态 |
|---|---|---|
| `src/cognitive_os/datasets/synthetic_events.py` | 可参数化事件-碎片语料（主题共享、时序、来源权重、因果链） | ✅ |
| `src/cognitive_os/nets/search_net.py` | 检索网原语（半径扩张、时序窗、来源门槛、跳数上限；3 个成本计数器） | ✅ |
| `src/cognitive_os/anchors/anchor_detector.py` | 四信号锚点检测（语义/来源/时序/密度） | ✅ |
| `src/cognitive_os/validation/progressive.py` | 渐进验证与早停（置信度阈值 + 稳定轮数） | ✅ |
| `src/cognitive_os/graph/evidence_graph.py` | 证据图：多信号建边、+causal 硬边、连通率/纯度口径 | ✅ |
| `src/cognitive_os/retrieval/strategy_[abc]_*.py` | 三策略实现（EXP-001 起冻结） | ✅ |
| `src/cognitive_os/metrics.py` / `stats.py` | 评估口径与统计推断（纯标准库） | ✅ |
| `src/cognitive_os/memory/` `agents/` `orchestration/` | 记忆/代理/编排 | 🗺️ STUB |

协议层（ADR-0001 [13]，状态 Proposed 🗺️）: Corpus / Embedder / Index 三协议——为真实语料、真实嵌入、ANN 索引的可替换接入预留，落地于 E1；落地时须附行为等价证明（EXP-001 复跑聚合指标一致）。

### 3.2 三策略设计（EXP-001 起冻结 [4]）

| 臂 | 思路 | 关键配置（`configs/benchmark.small.json` [16]） | 一句话现状 |
|---|---|---|---|
| A（传统） | 平铺语义检索 + 来源加权 | source_bonus=0.05 | ✅ 质量基线：F1/NDCG/Recall 全面领先 [4] |
| B（锚点） | 先选锚点碎片，再从锚点局部扩张 | 锚点数 3、四信号权重 1.0/0.5/0.3/0.4、扩张半径 0.72 | 🟡 效率 ✅（省 4–5×）；质量 ❌（召回损失超线 [5]） |
| C（多网渐进验证） | 四张异构网并行迭代，置信度收敛即停 | 置信阈值 0.9、稳定 2 轮、上限 6 轮、共识权重 0.4；四网半径 0.88/0.70/0.78/0.72 | 🟡 单格点显著 +0.081 [6]；早停有效（75% 查询 [4]）；聚合无增益（H-002 REFUTED [5]） |

## 4 实验方法与设定

&gt; 人话版：规矩先定死再跑——语料参数一张表全公开；判定要连过四道统计闸门；结论三态：支持 / 反驳 / 不确定；跑完的数据落 JSON，不许改口。

### 4.1 合成语料参数（small 基准，[16]）

| 参数 | 值 | 说明 |
|---|---|---|
| n_events / fragments_per_event | 12 / 8 | 共 96 碎片 |
| n_topics / topics_per_event | 5 / 4 | 主题共享制造歧义 |
| within_event_noise | 0.5 | 簇内扰动 |
| embed_dim | 24 | 合成嵌入维度 |
| time_horizon / event_span | 100 / 20 | 时序轴 |
| source_count / min_weight / primary_prob | 4 / 0.6 / 0.6 | 来源结构 |
| index_top_m | 6 | 邻居表宽度 |
| seed | 20260819 | 语料种子 |

另有 `configs/benchmark.medium.json` 规模档；因果链语料（BM-001 §7.3 [3]，EXP-002/005 用）: 12 事件 = 3 链 × 4 事件，mention_prob=0.4，noise=0.30。

### 4.2 seed 纪律

| 实验 | seed 约定 |
|---|---|
| EXP-001 / EXP-002 | 单 seed 20260819（探索性） |
| EXP-003 | 5 固定值 {20260819, 7, 42, 131, 9999}，即 `scripts/run_exp003_significance.py` --seeds 默认池 [6] |
| EXP-005（预注册） | 同 EXP-003 五固定值（2026-08-19 运行前更正 [15][20]） |
| EXP-004（预注册） | 3+2 边界扩展（3 主 + 边界补 2，自有模式 [18]） |

### 4.3 四闸门与三态判定（`src/cognitive_os/stats.py` [7]）

| 闸门 | 判据 | 参数 |
|---|---|---|
| q1 | 配对随机化检验 p &lt; 0.05 | R=10000，seed 777 |
| q2 | bootstrap 95% CI 排除 0 | B=10000，seed 888 |
| q3 | 跨 seed 方向一致 ≥ 80% | — |
| q4 | \|mean_diff\| ≥ 0.01 | 实际显著性边界 |

三态: SUPPORTED（四闸门全过）/ INCONCLUSIVE / REFUTED。d_z 为报告量、**不是闸门**。既有 REFUTED 结论（H-001 质量侧、H-002）永久保留在案，不因后续实验删除 [17]。

### 4.4 成本诚实计量（宪法 §3 [12]）

三计数器口径：similarity_calls / index_lookups / candidates_scored，外加 iterations 与 latency_ms；跨策略口径必须一致；G3/G4 类成本表只认落盘实际计数器（2026-08-19 预注册更正 [15]）。

### 4.5 策略冻结与复用纪律

三策略自 EXP-001 起冻结为对照基线；后续实验一律 import 复用构建逻辑、不复制代码（D-5 教训 [4]）；新想法走 `research/hypotheses/` 注册新假设，不得改冻结臂。

## 5 评测

&gt; 人话版：先给一个 30 秒演示，再给三个已完成实验的结论卡；两个已预注册未运行的实验（EXP-004/005）留了带冻结表头的空表，跑完填数即可。

### 5.1 快速演示（30 秒）

命令: `python examples/quickstart.py`（固定 seed，2026-08-19 本机复跑与 [9] 一致）。语料 96 碎片 / 12 事件；查询目标事件 evt05（7 个碎片）:

| 策略 | iter | sim_calls | idx_lookups | latency | top-10 命中 |
|---|---|---|---|---|---|
| A | 1 | 95 | 0 | 0.49 ms | **7/7** |
| B | 2 | 21 | 30 | 0.17 ms | 4/7 |
| C | 6 | 406 | 1326 | 2.32 ms | 6/7 |

解读：A 质量最好、成本中等；B 省 4.5× sim 调用但丢 3 片；C 两个计数器都最高、质量居中。**演示不构成判定**——单查询不进四闸门；正式判定看 5.2–5.4。

### 5.2 EXP-001 基线对照 ✅（已判定 [4]）

设置: small / medium 两档 × 12/30 查询 × k=10，另附截断查询（--truncate 0.6）验证「信息未齐」场景；结果 JSON 4 份落 `research/results/` [10]。

| 结论 | 徽章 | 数字 |
|---|---|---|
| A 是质量基线（F1/NDCG/Recall 领先） | ✅ | F1 0.637（small/k10） |
| B 省算力 | ✅ | 4.3× sim_calls 节省；MRR 0.933 vs 0.794 |
| B 质量不达标 | ❌ | 精度/召回双双超线 |
| C 早停有效 | ✅ | 75% 查询提前终止 |
| C 整体更优 | ❌ | 未证明 |

**判定**: Dynamic Net 未证明更有效——A/B/C 均保留为实验模块，不进核心架构 [4]。

### 5.3 EXP-002 十格扫描与假设修订 ✅（已判定 [5]）

设置: OVERLAP × NOISE 十格扫描（10 格 × 12 查询）+ 共识聚合对照 + H-003 口径再设计。

| 发现 | 徽章 | 数字 |
|---|---|---|
| H-001 效率分量：B 的节省全格稳健 | ✅ | 4–5×（10/10 格） |
| H-001 质量分量：召回损失且不随歧义收敛 | ❌ REFUTED | 损失 26.2–56.0 pp |
| H-002 共识聚合（max vs mean）无实际差异 | ❌ REFUTED | 差异在噪声内 |
| H-003 再设计：+causal 提升链恢复 | 🟡 | 连通率 0.940 vs 0.398/0.294 |
| H-003 再设计：引用边硬桥接损伤事件纯度 | ❌ | 纯度下降 |
| 单 seed 格点 C &gt; A | 🟡 | F1 0.892 vs 0.755（+0.137）→ 触发 EXP-003 |

**判定**: 「结构信号有没有用」取决于测什么口径——帮链恢复、伤聚类纯度，两者不可兼得（H-003 拆分为 H-004a/H-004b 的原因 [5]）。

### 5.4 EXP-003 多种子显著性 ✅（格点级 SUPPORTED [6][10]）

设置: 单格点 tpe=4 / noise=0.30；5 固定 seed × 12 查询 = 60 配对；C vs A，配对随机化 + bootstrap。

| 量 | 值 | 闸门 |
|---|---|---|
| mean_diff（F1@10） | **+0.081** | q4 ✅（≥0.01） |
| p（随机化，R=10000） | **0.0001** | q1 ✅（&lt;0.05） |
| 95% CI（bootstrap，B=10000） | **[+0.044, +0.115]** | q2 ✅（排除 0） |
| 跨 seed 方向一致 | 过线 | q3 ✅（≥80%） |
| d_z（报告量，非闸门） | +0.58 | — |

**判定**: SUPPORTED——**仅在该格点**。*有效范围: 结论不外推到其他（tpe, noise）组合，不外推到真实语料；四闸门全过的也只有这一个格点。*

### 5.5 EXP-004 自适应策略选择 🗓️（预注册冻结 [18]，未运行）

&gt; 问: 系统能否自己学会按查询选策略？分解为三问: ①有没有可省的余量（headroom）②能不能归因到可测特征 ③能不能做成控制器。

主效用: U = F1@k − λ·(sim_calls/N)，主判定 **λ=0.02**（标签冻结，λ 敏感性另作稳健性报告）。

表 A headroom 分解（10 个独立配置 × 3 seed，池化；预注册文本写 11 系笔误，网格 3×3=9 + medium = 10，G1 阈值按原值执行）:

| 口径 | U_gf（最优固定策略） | U_cf（逐配置最优） | Headroom-H0 | Headroom-H1 | 判定 |
|---|---|---|---|---|---|
| 池化（λ=0.02） | 0.7100（A-traditional） | 逐配置 0.4802–0.9118 | +0.0358 | +0.0408 | G1 PASS（8/10 格 H1≥0.02；逐 seed 池化 H1 全正 +0.034/+0.037/+0.043） |

表 B 特征-标签关联（Bonferroni 校正）:

| 特征 | 关联统计量 | 校正后 p | 结论 |
|---|---|---|---|
| f1 / f2 / f3 | （待 EXP-004b 回填） | （待回填） | （待回填） |

表 C 控制器对照（v0 恒 A / v0′ 恒最优固定 / v1 单特征单阈值）:

| 变体 | U 均值 | vs U_cf 配对差 | 四闸门 | 判定 |
|---|---|---|---|---|
| v0 / v0′ / v1 | （待 EXP-004c 回填） | （待回填） | （待回填） | （待回填） |

### 5.6 EXP-005 引用扩张 🗓️（预注册冻结 [20]，未运行；2026-08-19 运行前更正 [15]）

&gt; 问: 在检索层加引用扩张通道（B'/C'），能否恢复完整因果链而不炸事件纯度？五臂: A / B / B′ / C / C′ + A-large（k′=15）归因对照。

表 A 主判定（有序路径恢复率差，5 固定 seed）:

| 对比 | mean_diff | p | 95% CI | 跨 seed 一致 | d_z | 判定 |
|---|---|---|---|---|---|---|
| B′−B | （待回填） | （待回填） | （待回填） | （待回填） | （待回填） | （待回填） |
| C′−C | （待回填） | （待回填） | （待回填） | （待回填） | （待回填） | （待回填） |

表 B 护栏（Δpurity ≤ 10pp 且 ΔF1 ≤ 5pp，最差格）:

| 护栏 | 阈值 | 实测最差 | 判定 |
|---|---|---|---|
| 事件纯度 / F1 | 10 pp / 5 pp | （待回填） | （待回填） |

表 C 归因对照（A-large k′=15）:

| 臂 | 路径恢复率 | 与 B′/C′ 差 | 归因结论 |
|---|---|---|---|
| A-large | （待回填） | （待回填） | （待回填） |

度量口径（预注册）: 有序路径恢复率 = 检索结果诱导有向图中 ground truth 链的最长有序子路径长 / L（L=链内事件数）；与既有 chain_connectivy（事后建图层、无向成对连通、EXP-002 的 0.940 来源）**不同层、不同定义，不可互换** [20]。

### 5.7 消融与敏感性 🗓️（计划章节，无数据）

- λ 敏感性曲线（{0, 0.01, 0.02, 0.05, 0.1} × EXP-004 数据）
- 十格 headroom 热区图（OVERLAP × NOISE）
- top-m 扫描（成本-质量曲线）
- 锚点配置权衡 harness（≥3 配置 × ≥5 seed，回应 H-001 开放问题）

### 5.8 误差分析（案例库）🗓️

预留格式: 每条 = 查询 × 策略 × 失败归因（结构缺失 / 噪声淹没 / 锚点误选 / 预算不足）。数据源: EXP-002 scan 逐格明细起步。

## 6 工程与治理

&gt; 人话版：这个仓库把「诚实」做成了机器——十条宪法、预注册、四闸门、卫生门禁、研究日志，过不了 CI 的东西进不了主干。

### 6.1 系统宪法十条（`docs/system_constitution.md` [12]）

| # | 条目 | 一句话 |
|---|---|---|
| 1 | 科研诚实 | 假设 ≠ 验证结果 |
| 2 | 实验纪律 | 研究驱动增量开发，先注册后实现 |
| 3 | 检索效率的诚实计量 | 成本计数器口径统一，不许挑好看的报 |
| 4 | 用户数据与推断控制 | 推断型记忆须可控可撤 |
| 5 | 权限与高危领域 | 能力分级 |
| 6 | Capability Interface 原则 | 模型可插拔、不写死厂商 |
| 7 | 研究日志纪律 | 每次显著变更追加 log |
| 8 | Commit 纪律 | `type(scope): 描述` |
| 9 | 反虚荣复杂度 | 不为炫技加层 |
| 10 | 宪法自身修订 | 走 ADR |

### 6.2 预注册 → 实验 → 结果 → 日志

研究问题（`docs/research_questions.md`，RQ-1…RQ-11）→ 假设（`research/hypotheses/`，H-001…H-005）→ 预注册实验（`research/experiments/`，EXP-001…005，闸门先写死）→ 运行器（`scripts/`）→ 结果 JSON（`research/results/`，只追加）→ 日志（`research/log/`）。

近期案例: H-004/EXP-005 预注册后、运行前的对抗复核发现 1 处幻觉 + 4 处安排错误，全部按「运行前更正、git 历史留原误」处置并写入 log [15]——预注册不是不许改，是不许偷偷改。

### 6.3 门禁矩阵

| 门禁 | 命令 | 现状 |
|---|---|---|
| 单元测试 | `python -m pytest tests/ -q` | 113/113（15 个测试文件）[8] |
| 仓库卫生 | `python scripts/hygiene_scan.py` | 103 文件 0 异常（零宽/实体/拆词/幽灵路径/杂散反引号）[11] |
| 规格一致性 | `python scripts/check_specs_consistency.py` | BM-001 §2 参数表与 `configs/*.json` 一致 |
| 提交风格 | `type(scope): 描述` | CONTRIBUTING.md |

### 6.4 工程债（公开记录，见 [19] Fixed 段与 [15]）

- BM-001 运行器 judgments 的 H-003 PASS 条件仍停 EXP-001 版口径，未随 §7.3 纯度重设计更新——待排期；
- 卫生门禁拆词正则只覆盖小写 1–2 字母 token，大写拆词可逃逸——待扩展 + 单测；
- D-9: O(N²) 暴力索引的规模上限（E1 三协议 + ANN 解决 [13]）。

## 7 局限与讨论（独立成章，无营销措辞）

1. **H-001 质量侧 REFUTED**: 锚点法在当前证据下召回损失不收敛，只在「低歧义 + 容忍损失」场景可用 [5]。
2. **H-002 REFUTED（如原始陈述）**: 多网共识聚合无实际增益；C 已证实的只有单格点显著性与早停有效性 [5][6]。
3. **H-003 结论由口径决定**: 链恢复（连通率 0.940）与事件纯度不可兼得；引用哪个性结论必须同时报口径 [5]。
4. **EXP-003 仅单格点**: 5 固定 seed × 1 格点 × 合成语料；不外推其他格点、不外推真实语料 [6]。
5. **语料是合成的**: 无真实信息空间、无真实嵌入（Embedder 恒等）；主题-噪声模型是「可控但失真」的替身 [16]。
6. **检索层之外的都还是蓝图**: 记忆/代理/编排均 STUB；L1–L4 分层记忆未实现 [12]。
7. **一致性注**: 本文与 BM-001/运行器旧口径如有出入，以预注册文档与本文为准，差异作为工程债登记（§6.4）[15][19]。

## 8 结论与路线图

&gt; 人话版：平台能跑、纪律成型、第一批证据已落盘。接下来两件事：教系统自己选策略（EXP-004），让引用结构信号进检索层（EXP-005 / E2）。

### 8.1 工程路线（E0–E5，[1]）

| 阶段 | 内容 | 状态 |
|---|---|---|
| E0 | 实验与评测平台基线 | ✅ 完成（三策略 + 运行器 + 统计 + 门禁） |
| E1 | 检索核心抽象化（Corpus/Embedder/Index 三协议 [13]） | 🗺️ 预注册（ADR-0001 Proposed） |
| E2 | 结构信号参与检索（引用扩张通道 + 计数器落地 + 有序路径度量黄金值单测） | 🟡 闸门就绪（H-004/EXP-005 已预注册 [20]），工程未动工 |
| E3 | 记忆控制面 | 🗺️ |
| E4 | 能力接口与权限分级 | 🗺️ |
| E5 | 质量门禁与发布工程 | ✅ 持续（§6.3 已运转） |

### 8.2 研究阶段映射（[17]）

PHASE 0（仓库引导）✅ → PHASE 1（动态检索原型）✅ 首轮 → PHASE 1b（假设修订 EXP-002）✅ → **PHASE 2（自适应搜索策略，进行中: EXP-004）** → PHASE 3（个人记忆）→ … → PHASE 11（物理接口）。

### 8.3 下一步（按优先级）

1. E2 工程前置（EXP-005 运行的先决条件）: SearchNet 引用通道、计数器口径扩展、有序路径恢复度量 + 黄金值单元测试；
2. EXP-004a headroom 运行器（R2，与 E2 并行、互不前置 [18]）；
3. 工程债清偿排期（§6.4 三项）。

## 附录 A 复现命令全集

```bash
# 30 秒演示（单查询，三策略对比）
python examples/quickstart.py

# EXP-001 基线（small，12 查询）
python scripts/run_benchmark.py --config configs/benchmark.small.json
# 截断查询（信息未齐场景）
python scripts/run_benchmark.py --config configs/benchmark.small.json --truncate 0.6
# medium 档
python scripts/run_benchmark.py --config configs/benchmark.medium.json

# EXP-002 十格扫描 / 共识 / H-003 再设计
python scripts/run_exp002_scan.py
python scripts/run_exp002_h003.py
python scripts/run_exp002_consensus.py

# EXP-003 显著性（默认 5 固定 seed）
python scripts/run_exp003_significance.py

# 门禁
python -m pytest tests/ -q
python scripts/hygiene_scan.py
python scripts/check_specs_consistency.py
```

## 附录 B 资产地图

```text
cognitive-os/
├─ src/cognitive_os/        # 全部代码（纯标准库）
│  ├─ datasets/  nets/  anchors/  validation/  graph/
│  ├─ retrieval/             # 三策略（冻结）
│  ├─ memory/  agents/  orchestration/   # STUB
│  └─ metrics.py  stats.py  similarity.py  types.py
├─ research/                   # 研究（只追加）
│  ├─ hypotheses/  experiments/  benchmarks/
│  ├─ results/                 # 结果 JSON
│  └─ log/                       # 研究日志
├─ scripts/                    # 运行器 + 门禁
├─ configs/                    # benchmark.small / medium
├─ tests/                       # 10 个测试文件，87 用例
├─ docs/                         # 本说明书 + 宪法 + 路线图 + ADR + 报告
└─ examples/quickstart.py
```

## 附录 C 术语表

| 术语 | 含义 |
|---|---|
| 碎片（fragment） | 信息的最小传播单元，带嵌入/时间戳/来源 |
| 事件（event） | 一组同源碎片的目标聚类 |
| 锚点（anchor） | B 策略先选出的种子碎片，四信号打分 |
| 网（net） | 半径/时序窗/来源门槛/跳数约束的局部扩张器 |
| 渐进验证 | C 策略多网迭代至置信度收敛即停 |
| 证据图 | 检索结果之上的多信号建图；+causal 为因果硬边 |
| chain_connectivity | 事后建图层无向成对连通率（EXP-002 口径） |
| 有序路径恢复率 | 检索层新度量: 诱导有向图中最长有序子路径 / L（EXP-005 口径） |
| headroom | 最优固定策略与全局最优的效用差（EXP-004） |
| 四闸门 | q1 随机化 p / q2 CI / q3 跨 seed / q4 效应量 |
| 预注册 | 判定标准先于运行冻结，运行后不得回改 |
| 徽章 | ✅ 已验证 · 🟡 部分 · 🗺️ 蓝图 · 🗓️ 待回填 |

## 附录 D 待填充回填协议

§5.5–5.8 的空表按以下规则回填，任何人照做即可:

1. **数值只取自** `research/results/EXP-00x-*.json`，禁止手算誊抄；
2. **表头冻结**: 列名、行名、闸门参数在预注册文档定稿时已冻结，回填不得增删列；
3. **判定句模板**: 「H-00xa 判定: 〔SUPPORTED / REFUTED / INCONCLUSIVE〕」——以运行器 `decide()` 输出为准替换，不得改写措辞；
4. **徽章同步**: 回填后把对应小节 🗓️ 换成 ✅/❌/🟡，并在 `research/log/` 追加一条；
5. **预注册措辞不可改**: 阈值、口径、seed 池若需变更，走「运行前更正」流程（如 [15]），git 历史保留原误。

## 引用列表

| # | 文件 |
|---|---|
| [1] | `docs/engineering_plan.md` |
| [2] | `docs/vision.md` |
| [3] | `research/benchmarks/BM-001-synthetic-event-reconstruction.md` |
| [4] | `research/experiments/EXP-001-dynamic-nets-vs-baseline.md` |
| [5] | `research/experiments/EXP-002-ambiguity-scan-and-diagnostics.md` |
| [6] | `research/experiments/EXP-003-multiseed-significance.md` |
| [7] | `src/cognitive_os/stats.py` |
| [8] | `tests/` |
| [9] | `examples/quickstart.py` |
| [10] | `research/results/EXP-003-significance-s5-q12-20260819-045149.json` |
| [11] | `scripts/hygiene_scan.py` |
| [12] | `docs/system_constitution.md`（含 README.md 定位声明） |
| [13] | `docs/adr/ADR-0001-corpus-embedder-index-protocols.md` |
| [14] | `docs/adr/ADR-0002-zero-dependencies.md` |
| [15] | `research/log/LOG-2026-08-19-prereg-corrections.md` |
| [16] | `configs/benchmark.small.json` |
| [17] | `docs/roadmap.md` |
| [18] | `research/experiments/EXP-004-adaptive-strategy-selection.md` |
| [19] | `CHANGELOG.md` |
| [20] | `research/experiments/EXP-005-cited-expansion.md` |

---

*本说明书遵循仓库溯源原则: 任何「更优/更高效」表述均可循引用编号复现；无法复现的表述不应存在。*
