< English | [简体中文](./CHANGELOG.zh.md) >

# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [SemVer](https://semver.org/).

## [Unreleased]

### Added

- Engineering roadmap `docs/engineering_plan.md`: concept→status→gap matrix,
  six-phase plan E0–E5 (direction / work items / acceptance criteria), and the
  work-item→PR mapping standard; audited 7 cross-cutting engineering debts
  (incl. a new finding: BM-001 §2 parameter drift vs `configs/benchmark.small.json`)
- Research log LOG-2026-08-19-engineering-plan (planning rationale and next steps)

## [v0.1.0] - 2026-08-19

### Added

- Repository initialization: docs system (vision / architecture / research_questions /
  system_constitution / roadmap)
- Synthetic event corpus generator (configurable topic overlap / noise / time / source,
  with causal chain extension)
- Three-strategy retrieval prototypes: A traditional / B Anchor-based / C Dynamic Multi-Net
- Evidence Graph structural consistency analysis + cluster-level purity metrics
- Benchmark scripts and EXP-001 / EXP-002 experiments (ambiguity-level scanning / consensus
  diagnostics / H-003 measurement redesign), 51 unit tests
- Repository facade standardization: issue forms / PR template / CI / CODEOWNERS / contributing
  guide / security policy / code of conduct / Agent guide / label system (research evidence levels)