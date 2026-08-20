## LOG-2026-08-20-docs-consistency — 文档/计划一致性修订轮

- 状态: 完成
- 关联: `docs/plans/PLAN-2026-08-20-docs-consistency.md`（同轮修订清单）

### Problem
多份文档/计划的状态与概念口径落后于 main 真实进度：README 状态表停在 2026-08-19、
缺 EXP-003/EXP-004a/E1 三行；project_manual 内部测试数/文件数口径自相矛盾；
research_questions 的 Phase 编号与 roadmap 不一致；E1 已落地但 engineering_plan
DoD 仍全未勾选；EXP-005 预注册状态行乱码；roadmap 的 Phase 9-11 不切实际仍排期。

### Hypothesis
若把状态/编号/验收口径统一到 main @ ff02f49 实测事实（pytest 118/118、E1 三协议+
等价证明已落盘、EXP-004a G1 PASS、EXP-006 硬件未到位），则文档间不再互相矛盾。

### Change
纯文档/计划修订（不碰 `src/`、不改预注册判定标准、不改结果 JSON）：
- README（双语）状态表 + 目录树；roadmap EXP-004a 入账 + Phase 9-11 降级长期目标；
- research_questions Phase 编号对齐；engineering_plan E1 DoD 实勾 + E2 剩余前置 +
  EXP-006 硬件前置；project_manual 口径统一 + 拼写修正；EXP-005 状态行乱码修复；
- repo_inventory EXP-004/H-006/EXP-006 口径；ADR-0001 转 Accepted、ADR-0003 注记；
- OPENCLAW §5 重写真实待办。

### Experiment
实测复核（非盲信提示词快照）：`python -m pytest tests/ -q` 已跟踪口径 118/118（16 文件，
排除未跟踪的 5 个 EXP-005 WIP 测试后）；`python scripts/hygiene_scan.py` 起始 2 异常
（均在未跟踪的 `_ins.py` 残留损坏脚本，已删除）；`python scripts/check_specs_consistency.py`
零漂移。

### Result
- 全部 9 类文档/计划对齐完毕；`_ins.py` 删除后卫生扫描 0 异常；
- 等价证据 `research/results/PROOF-E1-EQUIV-20260820-021634.json`（`diffs`/`frozen_diffs`
  均为空）坐实 ADR-0001 转 Accepted；
- 测试数基线复核为 118/118（提示词"76 用例全过"是 unittest 子集口径；pytest 全量 118 为
  CI 权威口径，AGENTS.md 原数字无误）。

### Interpretation
文档/计划口径已收敛到 main 事实；sqlite 持久化语料变体是 E1 唯一遗留项，B'/C' 与
EXP-005 运行器是 E2 仅剩前置，EXP-004b 已解锁未启动——下一步只作排期记录，不启动。
EXP-006 硬件未到位，启动前必须遵守"无 GPU 记 INCONCLUSIVE"约定。

### Next Step
1. E1 sqlite 持久化语料变体；
2. B'/C' 策略变体 + EXP-005 运行器；
3. EXP-004b 状态可测性；
4. D-3 尾/D-5 尾工程债；
5. GPU extras 前置（≤15 GiB VRAM 到位后 EXP-006）。
