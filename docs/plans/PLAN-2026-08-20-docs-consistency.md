# PLAN-2026-08-20-docs-consistency — 文档/计划一致性修订轮

- **状态**: 已完成（本轮只改文档/计划，不写策略代码、不跑实验）
- **日期**: 2026-08-20
- **基准**: main @ ff02f49（含 E1 协议层 / EXP-004a / E2 cite 通道；早于提示词所记 0368aad）

## 一句话

把 README / roadmap / engineering_plan / project_manual / research_questions /
ADR / OPENCLAW 的状态与概念口径对齐到 main 的真实进度；补全缺失前置；把不切实际的
远期阶段降级为长期方向。

## 本轮修订清单（已落实）

1. `README.md` + `README.zh.md`：状态表日期 2026-08-19 → 2026-08-20；补 EXP-003
   （格点级 SUPPORTED）、EXP-004a（G1 PASS，004b 解锁）、E1 协议层三行；测试数复核为
   118/118（pytest，16 文件）；目录树补 `protocols.py` / `adapters/` /
   `datasets/text_fragments.py`，hypotheses 扩 H-001..006、experiments 扩 EXP-001..006。
2. `docs/roadmap.md`：Phase 5 处标注"经架构审计裁决提前启动（004a G1 PASS，004b 解锁
   未启动）"，并注明这是审计裁决的架构转向（`docs/reports/REPORT-2026-08-19-architecture-audit.md`）；
   Phase 9-11（仿生/世界模型/物理接口）移入"长期目标"，删验收行，标"无验收、不排期"。
3. `docs/research_questions.md`：Phase 标题对齐 roadmap（Adaptive→5、Memory→6、
   Multi-Agent→8、RQ-10/11→长期方向）；RQ-1"下一步"更新（EXP-004a 已 G1 PASS）。
4. `docs/engineering_plan.md`：E1 DoD 按实勾选（三协议/解耦/等价证明已完成；sqlite
   持久化语料变体未做，标遗留，E1 记"大部完成，余 1 项"）；§1 差距表 Embedder 抽象边界
   已由 E1 解决；E2 显式列剩余前置（B'/C' + EXP-005 运行器）；补 EXP-006 硬件前置说明。
5. `docs/project_manual.md`：§6.3 与附录 B 测试数统一（118/118，16 文件）；摘要/§6.3
   卫生扫描口径统一（136 文件）；§5.5 EXP-004 徽章 🗓️→🟡（004a 已跑）；§8.1 E1 行 🗺️→🟡；
   §8.2 Phase 映射对齐 roadmap；§8.3 删"EXP-004a 运行器待做"、改写下一步；:263
   `chain_connectivy` → `chain_connectivity`。（HTML 实体项经原始字节核实为 0，无需改动。）
6. `research/experiments/EXP-005-cited-expansion.md`：状态行乱码
   `PR|E-RE|G|IS|TER|ED` → `PREREGISTERED`（仅修状态行，不动判定标准）。
7. `docs/repo_inventory.md`：EXP-004 口径统一（004a 已运行，004b/c 未启动）；
   H-006/EXP-006 行补硬件前置口径；测试数括号口径修正。
8. `docs/adr/ADR-0001` 转 Accepted（等价证据 `research/results/PROOF-E1-EQUIV-*.json`，
   sqlite 变体遗留）；`ADR-0003` 保持 Proposed + 硬件前置注记。
9. `OPENCLAW.md` §5 重写为当前真实待办；§1 快照日期/hash 与 D-2 状态同步。

## 剩余前置步骤（如实排期，本轮不启动）

1. **E1 收尾**：sqlite 持久化语料变体（`src/` 补 `sqlite3` 只读语料 + 参数化双实现测试）。
2. **E2 剩余前置**：B'/C' 策略变体 + EXP-005 运行器（cite 通道与有序路径度量已落地）。
3. **EXP-004b** 状态可测性（f1/f2/f3 特征检验，004a 已解锁）→ 004c 控制器。
4. **D-3 尾 / D-5 尾**：结果 JSON 增补 `config_hash`/`code_sha`；`scripts/` runner 公共化。
5. **GPU extras 前置（ADR-0003）**：≤15 GiB VRAM 显卡到位前不启动 EXP-006；无 GPU 记
   INCONCLUSIVE。

## 验证链

- `python -m pytest tests/ -q`（已跟踪口径 118/118，16 文件）零回归；
- `python scripts/hygiene_scan.py` 0 异常（工作树口径，含未跟踪文件）；
- `python scripts/check_specs_consistency.py` 零漂移。
