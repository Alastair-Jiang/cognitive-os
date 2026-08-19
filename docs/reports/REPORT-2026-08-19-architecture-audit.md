# REPORT-2026-08-19 — Architecture Audit（架构审计）

- **日期**: 2026-08-19
- **范围**: 全仓库（src / research / docs / configs / scripts / tests / CI），基于 commit `ad02b58`
- **性质**: 审计报告（无代码修改）。所有 [V] 结论均引用 `research/` 下的可复现实验。
- **触发**: Master Prompt v2.0 §40（第一轮只做 Audit 与 Research Design，不动代码）

---

## 1. Current Architecture（当前架构）

定位（与 README/vision 一致，非 AGI 主张）：

> An experimental architecture for studying persistent, adaptive, personalized information processing.

当前实现是一个**纯标准库（zero runtime deps, Python ≥ 3.10）的合成语料检索实验平台**，
分层如下（`docs/architecture.md` 与源码核对一致）：

```text
Orchestration (STUB) / Agents (STUB) / Memory (STUB)   ← 未来阶段，无代码
─────────────────────────────────────────────────────
Retrieval Layer [IMPLEMENTED]
  Strategy A/B/C + ProgressiveValidator + EvidenceGraph + metrics/stats
─────────────────────────────────────────────────────
Nets / Anchors / Validation [IMPLEMENTED]
─────────────────────────────────────────────────────
Datasets [IMPLEMENTED]  SyntheticEventCorpus（含 ground truth + 邻居索引）
```

数据流（第一版原型）：

```text
Query(种子碎片) → 策略(A/B/C) → 候选收集(检索网/锚点扩张)
→ 渐进式验证(置信度+共识+早停，无硬淘汰) → EvidenceGraph → 排序 + 效率/结构指标
```

架构事实（代码级核对）：

- 策略接口 `RetrievalStrategy`（`src/cognitive_os/retrieval/base.py`）直接依赖
  **具体类** `SyntheticEventCorpus`，无 Corpus/Embedder/Index 协议抽象
  （工程化路线 E1 计划项，尚未启动）。
- 邻居索引为 O(N²) 暴力预计算（`synthetic_events.py:148-162`），
  构建成本不计入查询时成本（BM-001 §6 已诚实声明）。
- 嵌入为随机合成向量；来源可靠性为生成时设定标量。结论不能外推到真实信息空间
  （BM-001 §6、architecture.md §7）。

## 2. Current Implemented Modules（已实现模块清单）

| 模块 | 文件 | 实现要点（核对源码） |
|---|---|---|
| 语料 | `src/cognitive_os/datasets/synthetic_events.py` | 18 参数 `SyntheticCorpusConfig`（含 `causal_chains`/`mention_prob` 因果链扩展）；top-m 语义邻居索引；`sample_queries` 支持 truncate（信息未完整场景）；`similarity_stats` 歧义统计 |
| 检索网 | `src/cognitive_os/nets/search_net.py` | `SearchNetConfig`（半径/时间窗/来源门槛/跳数/四信号权重）；多跳扩张 + 每轮预算 = `max_candidates_per_anchor × frontier`；`NetSearchStats` 诚实计数 |
| 锚点 | `src/cognitive_os/anchors/anchor_detector.py` | 四信号（语义+来源+时间+密度）锚点评分；候选池来自种子 1-hop 索引扩张（不扫全库，保效率主张） |
| 渐进验证 | `src/cognitive_os/validation/progressive.py` | 跨网/跨轮证据合并（`aggregation: max|mean`）；置信度 = (1−w)·score + w·consensus；早停三判据（stabilized/threshold/budget）；**无硬性淘汰** |
| 证据图 | `src/cognitive_os/graph/evidence_graph.py` | 多信号一致性建边；`causal_edges=True` 引用硬边（权重 1.0）；连通成分 + 纯度 |
| 策略 A | `retrieval/strategy_a_traditional.py` | 全库扁平 top-k，无索引（质量与成本双基线）；score = sem + source_bonus·source_weight |
| 策略 B | `retrieval/strategy_b_anchor.py` | 锚点检测 + 局部扩张（H-001 载体） |
| 策略 C | `retrieval/strategy_c_multinet.py` | 4 网并行 + 渐进验证 + 早停 + 置信度前沿反馈（H-002 载体） |
| 度量 | `src/cognitive_os/metrics.py` | P/R/F1@k、NDCG@k、MRR；事件纯度/链纯度（聚类级加权）、重建 P/R/F1 |
| 统计推断 | `src/cognitive_os/stats.py` | 配对差、Cohen's d_z、sign-flip 随机化检验、bootstrap 均值 CI（E0 交付，金值 17 测试） |
| STUB | `memory/` `agents/` `orchestration/` | 仅占位（宪法 §9 反虚荣复杂度） |

测试与门禁：87 用例 / 10 文件；CI = ruff + specs-consistency + hygiene-scan + pytest
（Python 3.10/3.11/3.12 矩阵，`ci.yml`）。

## 3. Current Experiments（实验台账）

| 实验 | 预注册文档 | 原始数据 | 状态 |
|---|---|---|---|
| BM-001 规格 | `research/benchmarks/BM-001-*.md`（含 §7 扩展） | — | 有效，D-2 修正后零漂移 |
| EXP-001 三策略基线 | `research/experiments/EXP-001-*.md` | 3 份 JSON（small 主模式 / t0.6 截断 / medium） | 完成 |
| EXP-002 歧义扫描+诊断 | `research/experiments/EXP-002-*.md` | 3 份 JSON（scan 10 格 / consensus / h003） | 完成 |
| EXP-003 多种子显著性 | `research/experiments/EXP-003-*.md` | 1 份 JSON（5 seed × 12 query） | 完成，判定 SUPPORTED（仅格点级） |

## 4. Verified Findings（已验证结论 [V]，全部有原始数据）

1. **A 是质量基线**：EXP-001 主模式 A F1@k=0.637 &gt; C 0.490 &gt; B 0.512；
   EXP-002 十格扫描中 9/10 格 A ≥ C（F1 口径），medium 档同向。
2. **锚点效率组件稳健成立**：B 的 similarity_calls 恒为 A 的 19%–24%
   （10/10 格，4–5× 节省，与歧义度无关）；EXP-001 中 B MRR 0.933 &gt; A 0.794。
3. **C 的早停机制有效**：75% 查询提前停止（平均 2.2 轮 vs 预算 6–8）；
   mean 聚合不改变该结论（EXP-002 诊断）。
4. **格点级 C &gt; A 已证实**（EXP-003，overlap-mid/noise-mid 格点）：
   mean_diff=+0.081，p=0.0001，95% CI [+0.044, +0.115]，d_z=+0.58，5/5 seed 同向；
   代价 sim_calls ~3.7×。**边界：仅该格点，且是"预算换质量"，不可表述为算法更聪明**。
5. **共识聚合不是杠杆**：mean vs max 无实质质量收益，成本 +73%–80%，早停率近腰斩。
6. **引用结构边恢复因果链有效**（图层面）：链连通率 0.940 vs 纯语义 0.294–0.398；
   但纯度口径有害（硬桥接稀释排他性）——**指标选取决定结论**。
7. **检索层建图无边际价值**：语义预筛的 top-k 候选里几乎不含跨事件引用目标，
   结构信号若要有用必须参与检索/扩张（EXP-002 明确结论，E2/EXP-005 方向）。

## 5. Falsified Hypotheses（已证伪，如实记录）

| 假设 | 判定 | 证据 |
|---|---|---|
| H-001 质量组件（"不显著损失 Recall"） | **REFUTED** | 10/10 格召回损失 26.2–56.0pp，全部远超 10pp 容忍线；损失与歧义度无单调关系，"低歧义→收敛"修订预期亦被否定 |
| H-002 按原表述（"多网更优"） | **REFUTED** | 高歧义档 C F1&lt;A 且成本 14×；截断模式 predR 0.554&lt;0.614；mean 聚合诊断排除"聚合方式"解释。格点级 C&gt;A（EXP-003）不推翻整体判定 |
| H-003 按纯度表述（"多信号建图纯度更高"） | **REFUTED** | EXP-001 差异 ≤0.013；EXP-002 重设计后 +causal 纯度 0.115/0.365 反而低于 multi-signal 0.479/0.646 |

## 6. Unresolved Hypotheses（未决问题）

1. **H-001 开放尾**：召回损失能否由锚点配置（数量/半径/预算）收敛？
   ——复杂度-质量权衡曲线（Phase 2 / E2 项），无数据。
2. **H-002 格点边界**：C 优于 A 的信息 regime 边界在哪里？10 格中仅 1 格经多种子
   复核；其余 9 格仍是单 seed。regime 异质性本身未被系统量化。
3. **H-003 链恢复口径**：结构信号参与检索扩张是否带来 RQ-3/RQ-4 实质增益？
   ——E2 计划（引用扩张通道 + 有序路径恢复度量），未实验。
4. **RQ-3 早期识别**：C predR 仍低于 A；结构信号引入扩张后的早期识别增益未测。
5. **RQ-5 / RQ-6（自适应策略选择）**：完全 UNVALIDATED，无任何实验。
   **这正是 EXP-004 的研究对象**（见 §9）。
6. Phase 3+ 全部 RQ（记忆/回声室/可插拔/世界模型）：UNVALIDATED，按宪法不进代码。

## 7. Technical Debt（技术债清单）

沿用 engineering_plan.md §1 编号并新增：

| 编号 | 债 | 状态 |
|---|---|---|
| D-1 | `run_exp002_h003.py` 内联 CORPUS_CFG（归档但漂移风险在案） | 未收口 |
| D-3 | 结果 JSON 无 config_hash / code_sha（EXP-003 仅 schema_version） | 未收口 |
| D-5 | `build_strategies` 在 `run_benchmark.py` 与 `run_exp002_scan.py` 两份拷贝（EXP-003 以 import 缓解，未消除） | 部分缓解 |
| D-6 | CI 无覆盖率门禁 / 类型检查 / 基准冒烟 job | 未收口 |
| D-7 | 无 ADR 目录 | 未收口 |
| **D-8（本轮新发现，活缺陷）** | **Windows/GBK 可移植性**：`check_specs_consistency.py:131,135` 向 stdout 打印 ✅/❌ emoji；`tests/test_specs_consistency.py` 以 `subprocess.run(..., text=True)`（locale 编码）拉起子进程 → GBK 控制台（中文 Windows 默认）下 `UnicodeEncodeError`，**本机实测 3/87 用例失败**；设 `PYTHONIOENCODING=utf-8` 后 87/87 全过。CI（ubuntu/UTF-8）不可见此缺陷。修复方向：测试侧 subprocess 显式 `encoding="utf-8", errors="replace"` 或注入 `PYTHONIOENCODING` 环境变量；脚本侧 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` | 待修（小 PR） |
| D-9 | 邻居索引 O(N²) 构建只在小语料可接受；E1 协议化前规模上限受限 | 已在 BM-001 §6 声明，随 E1 收口 |

## 8. Documentation Inconsistencies（文档不一致）

1. **EXP-004 编号冲突（需裁决，本报告已按 Master Prompt 裁决）**：
   `engineering_plan.md` E2 Gate 预留 "EXP-004" 给**引用扩张实验**（结构信号参与检索，
   前置 H-004 拆分）；而 Master Prompt v2.0 将 EXP-004 定义为
   **Adaptive Retrieval Strategy Selection**。裁决：按直接人类指令，
   **EXP-004 = 自适应策略选择**（本报告随附预注册）；E2 的引用扩张实验顺延为
   **EXP-005**，`engineering_plan.md` E2 Gate 文字需一行同步（列入 §10 计划）。
   假设编号同理：H-004 仍保留给 H-003 拆分（E2 Gate 既定），
   自适应策略选择假设注册为 **H-005**。
2. **测试计数漂移**：`README.md`（"51/51 tests pass"）与 `AGENTS.md`/`CLAUDE.md`
   （"currently 51/51"）停留在 E0 之前；`repo_inventory.md` 为 87/87（D-2 收口后准确）。
3. **RQ-1 状态注记滞后**：`research_questions.md` RQ-1 的 ⚠️ 附带观察仍写
   "需 EXP-003 多 seed 显著性检验复核"，而 EXP-003 已完成且 SUPPORTED
   （roadmap.md 与 H-002 已同步，RQ-1 未同步）。
4. **repo_inventory.md 状态标签与假设文件不一致**：
   - inventory 写 H-001 "部分证实(效率稳定)"，H-001 文件正式状态是
     "REFUTED（质量组件）+ 效率组件成立"；
   - inventory 写 H-003 "REFUTED(结构入检索无收益)"——**表述反了**：
     被证伪的是纯度口径；"结构入检索"恰恰**尚未实验**（是 E2 待办）。
5. `README.md` 目录树未列 scripts/ 新增脚本（check_specs_consistency / hygiene_scan /
   run_exp003 等），属轻微滞后。

## 9. EXP-004 Research Design（自适应检索策略选择——研究设计）

> 完整预注册见 `research/experiments/EXP-004-adaptive-strategy-selection.md`，
> 假设文件见 `research/hypotheses/H-005-adaptive-strategy-selection.md`。
> 本节为设计摘要。

**研究问题**（对应既有 RQ-5/RQ-6，Master Prompt §11）：

> Can an adaptive controller select among retrieval strategies based on query and
> evidence state, achieving a better quality-cost trade-off than fixed strategies?

**三段式证伪路径**（先廉价证伪，后建控制器——Incremental Feature Introduction）：

1. **EXP-004a 异质性/上界测量（Oracle Headroom）**：
   - 在 EXP-002 十格网格 + medium 档上，逐查询计算 A/B/C 的
     Utility U = F1@k − λ·(sim_calls/N)（λ 入 config，禁止硬编码；延迟只记录不优化）；
   - Oracle = 逐查询事后最优策略；Headroom = U_oracle − max(U_固定策略)；
   - **若 headroom ≈ 0 → H-005 在该 regime 无空间，廉价证伪**（这本身是合格结论，
     Master Prompt §37：失败亦可接受）。
2. **EXP-004b 状态可测性**：提取廉价查询侧特征（种子邻域密度、top-邻相似度
   margin、局部歧义统计——全部计入成本），检验特征与"逐查询最优策略"的可预测性。
3. **EXP-004c 控制器 v0/v1**：v0 = 恒选 A（对照）；v1 = 单特征规则；
   后续每加一个特征必须回答"是否改善选择"（Master Prompt §10）。

**判定闸门**（预注册，沿用 stats.py 四闸门模式 q1–q4 + 闸门 G1–G4，详见预注册文档）：
G1 headroom 存在（≥δ 且覆盖足够格点）；G2 选择准确率与 regret 达标；
G3 统计显著性（配对随机化检验 p&lt;0.05 + bootstrap CI 不含 0 + 跨 seed 一致 ≥80%
+ 最小效应 ≥0.01）；G4 诚实成本（特征计算开销计入 U）。

**边界**：不做跨查询学习（无 Strategy Memory）、不用 LLM、不碰真实 embedding、
不优化延迟——均留待后续假设各自预注册。

## 10. Minimal Implementation Plan（最小实现计划）

按"研究先行、最小改动、每步可证伪"排序：

| 轮次 | 内容 | 改动面 | Gate |
|---|---|---|---|
| R1（本轮，已完成） | 本审计 + H-005 假设 + EXP-004 预注册 + 日志 | 仅新增 4 个文档 | — |
| R2 | **EXP-004a Oracle headroom**：`run_exp004a_oracle.py`（scripts/ 下）（import 复用 `run_exp002_scan.SCAN_STRATEGY_TEMPLATE`/`build_strategies`，零 src 改动）；10 格 × ≥3 seed × 12 查询；JSON 落 `research/results/`；回填 EXP-004 文档 | 1 个脚本 | G1 |
| R3 | 文档一致性小 PR：README/AGENTS/CLAUDE 测试计数 51→87；RQ-1 注记同步 EXP-003 已复核；repo_inventory H-001/H-003 标签修正；engineering_plan E2 Gate "EXP-004"→"EXP-005"；**D-8 修复**（subprocess UTF-8 编码） | ≤5 文件小改 | 87/87 在 GBK 控制台亦通过 |
| R4 | 仅当 G1 通过：**EXP-004b/c** 特征提取 + 控制器 v0/v1（实验模块，建议 `strategy_selector.py`（src/cognitive_os/retrieval/ 下，R4 交付），不进核心）+ 单测 | 1 模块 + 测试 | G2–G4 |
| R5+ | D-3/D-5（runner 公共化 + config_hash）、E1 协议化（有 EXP-001 复跑护栏）——沿用 engineering_plan 既有排序，本计划不重复展开 | — | — |

**明确不做**（Master Prompt §18/§36 + 宪法 §2/§9）：复杂 Memory、Agent 层、
World Model、真实 LLM/embedding 接入、任何"看起来像 AGI"的功能——
在检索策略研究收敛之前一律不入库。

---

*审计方法：通读 git ls-files 全部 104 个跟踪文件的文档与源码主体，运行测试套件
（GBK 默认环境 84/87 → UTF-8 环境 87/87，定位 D-8），核对 7 份结果 JSON 与
实验文档的一致性。所有引用均给出仓库相对路径，可在本 commit 复现。*
