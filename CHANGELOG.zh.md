< [English](./CHANGELOG.md) | 简体中文 >

# Changelog

本项目所有显著变更记录于此。
格式: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), 版本遵循 [SemVer](https://semver.org/)。

## [Unreleased]

### Added

- 工程化路线图 `docs/engineering_plan.md`: 概念→现状→差距总表、
  E0-E5 六阶段计划(方向/工作内容/验收标准)、工作项→PR 映射标准;
  盘点 7 项横切工程债(含 BM-001 §2 与 benchmark.small.json 参数漂移的新发现);
  **E0 段按要求重写为完整示范**(预期操作/实跑结果/数学推理/已落盘代码清单),
  其余 E1-E5 保持大纲式, 由本段内容由后段按同一模板执行时对照
- 统计推断模块 `src/cognitive_os/stats.py`: 配对差/Cohen d_z/sign-flip 随机化检验/
  boot 均值 CI(零运行时依赖, 仅标准库)
- EXP-003 多种子显著性复核运行器 `scripts/run_exp003_significance.py` +
  预注册实验文档(判定标准先写后跑) + 原始 JSON 数据; 判定 **SUPPORTED**
  (5 seed × 12 查询, mean_diff=+0.081, p=0.0001, 95% CI=[+0.044,+0.115],
  d_z=+0.58), 边界明确(**单格点成立 + 不写入核心**, 宪法第 2 条);
  H-002 / roadmap / 研究日志同步如实回填
- 仓库资产清单 `docs/repo_inventory.md`: 实装模块/研究工件/管线/测试/门面
  与标签对应, 含计划中资产(E1-E5)的提前标签化(完全便于用户查看)
- 标签扩展: `area: {nets, stats, benchmark, memory, agents}` 三处同步
  (LABELS.md / LABELS.zh.md / `.github/labels.json`, 先为未实施模块打 area 位)
- 研究日志 LOG-2026-08-19-e0-demo-EXP-003(四闸门判定设计 + 如实分屏)

- OpenClaw 专属工作提示词 `OPENCLAW.md`: 接续 E0 之后的工程化推进指引
  (工作循环/完整验证链/PR 卫生/诚实边界/下一步优先级 D-2、D-5、D-3 尾、E1),
  沉淀自 E0 完整示范周期(PR #4); OpenClaw 工作时自动读取, 其他 agent 仍以
  `AGENTS.md` 为准

### Fixed

- EXP-003 文档: 路径截断乱码(统计模块引用)修正为 `src/cognitive_os/stats.py`
- 仓库资产清单: 同步过期状态行(EXP-003 已完成——判定 SUPPORTED 仅格点级;
  H-002 复核完成)

## [v0.1.0] - 2026-08-19

### Added

- 仓库初始化: docs 体系(vision / architecture / research_questions /
  system_constitution / roadmap)
- 合成事件语料生成器(可配置主题重叠/噪声/时间/来源, 含因果链扩展)
- 三策略检索原型: A 传统 / B Anchor-based / C Dynamic Multi-Net
- Evidence Graph 结构一致性分析 + 聚类级纯度指标
- Benchmark 脚本与 EXP-001 / EXP-002 实验(歧义档位扫描 / 共识诊断 /
  H-003 测量重设计), 51 个单元测试
- 仓库门面标准化: issue forms / PR 模板 / CI / CODEOWNERS / 贡献指南 /
  安全政策 / 行为准则 / Agent 指南 / Label 体系(研究证据等级)