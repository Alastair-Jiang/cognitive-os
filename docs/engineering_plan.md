# Engineering Plan — 工程化路线图

> 状态: **计划文档**（方向 + 工作分解 + 验收标准）。
> 本文不包含实现代码与数学公式；只回答"做什么、为什么、做到什么程度算完成"。
> 本文与 [roadmap.md](roadmap.md)（研究路线图）互补：研究路线图回答"科学上验证什么"，
> 本文回答"工程上怎么把它落实"。所有阶段划分遵守
> [system_constitution.md](system_constitution.md) 第 2 条：**未经实验支持的概念不进核心架构**，
> 因此每个工程阶段都标注了它依赖的研究前置条件（Gate）。
> 本文所有未标注 [V] 的规划论断均为计划，不是承诺，更不是已验证结论。

---

## 0. 定位与总体原则

1. **研究优先，工程服务于研究**：工程的唯一目标是让"假设 → 实验 → 结果 → 修订"
   闭环更快、更可信、更可复现。不为了"看起来先进"提前建设施。
2. **两条路线**：研究路线（roadmap.md 的 Phase 1-11）与工程路线（本文 E0-E5）并行，
   工程阶段以研究阶段的结论作为准入闸门（Gate），研究阶段以工程阶段作为放大器。
3. **业界标准对齐**（按用途选用，不生搬硬套）：
   - 实验评测：TREC 式的 per-query 度量 + 配对显著性检验（IR 社区惯例）；
   - 预注册：OSF 式"先写判定标准再跑实验"（本仓库已在 BM-001 §5 实践）；
   - 架构决策：ADR（Architecture Decision Record）记录工程决策，
     与 research/log/ 的研究日志分工——ADR 记"为什么这么设计"，log 记"实验发现了什么"；
   - 可靠性：SRE 式 SLO/错误预算思想，用于检索延迟/成本预算的量化管理；
   - 质量门禁：CI 中 lint + 类型检查 + 覆盖率阈值 + 冒烟基准（业界 CI 标准）；
   - 发布：SemVer + Keep a Changelog + Conventional Commits（本仓库已采用）；
   - 数据治理：GDPR 式用户权利（View / Edit / Delete / Export）作为记忆控制面 API 设计底线
     （vision.md 第 10 节已自我要求，工程上必须可审计）。
4. **零运行时依赖红线**：核心运行时代码保持纯标准库（pyproject.toml 已声明）。
   引入 numpy 等仅限 dev 依赖或独立 benchmark profile，且必须有 ADR 说明。

---

## 1. 概念 → 现状 → 工程差距总表

通读全部源码与研究记录后的差距盘点（现状引用真实文件；结论引用真实实验）：

| 概念（vision） | 现状（代码/实验） | 工程差距（Gap） | 对应工程阶段 |
|---|---|---|---|
| Dynamic Information Net（§2） | `nets/search_net.py` 配置化检索网；策略 C 多网并行（`strategy_c_multinet.py`） | ① 语料与索引全内存、邻居索引 O(N²) 暴力构建、无持久化、无增量更新；② "网动态调整"未实现（配置静态，只有 C 的前沿随置信度调整）；③ 嵌入是随机合成向量，无 Embedder 抽象边界 | E1 |
| Progressive Validation（§3） | `validation/progressive.py` 跨网共识 + 置信度 + 早停；EXP-001 早停有效（75% 查询） | ① 置信度未校准（无可靠性度量，如校准误差）；② 成本只计数不预算（无 per-query 成本上限的调度）；③ 实验全为单 seed，无显著性检验 | E0 |
| Anchor Mechanism（§4） | `anchors/anchor_detector.py` 四信号锚点；EXP-002：效率组件 10/10 档成立（省 4-5×），质量组件 10/10 档失败（召回损失 26-56pp） | ① 配置敏感性扫描没有自动化 harness（Phase 2 前置）；② 锚点信号只有 4 种，vision 列出的因果一致性/历史证据/用户相关性未建模 | E0→E2 |
| Structure Consistency ≠ Semantic Similarity（§5, H-003） | `graph/evidence_graph.py` 多信号建图 + 因果硬边；EXP-002：链恢复口径成立（连通率 0.940 vs 0.398），纯度口径失败 | ① **结构信号只参与事后建图，不参与检索扩张**（EXP-002 明确结论）；② 无有序路径（A→B→C→D）恢复度量，只有成对连通率 | E2 |
| Information Topology（§6） | `chain_connectivity` 辅助指标 + 链纯度指标（`metrics.py`） | 链恢复目前是无向连通口径；拓扑恢复需要有序路径级度量与实验 | E2 |
| Personal Memory L1-L4（§10-11） | `memory/` STUB | 全部未建：分层 schema、行为证据门槛、VEED API、回声室度量、数据归属 | E3（Gate: Phase 6 研究） |
| Capability Interface / Multi-Agent（§12） | `agents/`、`orchestration/` STUB | 全部未建：能力适配器协议、Provider 注册、权限分级 L0-L4 + 审计 | E4（Gate: Phase 8 研究） |
| Cognitive Recommendation（§9） | 无 | Cognitive Utility 目标函数未定义——先立研究问题（RQ 未编号），工程不提前 | 暂不启动 |
| Biomimetic / World Model / Physical（§13-16） | vision 文本 | 留在愿景层，直到前置阶段产出可证伪的实验问题 | 暂不启动 |

**横切工程债（已实际盘点到的）**：

| 编号 | 问题 | 证据 | 归属 |
|---|---|---|---|
| D-1 | 实验脚本硬编码语料/策略配置，绕过 `configs/*.json` | `scripts/run_exp002_h003.py` 内联 CORPUS_CFG 与策略配置，与 `benchmark.medium.json` 存在漂移风险 | E0 |
| D-2 | BM-001 文档声明的默认参数与实际配置文件不一致 | BM-001 §2 写 `n_topics=8, tpe=3, noise=0.25`；`configs/benchmark.small.json` 实为 `5/4/0.5` | E0 |
| D-3 | 结果 JSON 无配置内容哈希、无代码版本（git sha），仅存配置文件路径 | `research/results/*.json` 的 meta 字段 | E0 |
| D-4 | 单 seed、单 k、无显著性检验 | EXP-001 局限自述；EXP-002 附带观察（noise=0.3 档 C>A）已标注"需 EXP-003 复核" | E0 |
| D-5 | EXP-002 三个脚本各自复制策略构建逻辑，无共享 runner 库 | `run_exp002_scan.py` / `run_exp002_consensus.py` / `run_exp002_h003.py` | E0 |
| D-6 | CI 无覆盖率门禁、无类型检查、无基准冒烟（改坏 harness 不会被发现） | `.github/workflows/ci.yml` 只有 ruff + pytest | E5 |
| D-7 | 无 ADR 目录，架构决策散落在文档与日志里 | 仓库结构 | E5 |

---

## 2. 工程阶段 E0-E5（方向 / 工作内容 / 验收标准）

### E0 实验与评测平台基线 — 最高优先级（**第一部分示范**：具体预期操作 + 预期结果 + 数学推理 + 代码已落地）

> **示范声明**：本文其余 E1-E5 保持原大纲式(方向/工作内容/验收)。
> E0 下面追加"操作-预期-推理-代码清单"的完整示范，作为 E1-E5 的模板。
> 本段凡"已运行/已落盘"均指向本 PR 的真实文件与 JSON 证据。

**方向**：把"跑实验"从一次性脚本变成可复用、可审计、可统计推断的平台。
这是 EXP-003(多 seed 显著性检验)的直接前置，也是后续一切工程的地基。

**为什么先做**：D-1/D-4/D-5 直接威胁研究结论的可信度——本仓库的立身之本是
实验诚实(宪法第 1 条)，而当前实验基础设施无法支撑"多 seed + 显著性检验"
这一业界最低门槛的统计严谨性。

---

#### E0-A. 预期建设目标(到达何种程度算完成)

| 项 | 预期结果 | 判定口径(看到什么算达成) |
|---|---|---|
| 统计推断模块 | 可复现给出 p / CI / 效应量 | 金值测试全过；同 rng_seed 复算同一数值 |
| 多种子 harness | EXP-003 首跑 JSON 落 `research/results/` | meta 含 seeds/k/queries/stats_params/timestamp |
| EXP-003 判定 | 附带观察升级为"已复核结论" | 下方四闸门 q1~q4 判定结果回填 |
| 结果 schema 起步 | 首跑 JSON 含 schema_version + 判定参数 | 项在 首跑 JSON meta 可 grep |
| 测试基座 | 零回归 + 统计金值 | 老 51 全过 + stats 17 金值(总 68) |

#### E0-B. 具体可执行操作(顺序 = 本 PR 真实落盘)

1. 新建 `src/cognitive_os/stats.py`(零依赖、标准库)：
   - `paired_diffs` / `mean_dz` / `permutation_test` / `bootstrap_mean_ci`;
   - 只支持双侧； n_resample / rng_seed / alpha 全部外露； 单参误用抛 `ValueError`。
2. 新建 `tests/test_stats.py`(金值 + 确定性 + 边界)：
   - 全同号差值 p 触达 sign-flip 固有下限(验证 2/2^n 分辨率语义)；
   - 完全对称数据 p=1.0(零分布全含 0);
   - 同 rng_seed 复算同一输出(确定性)；
   - CI 包围均值且随 n 收缩； 非法 alpha/n_resample 被拒；
3. 新建运行器 `scripts/run_exp003_significance.py`:
   `python scripts/run_exp003_significance.py --seeds 20260819,7,42,131,9999 --queries 12 --k 10`
   （策略/语料模板直接复用 `run_exp002_scan.SCAN_STRATEGY_TEMPLATE` 与
   `build_strategies`，无第三份拷贝, D-5 降解起点）
4. 预注册 + 运行：`research/experiments/EXP-003-*` 中规则先于运行写下
   （提交历史可证），原始 JSON 落 `research/results/`。
5. 判定结果按宪法如实回写： H-002 / roadmap 已做(无论方向)。

#### E0-C. 预期结果 vs 实跑结果(四闸门 q1~q4)

预注册判据(全部通过才 SUPPORTED； q1&q2&q4 反向才 REFUTED):
- q1 双侧配对随机化检验 p < 0.05;
- q2 boot 95% 均值差区间(B=10000)不含 0;
- q3 跨 seed mean_diff ≥ 0 占比 ≥ 80%;
- q4 最小效应 |mean_diff| ≥ 0.01(排除"统计显著但物理无意义")。

本 PR 实跑(2026-08-19， 数据 `research/results/EXP-003-significance-s5-q12-*.json`):

| seed | A F1 | C F1 | diff(C−A) |
|---:|---:|---:|---:|
| 20260819 | 0.765 | 0.804 | +0.039 |
| 7 | 0.814 | 0.941 | +0.127 |
| 42 | 0.824 | 0.946 | +0.123 |
| 131 | 0.765 | 0.770 | +0.005 |
| 9999 | 0.784 | 0.896 | +0.112 |

**判定: SUPPORTED** — q1 p=0.0001 ✅; q2 CI=[+0.044,+0.115] ✅;
q3 5/5=100% ✅; q4 +0.081 ≥0.01 ✅; 效应量 d_z=+0.58。
边界: 仅对 overlap-mid/noise-mid 格点成立； C 成本为 A 的 ~3.7×(sim 95 vs 275-411)；
按宪法第 2 条**不写入核心**(EXP-002 全网格大部分档仍是 A ≥ C)。
详文: `research/experiments/EXP-003-multiseed-significance.md`。

#### E0-D. 数学推理(为何这样判)

- **为何配对:** 不同查询难度差异巨大； 同一查询上取 d_i = F1_C,i − F1_A,i,
  消去"查询本身难度"混杂——差分布只反映策略相对行为。
- **为何随机化检验(sign-flip permutation):** per-query F1 混 0 与 1, 非正态,
  t 检验正态假设不成立； sign-flip 只需 H0 下"差分布关于 0 对称",
  是 IR/TREC 惯例(Smucker 2007); T=mean(d), 每个 d_i 随机 ±1 后求 T',
  双侧 p = (1 + #{|T'| ≥ |T|}) / (1 + R); n=60 的符号组合 2^60, R=10000
  随机逼近足够(分辨率下界 1/(1+R)=1e-4, 结论不受分辨率约束)。
- **为何 boot CI:** 同样非正态——取样均值的重抽样分布, 取 alpha/2 与
  1-alpha/2 分位点; "CI 不含 0 ⇔ 双侧 alpha=0.05", 与 q1 互补且给出
  效应量级(区间两端为量化的信心区间, 非单点二值)。
- **为何 q3 跨 seed 一致性:** 堆叠 60 对可能被单语料主导； ≥80% seed 同向
  检验"换语料换种"下效应是否稳健——语料级(基形)与查询级(难度)双轴补全。
- **为何 q4 最小效应:** "n 大则 p 优但 d≈+0.001" 无工程价值; 当前测量
  噪声量级 ~0.01-0.03(标准误), 门槛设 1pp 与噪声分辨率对应。
- **为何 d_z(配对标准化效应量):** d_z = mean(d)/SD(d)(总体口径, 除 n),
  小样本配对设计宜呈"差值自身的标准化"而非 t 语义效应;
  本次 +0.58 属"中等效应"(Cohen 约定 0.2/0.5/0.8)。
- **三方判定:** SUPPORTED(q1~q4 全通过); REFUTED(q1&q2&q4 显著且
  mean_diff ≤ -0.01, 反向); INCONCLUSIVE(其他)——把"测量不足"与
  "反向证实"分开, 反对"看不见就当没有"。
- **实现与判定对齐:** 判定只在 `decide()` 集中拼装;
  stats.py 不输出判定, runner 不内联统计——分层不清被宪法 §2 禁止。

#### E0-E. 代码/文档清单(本 PR 已交付)

| 资产 | 类型 | 行数(约) | 关键职能 |
|---|---|---|---|
| `src/cognitive_os/stats.py` | 库模块 | ~130 | sign-flip perm/boot CI/d_z, 零依赖 |
| `tests/test_stats.py` | 单测 | ~125 | 17 金值 + 确定性 + 边界 |
| `scripts/run_exp003_significance.py` | 运行器 | ~170 | 5 seed 复跑 → 四闸门判定 |
| `research/experiments/EXP-003-*.md` | 预注册+结果 | ~100 | 判定标准先写后跑, 结果后填 |
| `research/hypotheses/H-002*.md` | 假设 | — | EXP-003 复核结论回填 |
| `docs/roadmap.md` | 路线图 | — | 附带观察注记改为已定 |

**跨债降解(对应 §1 D 表):**
- D-4(单 seed/单 k/无显著性)→ **E0-C 已闭合**;
- D-5(三脚本复制)→ run_exp003 直接 import 原模板, 不再复制;
- D-1(内联 CORPUS_CFG)→ run_exp003 无内联(见 grep);
- D-3(无 schema_version)→ EXP-003 首跑 meta 已含; 
  config_hash/code_sha 在 runner 公共化时一并补入(E0-B 已列口径);
- D-2(BM-001 §2 vs small 漂移)→ **未收敛**, 下一 PR 的
  `check_specs_consistency.py` 入库+CI, 已在 D 表标注。

**验收标准(DoD) — 与本示范逐项对齐:**
- [x] 实验脚本 0 硬编码语料/策略参数(run_exp003 复用 SCAN_TEMPLATE, grep 可证);
- [x] EXP-003 产出: 5 seed 聚合 + p/效应量/CI, H-002 按 SUPPORTED 如实回填;
- [x] 结果 JSON meta 含 schema_version/seeds/stats_params/timestamp(首跑);
  config_hash/code_sha 列 E0-B 后续工作项(本 PR 体边界内);
- [x] 测试零回归(51→68), 新增 stats 金值 17;
- [x] 路线图 / 假设文件按结果如实更新(SUPPORTED 而非"印证原断言")。

**关联**: RQ-1/RQ-3 复核； 研究 roadmap Phase 1 收尾； `stats.py` 金值入测试;
判定语言与宪法 §2/§3 一致(不外推, 不写入核心)。

---

### E1 检索核心抽象化（Capability Interface 的数据层先例）

**方向**：按宪法第 6 条"核心是能力接口，不是模型依赖"，先把**数据面**抽象化：
语料、嵌入、索引三件事从策略代码中解耦。这是未来接入真实 embedding 模型的
唯一通道，也是消灭 O(N²) 索引构建的前置。

**Gate（研究准入）**：无硬闸门——这是对已实现模块（[IMPLEMENTED]）的内部重构，
不改变任何对外行为；但必须用 EXP-001 已有结果的复跑证明"重构前后指标不变"。

**工作内容**：
1. **Corpus 协议**（Protocol/ABC）：现有 `SyntheticEventCorpus` 的查询面
   （get / neighbors / event_fragments / mentions / observable_pids / sample_queries）
   提升为显式接口；策略与锚点只依赖协议。
2. **Embedder 协议**：合成随机嵌入的实现为默认 Provider；
   预留真实 embedding 模型 Provider 的接口位（不实现，仅定义契约 + mock 测试）。
3. **索引抽象 + 构建成本记账**：邻居索引构建单列为可替换组件，
   构建成本与查询成本分开上报（宪法第 3 条的工程化）；
   默认实现保持纯标准库，ANN 类优化仅留接口。
4. **持久化语料变体（最小）**：一个基于标准库 `json`/`sqlite3` 的只读语料实现，
   证明 Corpus 协议不绑定内存结构。

**验收标准（DoD）**：
- [ ] 三个策略（A/B/C）源码中不再 import `SyntheticEventCorpus` 具体类，
      只依赖协议（grep 可验证）；
- [ ] 全部现有测试在"内存语料 + 持久化语料"两种实现下都能通过（参数化测试）；
- [ ] EXP-001 的 small 配置复跑：各策略聚合指标与历史 results/ JSON 完全一致
      （容差内，seed 固定），以此证明重构无行为漂移；
- [ ] ADR-0001 记录 Corpus/Embedder/Index 三协议的设计取舍。

**关联**：架构文档 §5.1；为研究 roadmap Phase 2（真实信息空间）铺路。

---

### E2 结构信号参与检索（H-003 修订的工程载体）

**方向**：落实 EXP-002 的核心修订结论——**"结构信号必须参与检索/扩张，
而非仅事后建图"**。这是从"检索相关点"走向"恢复信息结构"（vision §6）的
第一段工程路径。

**Gate（研究准入）**：必须先有 H-004 假设文件（把 H-003 拆分为
"事件聚类"与"链恢复"两个目标，各配预注册指标——EXP-002 Next Step 第 4 条），
再预注册 EXP-005，才允许写策略代码。**顺序不可倒置**（宪法第 2 条）。

**工作内容**：
1. **引用扩张通道**：`SearchNet` 增加"沿 mentions 边扩张"的可配置通道
   （与语义半径扩张并列、独立计费 similarity_calls / index_lookups）。
2. **新策略变体**：B'/C' —— 在 B/C 基础上启用引用扩张（实验模块，
   不替换现有 A/B/C）。
3. **有序路径恢复度量**：链恢复从"无向连通率"升级为
   "有序路径恢复率"（ground truth 链 A→B→C→D 的方向是否被恢复），
   预注册进 BM-001 §8 扩展。
4. **Phase 2 锚点权衡曲线 harness**：n_anchors × radius × 预算 的网格扫描
   （复用 E0 runner），回答"B 召回损失是否可由配置收敛"（H-001 开放问题）。

**验收标准（DoD）**：
- [ ] H-004 假设文件存在且区分两个目标，各配可证伪判定标准；
- [ ] EXP-005 预注册文档存在（判定标准先于运行落盘）；
- [ ] 引用扩张的每次启用都能在结果 JSON 中单独核算成本增量；
- [ ] 有序路径恢复率有单元测试（构造已知链语料，黄金值可手算）；
- [ ] 锚点权衡曲线：≥3 配置 × ≥5 seed 的完整曲线数据落盘 results/，
      无论结论方向 H-001 开放问题被显式回答（收敛/不收敛）。

**关联**：RQ-3/RQ-4；研究 roadmap Phase 2 / Phase 4。

---

### E3 记忆控制面（Phase 6 的工程底座）

**方向**：L1-L4 分层记忆的"控制面"先行——即使记忆的"智能面"（什么该记住）
还是研究问题，**用户控制权**（View / Edit / Delete / Export）与
**证据门槛**（推断 ≠ 事实）是宪法第 4 条的硬约束，可以也应该先工程化。

**Gate（研究准入）**：分层记忆的有效性（RQ-7/RQ-8）仍 UNVALIDATED。
因此 E3 只建**控制面与存储 schema**，不建"自动写入策略"；
任何自动写入逻辑必须等对应假设通过实验。

**工作内容**：
1. **记忆存储 schema**（纯标准库 sqlite）：层级 / 内容 / 证据链接 /
   来源类型（用户陈述 vs 系统推断）/ 时间戳 / 撤销标记。
2. **VEED API**：View / Edit / Delete / Export 四操作的完整接口与
   审计日志（谁、何时、对哪条、做了什么）。
3. **证据门槛写入策略**：L3/L4（思维策略/元认知）条目必须携带
   行为证据引用，无证据的推断只能进入"待验证"区，不进入生效记忆。
4. **回声室度量定义**（研究协作项）：定义"反证保留率 / 来源多样性 /
   观点对立暴露度"等候选指标——先定义后实验，指标本身走预注册。

**验收标准（DoD）**：
- [ ] VEED 四操作全部有单元测试 + 审计日志断言；
- [ ] 无证据链接的 L3/L4 写入被存储层拒绝（负向测试）；
- [ ] Export 输出为自包含格式（用户可带走数据，数据归属可执行）；
- [ ] Delete 为硬删除且不可从导出残留（隐私底线测试）；
- [ ] 回声室候选指标以假设文件形式进入 research/hypotheses/，未验证不实现。

**关联**：RQ-7/RQ-8；宪法第 4 条；研究 roadmap Phase 6。

---

### E4 能力接口与权限分级（Phase 8 的工程底座）

**方向**：Capability Adapter 协议 + 权限分级 L0-L4。
同样遵循"控制面先行"：权限确认与审计是行为约束，可以先于智能面落地。

**Gate（研究准入）**：RQ-9（模型可插拔性）未验证。E4 只交付协议与
权限审计框架，用 mock provider 证明可插拔性；接入真实 Provider 的
价值判断留给实验。

**工作内容**：
1. **Capability Adapter 协议**：search / reason / remember 等能力的
   最小接口集（vision §12 的 Provider → Adapter → Agent → Orchestrator 分层）。
2. **Provider 注册表**：配置驱动（环境变量引用，绝不硬编码 key），
   内置 mock provider 供测试。
3. **权限分级执行器**：L0-L4 的动作分类、确认流程、审计日志；
   高危领域（医疗/金融/法律/保险/物理安全）强制人工确认钩子。
4. **行为一致性测试套**：同一 Agent 逻辑在两个 mock provider 下
   跑同一任务序列，断言行为等价（RQ-9 的可执行版本）。

**验收标准（DoD）**：
- [ ] 行为一致性套件：两个 mock provider 全绿（RQ-9 的工程侧证据）；
- [ ] 每一级权限的确认流程有正/负向测试（该确认未确认 → 动作被拒）；
- [ ] 全部审计事件可重放（给定日志序列能重建状态机）；
- [ ] 代码中 0 个硬编码 API key / endpoint（grep + CI 检查）；
- [ ] ADR 记录协议设计的取舍（为何最小接口集、如何防厂商锁定）。

**关联**：RQ-9；宪法第 5/6 条；研究 roadmap Phase 8。

---

### E5 质量门禁与发布工程（持续进行）

**方向**：把"仓库门面已标准化"（v0.1.0 已完成的部分）推进到
"质量门禁自动化"。这是横切阶段，与 E0-E4 并行滚动。

**工作内容**：
1. **CI 扩容**（`ci.yml`）：
   - ruff（已有）+ mypy（仅 public 接口与策略类，渐进收紧）；
   - 覆盖率报告 + 阈值门禁（核心模块行覆盖率目标 ≥85%，新代码不得低于存量）；
   - 基准冒烟 job：小配置全流程跑通（< 2 分钟），防止 harness 静默损坏（D-6）。
2. **ADR 实践**：`docs/adr/` 目录 + 模板（Nygard/MADR 精简版）；
   首批回填 ADR-0001（E1 三协议）与 ADR-0002（零运行时依赖红线）。
3. **发布流程**：SemVer + Keep a Changelog（已有）补充发布 checklist
   （测试 / 文档一致性 / 结果可复现抽查三项）。
4. **文档一致性纳入日常**：E0 的一致性检查脚本纳入 CI 后，
   任何"规格文档说了但配置不是"的漂移在 PR 阶段拦截（D-2 类问题归零）。

**验收标准（DoD）**：
- [ ] CI 全绿包含：lint + 类型检查 + 覆盖率门禁 + 基准冒烟；
- [ ] `docs/adr/` 存在、有模板、≥2 条已回填；
- [ ] 覆盖率基线落盘并只升不降（ratchet 机制）；
- [ ] 发布 checklist 文档化并演练过一次（0.2.0 目标）。

**关联**：横切；CONTRIBUTING.md 的 PR 检查清单自动化。

---

## 3. 阶段依赖与优先级

```text
E0 ──► E1 ──► E2（Gate: H-004 + EXP-005 预注册）
│       │
│       └──► E3（Gate: 控制面先行，智能面待 Phase 6 研究）
│
└──► E5（横切，随时并入）
        E4（Gate: 协议先行，真实 Provider 待 Phase 8 研究）
```

- **立刻可做**：E0 全部、E5 的 CI 扩容、E1 的协议提取（有 EXP-001 复跑护栏）。
- **等待研究闸门**：E2（等 H-004/EXP-005 预注册）、E3 智能面（等 RQ-7/8）、
  E4 真实接入（等 RQ-9）。
- **明确不做**（本轮工程周期内）：Cognitive Recommendation 的任何实现
  （目标函数未定义）；Biomimetic/World Model/Physical 的任何代码
  （无可证伪实验问题，宪法第 9 条反虚荣复杂度）。

## 4. 工作项 → PR 的映射标准

每个工作项按业界 trunk-based + 小 PR 惯例落地：

1. **PR 粒度**：单一主题、可独立评审，建议改动 ≤ 400 行；
   E0 的 runner 库与显著性检验分两个 PR。
2. **PR 流程**（CONTRIBUTING.md 已定义，此处细化工程项的附加要求）：
   - 每个工程 PR 引用本文的对应 DoD 条目作为验收 checklist；
   - 涉及行为变化（如 E1 重构）必须附带"复跑对比"证据
     （与 results/ 历史 JSON 的指标对照）；
   - 涉及研究闸门（E2/E3/E4）的 PR 必须先合假设/预注册文档 PR，
     代码 PR 引用之。
3. **标签约定**：`📚 文档` + `area: docs`（本计划）；
   工程实现 PR 用 `✨ 功能` / `area: retrieval` 等对应模块标签；
   rating 标签按证据等级如实自评——本计划 PR 为规划文档，不含实验主张。
4. **Commit 约定**：`type(scope): description`，
   工程基建用 `feat(benchmark)` / `chore(ci)` / `refactor(retrieval)`，
   实验结论用 `research(...)`（与现行历史一致）。

## 5. 风险与诚实边界

1. **计划失效风险**：EXP-003 若证实 C 在低噪声档的优势，E2 的优先级上升、
   网配置互补性诊断并入；若证伪，E2 聚焦引用扩张。**计划跟随实验，不相反**。
2. **过度工程风险**：E1 的 ANN 接口、E4 的多 Provider 只定义不实现，
   防止为未来买单（YAGNI 与宪法第 9 条双重约束）。
3. **结论边界重申**：本文所有现状描述引用的实验结论仅对已跑条件有效
   （合成语料、固定 seed、特定配置），不外推到真实信息空间；
   工程阶段完成 ≠ 科学假设成立，两者在 roadmap 与本文中分别记账。
