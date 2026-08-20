< English | [简体中文](./README.zh.md) >

# Cognitive OS — Research Repository for a Personal Cognitive OS

<div align="center">

*An open experimental platform for researching "Personal Cognitive OS" / personal intelligence infrastructure.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![GitHub issues](https://img.shields.io/github/issues/Alastair-Jiang/cognitive-os)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Alastair-Jiang/cognitive-os)
![GitHub stars](https://img.shields.io/github/stars/Alastair-Jiang/cognitive-os)

</div>

> **This is not an AGI project claim.**
> Whether this project approaches AGI should be decided by experimental
> results, not by conceptual judgement. The correct positioning:
>
> > *An experimental architecture for studying persistent, personalized,
> > adaptive intelligence.*

---

## Current status (2026-08-19)

| Item | Status |
|---|---|
| Phase 0 — Repo bootstrap | ✅ Done |
| Phase 1 — Dynamic Retrieval Prototype | ✅ First experiments done |
| Phase 1b — Hypothesis revision (EXP-002) | ✅ Done (10-cell sweep + consensus diagnosis + H-003 redesign) |
| Three strategies (A Traditional / B Anchor / C Multi-Net) | ✅ Implemented, 104/104 tests pass |
| Benchmark EXP-001 | ✅ Done (main + truncated + medium config) |
| Benchmark EXP-002 | ✅ Done (ambiguity sweep / consensus / H-003 redesign) |
| H-001 Anchor efficiency | ❌ REFUTED (quality component; efficiency holds across 10 cells, recall loss does not converge with ambiguity) |
| H-002 Multi-Net progressive validation | ❌ REFUTED (as stated; early stopping works, mean aggregation no real gain) |
| H-003 Structure consistency | 🔶 REFUTED (purity framing) / PARTIAL (chain-recovery framing, connectivity 0.940) |

**EXP-001 core conclusion (honest record, see [research/experiments/EXP-001](research/experiments/EXP-001-dynamic-nets-vs-baseline.md))**:
On the high-ambiguity synthetic corpus, **the flat semantic baseline A leads
on F1 / NDCG / Recall**. Dynamic Net is not yet proven more effective — but
Anchor gives a 4.3× compute saving and higher MRR (0.933 vs 0.794), and
progressive-validation early stopping works (75% of queries). **Until the
evidence is sufficient, Dynamic Net / Anchor stay experimental modules —
they do not enter the core architecture.**

**EXP-002 core conclusion (see [EXP-002](research/experiments/EXP-002-ambiguity-scan-and-diagnostics.md))**:
A 10-cell ambiguity sweep confirms H-001's efficiency component is robust
(4–5× saving) while its quality component fails everywhere (recall loss
26.2–56.0pp, no monotonic dependence on ambiguity); the C-consensus
aggregation max vs mean shows no real difference; the H-003 redesign shows
structural signals help **chain recovery** (connectivity 0.940 vs 0.29–0.40)
but hurt **event-cluster purity** (reference edges hard-bridge) — the chosen
metric decides the conclusion.

**Honesty principle**: every claim in this file and in `docs/` is a
hypothesis unless marked `[V]`. Any "better / more efficient" statement must
point to a reproducible experiment in `research/experiments/`.

---

## What this repository researches

The project originates from an information-security problem: a piece of
valid information is split into fragments propagating through different
nodes and paths. Traditional methods must wait until the information is
complete to verify it, at high cost. This project studies the inverse
question:

> **Before information has fully formed, can we — through dynamic "nets",
> local anchors, vector relations, and progressive validation — identify in
> advance which fragments are more likely to belong to the same valid
> information structure?**

Core concepts (all hypotheses, see [docs/vision.md](docs/vision.md)):

- **Dynamic Information Net**: multiple configurable search nets in
  parallel, rather than a single retrieval pipeline;
- **Progressive Validation**: validation moves from "one-shot at the end" to
  "continuous during the process";
- **Anchor Mechanism**: a few multi-signal anchors replace O(N²)
  pairwise comparison;
- **Structure Consistency ≠ Semantic Similarity**: "Apple launches / Apple
  earnings / apple-orchard disaster" are semantically similar but not the
  same structure;
- **Information Topology**: from retrieving relevant points to recovering
  relational structure;
- Long-term direction: Search Strategy Learning → Personal Memory →
  Multi-Agent → Cognitive OS → World Model → Physical Interface.

## Repository layout

```text
cognitive-os/
├── docs/                  vision / architecture / research_questions /
│                          system_constitution / roadmap
├── research/              research records
│   ├── hypotheses/        hypotheses (H-001..003, status UNVALIDATED)
│   ├── experiments/       registered / completed experiments (EXP-001)
│   ├── benchmarks/        benchmark specs (BM-001)
│   ├── results/           experiment result JSON (raw data)
│   └── log/               research log (Problem/Hypothesis/Change/Experiment/
│                          Result/Interpretation/Next Step)
├── src/cognitive_os/
│   ├── datasets/          synthetic event-fragment space (ground truth)
│   ├── nets/              search nets (configurable strategy primitives)
│   ├── anchors/           anchor detection (multi-signal)
│   ├── validation/        progressive validation (no hard pruning)
│   ├── graph/             evidence graph (multi-signal consistency)
│   ├── retrieval/         three strategies: A / B / C
│   ├── memory/            [STUB] future phase
│   ├── agents/            [STUB] future phase
│   └── orchestration/     [STUB] future phase
├── tests/                 unit tests (unittest, zero-dep)
├── configs/               benchmark configs (small / medium)
├── examples/              quickstart
└── scripts/               benchmark / experiment runners + CI gates
```

## Quick start

**Zero runtime dependencies** (pure Python stdlib, Python ≥ 3.10), no
`pip install` needed:

```bash
# 1. quick example (synthetic corpus + 3-strategy comparison)
python examples/quickstart.py

# 2. run benchmark (results written to research/results/)
python scripts/run_benchmark.py --config configs/benchmark.small.json

# 3. incomplete-information scenario (query time = 60% of event span)
python scripts/run_benchmark.py --config configs/benchmark.small.json --truncate 0.6

# 4. run tests (stdlib unittest)
python -m unittest discover -s tests -v
```

## The three retrieval strategies

| Strategy | File | Idea |
|---|---|---|
| A: Traditional | `src/cognitive_os/retrieval/strategy_a_traditional.py` | flat top-k over the whole corpus (baseline) |
| B: Anchor-based | `src/cognitive_os/retrieval/strategy_b_anchor.py` | multi-signal anchors + local expansion |
| C: Dynamic Multi-Net | `src/cognitive_os/retrieval/strategy_c_multinet.py` | parallel nets + progressive validation + early stop |

Every strategy honestly records `similarity_calls` / `index_lookups` /
`iterations` / `latency_ms` (see [docs/system_constitution.md](docs/system_constitution.md) §3).

## How to join the research (research discipline)

1. Write new ideas into [research/hypotheses/](research/hypotheses/) first,
   status UNVALIDATED;
2. Design and pre-register experiments in
   [research/experiments/](research/experiments/);
3. Run scripts; raw data lands in [research/results/](research/results/);
4. Update hypothesis status from experiments — if refuted, record REFUTED,
   do not force-retain;
5. Append a [research/log/](research/log/) entry for every significant change.

**Forbidden**: wrapping hypotheses as validated conclusions; substituting
"sounds advanced" for experiments; writing only "Added feature X" without
the hypothesis and the experimental result.

## Related docs

- [Project Manual](docs/project_manual.md)
- [Vision](docs/vision.md)
- [Architecture](docs/architecture.md)
- [Research Questions](docs/research_questions.md)
- [System Constitution](docs/system_constitution.md)
- [Roadmap](docs/roadmap.md)
- [Engineering Plan](docs/engineering_plan.md)

## Contributing

- [Contributing Guide](CONTRIBUTING.md) · [Security Policy](SECURITY.md) ·
  [Code of Conduct](CODE_OF_CONDUCT.md)
- [Label Guide](LABELS.md) · [AI Agent Guide](AGENTS.md) ·
  [Changelog](CHANGELOG.md)

## License

MIT © 2026 Alastair(Dongxu-Jiang). See [LICENSE](LICENSE).
