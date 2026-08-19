< English | [简体中文](./CHANGELOG.zh.md) >

# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [SemVer](https://semver.org/).

## [Unreleased]

### Added

- E1 protocol layer: `src/cognitive_os/protocols.py` (structural
  Corpus / Embedder / Index protocols, stdlib-only) + identity adapters
  `src/cognitive_os/adapters/identity.py` (CorpusView / IdentityEmbedder /
  BruteForceIndex); strategy stack (retrieval / nets / anchors /
  validation) decoupled from the concrete corpus, machine-checked by
  a purity test (ADR-0001 acceptance); behavior equivalence proven by
  `scripts/prove_protocol_equivalence.py` — identity path reproduces the
  direct path field-by-field and matches frozen EXP-001 aggregates
  (latency excluded); tests 87 to 96
- GPU research line pre-registration: ADR-0003 (zero-dep redline
  scoped to stdlib core; GPU stack as optional extras behind E1
  protocols; 12 GiB steady VRAM hard gate; model SHA256 pinned;
  GPU telemetry counters) + H-006 (real-embedder parity, 4
  falsifiable parts) + EXP-006 pre-registration (5 fixed seeds,
  P1-P4 frozen criteria, four-gate `decide()` unchanged; EXP-004/005
  pre-registrations untouched)
- Project manual `docs/project_manual.md` (tech-report style, bilingual
  audience layering): abilities / architecture / methods / evidence /
  domains / governance / limitations / roadmap + reproduction commands +
  glossary + 20-entry citation list; status badges (✅/🟡/🗺️/🗓️) on every
  capability; frozen-header blank tables pre-drawn for EXP-004/005 with a
  fill-back protocol (Appendix D)
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

- OpenClaw-specific work prompt `OPENCLAW.md`: continuation guidance for the OpenClaw agent
  (work loop, full verification chain, PR hygiene, honesty boundaries, next-step
  priorities D-2/D-5/D-3-tail/E1), distilled from the E0 demonstration cycle (PR #4)
- Spec–config consistency checker `scripts/check_specs_consistency.py`: parses
  declared default params in BM-001 §2 and diffs them against `configs/*.json`
  (stdlib-only, exits non-zero on drift, wired into CI)
- Repo hygiene scanner `scripts/hygiene_scan.py`: five-class corruption scan
  (zero-width / HTML entities in .py / split-word garble / backtick path
  existence / stray backticks), CI-gated

### Fixed

- D-2: BM-001 §2 declared defaults (`n_topics=8, topics_per_event=3,
  within_event_noise=0.25`) corrected to actual `configs/benchmark.small.json`
  values (`5/4/0.5`), with correction note; config is the running baseline
  (EXP-001/002/003)
- EXP-003 doc: path-truncation garble in the stats-module reference corrected to `src/cognitive_os/stats.py`
- Repo inventory: synced stale status rows (EXP-003 completed — verdict SUPPORTED,
  grid-level scope; H-002 review completed)

- Documentation consistency sweep (audit R3): fixed 13 hygiene findings
  (word-split garble + dangling path refs) in the EXP-004 pre-registration and
  architecture audit; synced test counts 51→87 (README/AGENTS, EN+zh);
  updated RQ-1 note (EXP-003 reviewed); corrected H-001/H-003 status
  labels in the inventory; listed new scripts in the README tree
- EXP numbering decision landed: E2 gate cited-expansion experiment
  renumbered EXP-004 → EXP-005 (engineering plan + OPENCLAW)
- H-004 hypothesis registered (H-003 split into event-clustering vs
  chain-recovery, each with falsifiable gates) + EXP-005 pre-registered
  (cited-expansion channel; gates G1–G4; A-large attribution control)
- ADR directory added: template + ADR-0001 (Corpus/Embedder/Index
  protocols, Proposed) + ADR-0002 (zero-dependency redline)
- **D-8 fixed**: gate scripts reconfigure stdout to UTF-8; test
  subprocess decodes explicitly and injects PYTHONIOENCODING —
  87/87 now passes on a GBK console without env vars

- Pre-registration correction round (runtime untouched; both
  experiments still un-run): EXP-005 seed pool realigned to
  EXP-003's five fixed values {20260819, 7, 42, 131, 9999}; "five
  cost counters" corrected to the real 3-counter `NetSearchStats`;
  ordered-path recovery rate generalized to /L and
  disambiguated from `chain_connectivity`. EXP-004b optimal
  strategy labels frozen to main λ = 0.02; EXP-004 and EXP-005
  declared parallel (no gate-on-G1-failure). Audit also logs two
  engineering debts: BM-001 runner judgment caliber for H-003
  still EXP-001-style in `scripts/run_benchmark.py`, and hygiene
  SPLIT regex misses uppercase/≥3-letter split garble. Details
  in research/log/LOG-2026-08-19-prereg-corrections.md

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