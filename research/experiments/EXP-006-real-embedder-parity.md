
# EXP-006: 换真嵌入平价复核（预注册）

- **状态**: 预注册（2026-08-19 冻结，未运行；任何运行前更正须走公开更正流程并留 git 历史）
- **假设**: H-006（`research/hypotheses/H-006-real-embedder-parity.md`）
- **前置（全部先行落地，缺一不跑）**:
  1. E1 三协议 + 行为等价证明（恒等 Embedder + 暴力 Index 走新协议
     复跑 EXP-001，聚合指标一致）——ADR-0001/0003；
  2. 文本碎片语料发生器: 参数与 `configs/benchmark.small.json`
     同源（12 事件 × 8 碎片、5 主题、tpe=4、noise=0.5、来源结构、
     seed=20260819），但碎片以**模板文本**产出（主题句 + 事件谓词句 +
     因果链提及句），文本→嵌入由 GPU Embedder 完成；
  3. GPU 栈就位: BGE-M3 fp16 本地锁定（SHA256 钉死）、VRAM 预检
     （稳态 12 GiB 硬闸门，ADR-0003）。

## 实验设置（冻结）

- **语料**: 文本碎片语料（同 small 参数）；嵌入 BGE-M3 fp16，1024 维；
- **seed 池**: 5 固定值 {20260819, 7, 42, 131, 9999}（GPU 线一律 5 固定，
  与 EXP-003/005 同款纪律）；
- **查询**: 每 seed 12 个（query_seed=1），k=10；截断模式 frac=0.6 附加一轮；
- **臂**: A / B / C（三策略 EXP-001 起冻结，import 复用构建逻辑不复制，
  D-5）；无新增臂；
- **对照格点**: C vs A 主判定只在 tpe=4 / noise=0.30 格点（对齐 EXP-003）。

## 度量（与旧栈完全同口径）

F1@k / NDCG@k / Recall@k / MRR / predR；
成本: similarity_calls / index_lookups / candidates_scored +
iterations + latency_ms + GPU 遥测五件套
（gpu_mem_peak_mb / embed_tokens / embed_ms / index_build_ms /
knn_ms，ADR-0003 口径）。

## 判定标准（冻结，运行后不得回改）

四分量各自独立三态，判定只出自运行器 `decide()` 输出:

| 分量 | 判据（冻结） |
|---|---|
| P1（H-006a A 质量基线） | A 的 F1@10 / NDCG@10 / Recall@10 均 ≥ C，或 C−A 差异未过四闸门 |
| P2（H-006b B 效率） | B 的 sim_calls 均值 ≤ A 的 50%（即节省 ≥ 2×） |
| P3（H-006c C 早停） | 早停查询占比 ≥ 50%（5 seed 合并） |
| P4（H-006d C vs A 格点） | 四闸门 q1–q4 全过（q1 p&lt;0.05，R=10000；q2 95% CI 排除 0，B=10000；q3 跨 seed ≥80%；q4 \|diff\|≥0.01）；d_z 仅报告 |

四闸门实现沿用 `src/cognitive_os/stats.py` 与
`scripts/run_exp003_significance.py` 的 `decide()` 口径，不改参数。

## 护栏与诚实条款

- GPU 不可用 / VRAM 预检失败 → 整个实验记 INCONCLUSIVE，不跑半个；
- 结果 JSON 只追加不改（含 GPU 遥测原始值）；
- 任何分量 REFUTED 必须在结果文档与 `CHANGELOG` 双语同步，并注明
  「该结论仅合成嵌入成立」的影响范围；
- 单格点结论不外推（同 EXP-003 纪律）。

## 计划产出

- `research/results/` 下 EXP-006 结果 JSON（含遥测）；
- 结果文档追加判定表（四分量三态）；
- 项目说明书 `docs/project_manual.md` §5 按附录 D 协议回填新小节；
- `research/log/` 七段式回执。
