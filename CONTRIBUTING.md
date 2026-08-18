< English | [简体中文](./CONTRIBUTING.zh.md) >

# Contributing

Thank you for your interest in this project! Please take a moment to read this guide to make contributions smoother.

## Special conventions of the research repository

This project is an **open research platform** that follows the honesty rules in `docs/system_constitution.md`:

1. **Any claim of "better / more efficient" must point to a reproducible experiment**; claims without a `[V]` mark are hypotheses;
2. **Experimental results are only valid under the experimental conditions and must not be extrapolated** (synthetic data, config, seed);
3. **When a hypothesis is refuted, record it honestly as REFUTED**, and do not forcibly keep it;
4. New ideas should first be written into `research/hypotheses/` (status UNVALIDATED), experiments designed and pre-registered in `research/experiments/`, raw data dropped into `research/results/` after running scripts, and finally the hypothesis status updated with the experiment results.

## Quick start

1. Fork this repository;
2. Create a feature branch: `git checkout -b feat/your-feature`;
3. Make your changes and commit with a clear commit message;
4. Push and open a pull request against `main`.

## Pull request checklist

- [ ] PR description explains what was changed and why;
- [ ] Local tests pass (`python -m pytest tests/ -q`);
- [ ] New behavior is covered by tests;
- [ ] User-facing behavior changes are reflected in the docs;
- [ ] If research conclusions are involved: hypotheses / experiments / logs updated accordingly (in the `research/` directory).

## Issue conventions

- Use the issue forms: bug report / feature request / question;
- Mark issues with matching labels: `🐛 缺陷` / `✨ 功能` / `🔴 P0`-`🟢 P3`;
- Mark PR quality with `rating:` evidence-level labels (see LABELS.md).

## Commit style

Use **scoped conventional commits**: `type(scope): description`

```
feat(retrieval): 添加 X 策略
fix(validation): 修正早停判定
docs(hypotheses): 更新 H-001 状态
research(benchmark): EXP-002 扫描结果
```

Common types: `feat` `fix` `docs` `chore` `refactor` `test` `ci` `perf` `research`.
Scope = the module you changed (anchors / graph / nets / retrieval / validation / dataset / research / docs …).

## Code style

- Pure standard library (Python >= 3.10), keep zero runtime dependencies;
- Line width 100, follow the ruff config in `pyproject.toml`;
- Functions/classes should have a one-line Chinese docstring (consistent with the repository-wide documentation language).