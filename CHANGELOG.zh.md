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
- 规格-配置一致性校验器 `scripts/check_specs_consistency.py`: 解析 BM-001 §2
  声明默认参数与 `configs/*.json` 逐 key 对比(纯 stdlib, 漂移即退出码 1,
  已挂 CI 三版本矩阵)
- 仓库卫生扫描器 `scripts/hygiene_scan.py`: 五类落地损坏扫描(零宽字符 /
  .py 内 HTML 实体 / 拆词乱码 / 反引号路径存在性 / 字母被反引号拆断),
  已挂 CI 门禁

### Fixed

- D-2: BM-001 §2 声明默认参数 `n_topics=8, topics_per_event=3,
  within_event_noise=0.25` 修正为 `configs/benchmark.small.json` 实况
  `5/4/0.5`(配置为 EXP-001/002/003 实际运行基准, 附修正注记)
- EXP-003 文档: 路径截断乱码(统计模块引用)修正为 `src/cognitive_os/stats.py`
- 仓库资产清单: 同步过期状态行(EXP-003 已完成——判定 SUPPORTED 仅格点级;
  H-002 复核完成)

- 文档一致性收口（审计 R3）: 修复 13 处卫生异常（EXP-004 预注册与架构
  审计中的拆词乱码 + 失效路径引用）; 测试计数 51→87 同步（README/AGENTS
  双语）; RQ-1 注记更新（EXP-003 已复核）; inventory 中 H-001/H-003 状态
  标签修正; README 目录树补列新脚本
- EXP 编号裁决落地: E2 Gate 引用扩张实验顺延为 EXP-005
  （engineering_plan + OPENCLAW 同步）
- H-004 假设注册（H-003 拆分为事件聚类 vs 链恢复两目标，各配可证伪
  判定）+ EXP-005 预注册（引用扩张通道; 闸门 G1–G4; A-large 增益归因对照）
- 新增 ADR 目录: 模板 + ADR-0001（Corpus/Embedder/Index 三协议,
  Proposed）+ ADR-0002（零运行时依赖红线）
- **D-8 修复**: 门禁脚本 stdout 重配置为 UTF-8; 测试 subprocess 显式解码
  并注入 PYTHONIOENCODING — GBK 控制台无环境变量亦 87/87 通过

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