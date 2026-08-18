# LOG-2026-08-19-repo-init

- 状态: 完成(首轮实验结论另行追加: LOG-2026-08-19-exp001)
- 关联: RQ-1..RQ-4, H-001..H-003

## Problem

需要把"动态信息检索 → 个性化认知 → Agent → 仿生架构 → 世界模型 →
Physical AI"的思想转化为可验证、可实验、可迭代的研究仓库;
当前没有仓库、没有文档体系、没有原型、没有实验纪律。

## Hypothesis

- H0(仓库设计): 一个严格区分 Hypothesis 与 Validated Result、
  以研究日志为轴、实验驱动递增开发的仓库结构, 会比
  "一次性实现大而全系统"产生更多可验证知识。
- 首轮验证范围: 先建立仓库骨架 + 文档 + research 脚手架 +
  第一个 Dynamic Retrieval Prototype(BM-001), 回答"第一块砖是否成立"。

## Change

- 新建独立 git 仓库 `cognitive-os/`(与 DAFT 量化项目完全隔离)。
- 文档: docs/{vision, architecture, research_questions, system_constitution, roadmap}.md。
- 研究脚手架: research/{hypotheses(H-001..003), experiments(EXP-001 预注册),
  benchmarks(BM-001), log(模板+本条目)}。
- 工程: pyproject.toml(零运行时依赖)、LICENSE、.gitignore。

## Experiment

- 无(本轮为基础设施; 原型实验见 LOG-2026-08-19-exp001)。

## Result

- 仓库结构、文档体系、研究纪律已建立(见上文 Change)。

## Interpretation

- 本条目本身不验证任何检索假设; 它验证的是"研究仓库的可运行性"。
- 文档中所有 [H] 标记的论断均为假设, 未验证。

## Next Step

- 实现合成数据集 + 三策略 + Benchmark, 运行 EXP-001 并回填结果。
