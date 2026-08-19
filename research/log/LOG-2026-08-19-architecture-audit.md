# LOG-2026-08-19-ARCHITECTURE-AUDIT — 全仓库架构审计 + EXP-004 预注册

- **类型**: 研究设计（无代码修改）
- **范围**: `docs/reports/REPORT-2026-08-19-architecture-audit.md`（新增）、
  `research/hypotheses/H-005-adaptive-strategy-selection.md`（新增, UNVALIDATED）、
  `research/experiments/EXP-004-adaptive-strategy-selection.md`（新增, 预注册未运行）
- **触发**: Master Prompt v2.0 §40（第一轮只做 Audit 与 Research Design）

## Problem

项目进入"Adaptive Cognitive Retrieval Architecture"新阶段前，需要一个
基于仓库实况（而非愿景）的完整盘点：架构现状 / 已验证与已证伪结论 / 技术债 /
文档不一致，以及下一核心实验（自适应策略选择）的预注册设计。
同时 Master Prompt 的 EXP-004 编号与 `engineering_plan.md` E2 Gate 的
预留编号冲突，需裁决并留痕。

## Hypothesis

H-005（新注册, UNVALIDATED）: 存在廉价查询侧状态特征，使策略选择器
π(a|s) 在 U = F1@k − λ·(sim_calls/N) 下显著优于任何固定策略。
前置迹象: EXP-002/003 已证最优策略依赖 regime（9/10 格 A≥C, 1 格 C 显著优,
B 恒省 4-5×），但异质性的幅度/可预测性/可利用性未量化。

## Change

1. 架构审计报告（10 节, `docs/reports/REPORT-2026-08-19-architecture-audit.md`）:
   含模块清单、[V] 结论、证伪台账、技术债 D-1..D-9、文档不一致 5 项、
   EXP-004 设计摘要、最小实现计划 R1-R5;
2. H-005 假设文件 + EXP-004 预注册（三段子实验 004a/b/c, 闸门 G1-G4,
   λ 主值 0.02 + 敏感性扫描, seed 防泄漏划分, 判定标准先于运行写下）;
3. 编号裁决留痕: EXP-004 = 自适应策略选择（按 Master Prompt 直接指令）,
   引用扩张实验顺延 EXP-005, 自适应假设为 H-005（H-004 保留给 H-003 拆分）。

## Experiment

本轮无新实验运行。验证性操作:
- `python -m pytest tests/ -q`: GBK 默认环境 **84/87（3 失败）**,
  `PYTHONIOENCODING=utf-8` 下 **87/87** —— 定位为新债 **D-8**
  （`check_specs_consistency.py` emoji 输出 × subprocess locale 编码,
  Windows/GBK 可移植性缺陷; CI 的 ubuntu/UTF-8 环境不可见）;
- 通读全部跟踪文件, 核对 7 份结果 JSON 与实验文档一致性。

## Result

审计核心发现（详见报告）:
- [V] 结论 7 条（A 质量基线 / B 效率 4-5× / C 早停有效 / 格点级 C&gt;A /
  聚合非杠杆 / 引用边恢复链 / 检索层建图无边际价值）;
- 证伪 3 条（H-001 质量组件 / H-002 原表述 / H-003 纯度口径）;
- 未决 6 条（锚点配置收敛性 / C 优势 regime 边界 / 结构入检索 / 早期识别 /
  RQ-5/6 自适应 / Phase 3+ 全部）;
- 文档不一致 5 项（EXP-004 编号冲突、测试计数 51 vs 87、RQ-1 注记滞后、
  repo_inventory H-001/H-003 标签错位、README 目录树滞后）;
- 新技术债 D-8（活缺陷, 本机可复现）、D-9（O(N²) 索引规模上限）。

## Interpretation

仓库处于健康的研究中期状态: 假设-实验-证伪闭环运转正常, 负结果如实记录,
"哪些结论在哪些条件下成立"边界清晰。转向自适应策略选择的时机合理——
三策略在不同 regime 各有优势且代价结构差异大, 是策略选择的天然试验场;
但 **headroom 是否存在尚属未知**, 故 EXP-004a 把"最廉价的证伪点"放在最前。
D-8 说明"CI 全绿 ≠ 本地可复现", 环境矩阵是诚实计量的组成部分。

## Next Step

1. **R2**: `run_exp004a_oracle.py`（scripts/ 下）（零 src 改动）跑 11 配置 × 3 seed,
   回填 G1 判定（通过/regime/失败三路都已预注册）;
2. **R3**: 文档一致性小 PR（测试计数 51→87 同步、RQ-1 注记、inventory 标签、
   engineering_plan E2 编号顺延、D-8 修复）;
3. G1 结果驱动后续: 通过 → 004b 特征检验; regime → 改写 H-005 表述;
   失败 → H-005 如实 REFUTED, 重心回锚点权衡曲线与引用扩张（EXP-005）。
