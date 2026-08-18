< English | [简体中文](./CHANGELOG.zh.md) >

# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [SemVer](https://semver.org/).

## [Unreleased]

### Added

- Engineering roadmap `docs/engineering_plan.md`: concept→status→gap matrix,
  six-phase plan E0–E5 (direction / work items / acceptance criteria), and the
  work-item→PR mapping standard; audited 7 cross-cutting engineering debts
  (incl. a new finding: BM-001 §2 parameter drift vs `configs/benchmark.small.json`);
  E0 section rewritten as the requested full demonstration (concrete operations,
  expected vs. actual results, mathematical derivations, landed code inventory)
- Statistical inference module `src/cognitive_os/stats.py`: paired diffs,
  Cohen's d_z, sign-flip permutation test, bootstrap mean CI (zero-runtime-deps)
- EXP-003 multi-seed significance replication runner
  `scripts/run_exp003_significance.py` + pre-registered experiment doc +
  raw JSON results; verdict **SUPPORTED** (5 seeds × 12 queries,
  mean_diff=+0.081, p=0.0001, 95% CI=[+0.044,+0.115], d_z=+0.58), with explicit
  scope boundary (single cell only, not written into core)
- Repo asset inventory `docs/repo_inventory.md`: production modules, research
  artifacts, pipelines, tests, governance — each mapped to labels, incl. planned
  (unshipped) assets pre-tagged for E1–E4
- Label taxonomy extended: `area: {nets, stats, benchmark, memory, agents}`
  mirrored in `LABELS.md` / `LABELS.zh.md` / `.github/labels.json`
- Research log LOG-2026-08-19-e0-demo-EXP-003

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