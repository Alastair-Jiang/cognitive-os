# LOG-2026-08-19-r3-docs-consistency — 文档一致性收口 + E2 Gate 前置工件补全

- **日期**: 2026-08-19
- **类型**: `fix(docs)` + `research(preregistration)`（无新实验，文档/预注册轮）
- **触发**: 架构审计 `docs/reports/REPORT-2026-08-19-architecture-audit.md` §8/§10 R3；
  本地实跑 `scripts/hygiene_scan.py` 发现 13 处异常（审计落盘后新增的门禁欠账）。

## Problem

1. 审计 R1 批次四个文档未过自家卫生门禁: 6 处拆词乱码（EXP-004 预注册）+
  7 处反引号路径（前瞻引用/相对路径）；
2. 审计 §8 列出的五项文档不一致未落地（测试计数 51→87、RQ-1 注记、
  inventory 标签、E2 Gate 编号、README 目录树）；
3. D-8 活缺陷（GBK 控制台 3/87 失败）未修；
4. E2 Gate 前置（H-004 拆分 + EXP-005 预注册）与 ADR 目录缺失，
   按宪法第 2 条阻塞 E2 全部工程项。

## Change

 #  内容  文件 
---------
 1  拆词修复 6 处 + Next Step 标题  `research/experiments/EXP-004-*.md` 
 2  前瞻路径改写（不带目录前缀 + 落位注记）  EXP-004 / 审计报告 / 审计日志 / H-005 
 3  测试计数 51→87  README 双语 / AGENTS 双语 
 4  E2 Gate 编号 EXP-004→EXP-005  `docs/engineering_plan.md` ×4 处 / `OPENCLAW.md` 
 5  RQ-1 注记（EXP-003 已复核，含边界）  research_questions.md 
 6  H-001/H-003 状态标签修正  repo_inventory.md 
 7  scripts/ 目录树行  README 双语 
 8  D-8 修复: 脚本 stdout reconfigure + 测试 subprocess 显式 UTF-8 + 环境变量  `scripts/check_specs_*.py` / `scripts/hygiene_scan.py` / `tests/test_specs_*.py` 
 9  H-004 假设注册（H-003 目标拆分, 双子假设+护栏）  `research/hypotheses/H-004-*.md` 
 10  EXP-005 预注册（引用扩张, G1-G4 + A-large 归因对照）  `research/experiments/EXP-005-*.md` 
 11  ADR 目录 + 模板 + ADR-0001（三协议）/ ADR-0002（零依赖红线）  `docs/adr/` 

## Experiment

无新实验。EXP-005 仅预注册（判定标准先于运行落盘），E2 策略代码仍被
Gate 阻塞（顺序不可倒置）。

## Result（完整验证链）

 检查  结果 
------
 `hygiene_scan.py`  ✅ 0 异常（修复前 13） 
 `python -m pytest tests/ -q`  ✅ **87/87**（含 GBK 模拟: 不设 PYTHONIOENCODING） 
 `ruff check .`  ✅ 全绿 
 `check_specs_consistency.py`  ✅ 零漂移 

## Interpretation

拆词/注入类损坏在本仓库历史上反复发生（EXP-003 14+ 处、EXP-004 6 处、
本轮新写文件再次中招），且防过滤字符注入是**生成侧**问题——D-2 把卫生
扫描门禁化（CI 零容忍）是唯一有效防线，本轮实践再次验证。D-8 修复后
本地 GBK 控制台与 CI（UTF-8）行为一致，"CI 全绿 ≠ 本地可复现"缺口闭合。

## Next Step

1. **R2 仍是前沿**: `run_exp004a_oracle.py`（EXP-004a headroom, G1）；
2. E2 工程项（引用扩张通道 + B'/C' + 有序路径恢复度量）现在 Gate 齐备，
   可与 EXP-004a 并行排期；
3. E5 剩余: 覆盖率门禁（ratchet）。
