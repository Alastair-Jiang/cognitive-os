# Repo Inventory — 仓库资产清单与标签分类

&gt; 用途: 把"已有与计划中"的所有资产按模块/证据/管线分类, 对应
&gt; [LABELS.md](../LABELS.md) 标签, 并标注生命周期位置。
&gt; 更新责任: 新增/归档资产时同步(对应宪法 §7)。

---

## 功能模块 (Production 代码)

| 模块 | 路径 | 状态 | 创建来源 | 预注的 Gate |
|---|---|---|---|---|
| 合成语料 | `src/cognitive_os/datasets` | ✅ 实装, EXP-001 起使用 | BM-001 | — |
| 传统检索 A | `src/cognitive_os/retrieval/strategy_a_traditional.py` | ✅ 实装, **质量基线** | RQ-1 | — |
| 锚点检索 B | `src/cognitive_os/retrieval/strategy_b_anchor.py` | ✅ 实装, H-001(效率组件稳态) | RQ-1, RQ-4 | H-002 EXP-003 格点复核 |
| 多网渐进验证 C | `src/cognitive_os/retrieval/strategy_c_multinet.py` | ✅ 实装, 未证更优(见 H-002) | RQ-1, RQ-3 | EXP-003 + H-004 |
| 检索网引擎 | `src/cognitive_os/nets` | ⚠️ 实装, 配置静态(计划 E1: Embedder/ANN 抽象) | RQ-1 | E1 |
| 渐进验证器 | `src/cognitive_os/validation` | ⚠️ 实装, 置信度无校准/无成本预算 | RQ-3 | E1+E2 |
| 锚点检测器 | `src/cognitive_os/anchors` | ✅ 实装, 4 信号 | RQ-4 | E2信号扩展 |
| 证据图 | `src/cognitive_os/graph` | ⚠️ 实装(仅事后评估), 未入检索扩张(H-003 失败) | RQ-2 | E2 |
| 度量工具 | `src/cognitive_os/metrics.py` | ✅ 实装 | BM-001 §3 | — |
| 统计推断 | `src/cognitive_os/stats.py` | 🆕 实装(E0, perm/seed boot/effect) | 工程化路线图 §E0 | — |
| 记忆控制面 | `src/cognitive_os/memory` | ❌ STUB(计划 E3) | PS-3 | — |
| 能力接口 | `src/cognitive_os/agents` | ❌ STUB(计划 E4) | PS-4 | — |
| 多 Agent 编排 | `src/cognitive_os/orchestration` | ❌ STUB(计划 E4) | PS-4 | — |

标签: `area: dataset` / `area: retrieval` / `area: anchors` / `area: graph` /
`area: validation` / `area: nets`(新增) / `area: stats`(新增) / `area: memory`(新增,
待实施) / `area: agents`(新增, 待实施)

---

## 研究证据 (Experiment & Proof)

| 工件 | 类型 | 现状 | 结论/用途 | 支持的 Rating |
|---|---|---|---|---|
| `research/hypotheses/H-001` | 假设 | 部分证实(效率稳定) | B 省 sim 4-5× | `rating: 📊 实验` |
| `research/hypotheses/H-002` | 假设 | 进行中(EXP-003 复核) | C 未证更优(附带观察待复核) | `rating: 🔬 假设` |
| `research/hypotheses/H-003` | 假设 | REFUTED(结构入检索无收益) | 链纯度反例成立 | `rating: ✅ 已验证`(证伪成立) |
| `research/benchmarks/BM-001` | benchmark 规格 | 有效, 已扩 §5/§7 | 三策略对照框架 | `rating: 📊 实验` |
| `research/experiments/EXP-001` | 实验 | 完成(2026-08) | 阶段基线 | `rating: 🏆 里程碑` |
| `research/experiments/EXP-002` | 实验 | 完成(2026-08) | 歧义扫描 + 诊断 | `rating: 🏆 里程碑` |
| `research/experiments/EXP-003` | 实验 | 进行中(预注册 + 首次实跑) | 复核附带观察 | `rating: 📊 实验` |
| `research/results/*.json` | 原始数据 | 2+3+1+1 个 EXP 结果 | 结论的唯一证据源 | `area: research` |

标签: `rating: 🔬 假设` / `rating: 🧪 原型` / `rating: 📊 实验` /
`rating: ✅ 已验证` / `rating: 🏆 里程碑` / `area: research`

---

## 运行管线 (Scripts & Configs)

| 脚本/配置 | 用途 | 现状 |
|---|---|---|
| `scripts/run_benchmark.py` | EXP-001 benchmark 入口 | ✅ 使用中(输出 EXP-001 JSON) |
| `scripts/run_exp002_scan.py` | EXP-002 歧义扫描 | ✅ 使用中 |
| `scripts/run_exp002_consensus.py` | 共识聚合诊断 | ✅ 一次性, 归档 |
| `scripts/run_exp002_h003.py` | H-003 测量 | ✅ 一次性, 归档(含 CORPUS_CFG 内联警讯 D-1) |
| `scripts/run_exp003_significance.py` | EXP-003 多种子显著性 | 🆕 使用中 |
| `scripts/apply_repo_config.sh` | 门面同步脚本 | ✅ |
| `configs/benchmark.small.json` | 小型 benchmark 配置 | ✅(但 §2 声明与实况分离见 D-2) |
| `configs/benchmark.medium.json` | 中型 benchmark 配置 | ✅ |
| `examples/quickstart.py` | 探针三角(A/B/C) | ✅ |

标签: `area: benchmark`(新增) / `area: research`

---

## 测试与质量

| 工件 | 现状 | 覆盖 |
|---|---|---|
| `tests/test_anchors.py` | ✅ | 4 test(信号边界) |
| `tests/test_causal_structure.py` | ✅ | 11(因果链/有序恢复) |
| `tests/test_graph.py` | ✅ | 5(图构建/连通) |
| `tests/test_metrics.py` | ✅ | 6(度量正确性) |
| `tests/test_stats.py` | 🆕 | 17(统计推断金值/确定性/边界) |
| `tests/test_strategies.py` | ✅ | 13(三策略行为) |
| `tests/test_synthetic_dataset.py` | ✅ | 7(语料生成可复现) |
| `tests/test_validation.py` | ✅ | 5(渐进验证早停) |

**总用例: 68/68 通过(原有 51 + 新增 17)。**
已知缺口(并行看, 后续跟进, 见工程化文档 G):

- CI 无覆盖率门禁: 现行 CI 只跑 lint+test, 不统计覆盖率(D-6);
- 部分核心文件(如 `retrieval/strategy_c_multinet.py` 早停边界)依赖行为级 test 而非白盒。

标签: 与模块同 `area:*` + PR 附上测试增量的 `🧪 rating: 原型`

---

## 门面与治理

| 工件 | 用途 | 状态 |
|---|---|---|
| `README.md` + `.zh` | 门面双语 | ✅(本次 PR 补 Engineering Plan 双链接) |
| `CONTRIBUTING` / `SECURITY` / `CoC` | 治理 | ✅(双语化, 同步上游) |
| `LABELS.md` + `labels.json` | 标签系统 | ✅(本 PR 扩 area:{nets, stats, benchmark, memory, agents}) |
| `AGENTS.md` + `CLAUDE.md` | AI 协作规约 | ✅(双语) |
| `docs/vision.md` | 愿景(未验证概念) | ✅ |
| `docs/architecture.md` | 系统架构(现状) | ✅ |
| `docs/system_constitution.md` | 诚实宪法 | ✅ |
| `docs/research_questions.md` | RQ 索引 | ✅ |
| `docs/roadmap.md` | 研究路线图 Phase 1-11 | ✅ |
| `docs/engineering_plan.md` | 工程化路线图(E0 全套示范, 后续) | 🆕 本 PR |
| `research/log/*.md` | 研究日志链 | ✅(每次显著变更追加) |

标签: `area: docs` / `📚 文档`

---

## 计划中资产(暂不入库, 先立项)

| 资产 | 计划阶段 | 前置 Gate | 预估 PR 体量 |
|---|---|---|---|
| `Corpus/Embedder/Index` 协议 + 骨架 | E1 | — | ≤ 400 行 |
| ANN 占位实现 | E1 | — | 与上同 PR |
| memory/L1-L4 分层 schema + VEED API | E3 | Phase 6 研究 + 预注册 H-004 类的 gate | ≤ 400 行骨架 |
| 回声室度量 + 记忆一致性实验 | E3 | 同上 | 配套研究 |
| Capability | E4 | Phase 8 研究 | 分两份 PR |
| Provider 注册 | E4 | Phase 8 研究 | 配套 |
| CI 覆盖率门禁 | E5 | — | ≤ 200 行 |
| ADR 目录 + 首批 3 条 ADR | E5 | E0/E1/E2 收口后 | 单独 PR |

标签: 上述 `area:` 目标 + `✨ 功能` / `rating: 🔬 假设`(标为未验证规划)

---

## 归档与退役

- `research/results/*.json`: **永久保留**(宪法 §7 审计依据, 即使被后续
  结果取代也留档——**不可 git-eliminate**);
- 判读逻辑已并入 `rating: 🏆 里程碑` 的里程碑 PR 可在 CHANGELOG 中
  遗迹标记为"已归档"而不删除——历史上 EXP-001 / EXP-002 已这样做。

---

*首次落笔: 2026-08-19; 下次同步: E0 收口时(覆盖 E1 骨架进入清单)。*
