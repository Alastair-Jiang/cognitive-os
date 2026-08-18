< [English](./CONTRIBUTING.md) | 简体中文 >

# 贡献指南 (Contributing)

感谢你对本项目的兴趣! 请花一点时间阅读本指南, 让贡献更顺畅。

## 研究仓库的特殊约定

本项目是**开放式研究平台**, 遵循 `docs/system_constitution.md` 的诚实规则:

1. **任何"更优/更高效"的说法必须指向可复现的实验**, 未标注 `[V]`
   的论断一律是假设;
2. **实验结果只对实验条件有效, 不得外推**(合成数据、config、seed);
3. **假设被否定时如实记录 REFUTED**, 不强行保留;
4. 新想法先写进 `research/hypotheses/`(状态 UNVALIDATED), 设计实验
   预注册到 `research/experiments/`, 运行脚本后把原始数据落到
   `research/results/`, 最后用实验更新假设状态。

## 快速开始

1. Fork 本仓库;
2. 创建功能分支: `git checkout -b feat/your-feature`;
3. 做出修改并用清晰的 commit message 提交;
4. push 并对 `main` 打开 pull request。

## Pull request 检查清单

- [ ] PR 描述说明了改了什么、为什么;
- [ ] 本地测试通过 (`python -m pytest tests/ -q`);
- [ ] 新行为有测试覆盖;
- [ ] 面向用户的行为变化已更新文档;
- [ ] 涉及研究结论: 假设/实验/日志已同步更新(`research/` 目录)。

## Issue 约定

- 使用 issue 表单: 缺陷报告 / 功能请求 / 提问;
- 用匹配的 label 标记 issue: `🐛 缺陷` / `✨ 功能` / `🔴 P0`-`🟢 P3`;
- PR 质量用 `rating:` 证据等级 label 标记(见 LABELS.md)。

## Commit 风格

使用**带 scope 的 conventional commits**: `type(scope): description`

```
feat(retrieval): 添加 X 策略
fix(validation): 修正早停判定
docs(hypotheses): 更新 H-001 状态
research(benchmark): EXP-002 扫描结果
```

常用 type: `feat` `fix` `docs` `chore` `refactor` `test` `ci` `perf` `research`。
Scope = 你改动的模块(anchors / graph / nets / retrieval / validation /
dataset / research / docs …)。

## Code style

- 纯标准库(Python >= 3.10), 保持零运行时依赖;
- 行宽 100, 遵守 `pyproject.toml` 中的 ruff 配置;
- 函数/类要有一行中文 docstring(与全仓库文档语言一致)。