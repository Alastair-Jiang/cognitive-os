English | [简体中文](./LABELS.zh.md) >

# Label Guide

Every label in this repository, what it means, and how it ranks. **Rating
tiers must carry an emoji prefix with a low→high gradient**; within other
dimensions, either all labels carry an emoji or none do. Labels use the
project's primary language (中文/Chinese).

## Type

| Label | Meaning |
|---|---|
| `🐛 缺陷` | Something isn't working as expected |
| `✨ 功能` | New feature or request |
| `📚 文档` | Improvements or additions to documentation |
| `❓ 问题` | A question that needs more information |
| `🙋 寻求帮助` | Extra attention is needed; contributions welcome |
| `🌱 新手友好` | Good for newcomers |

## Priority (P0 → P3)

| Label | Meaning |
|---|---|
| `🔴 P0` | Emergency: data loss, security bypass, crash loop, unusable core |
| `🟠 P1` | High: blocks planned work, needs attention soon |
| `🟡 P2` | Medium: normal priority |
| `🟢 P3` | Low: nice to have |

## Status

| Label | Meaning |
|---|---|
| `🚧 进行中` | Work is underway |
| `🧱 被阻塞` | Blocked by something else |
| `✅ 待合并` | Approved, ready to merge |
| `🎉 已合并` | Already merged |
| `🚫 不修复` | Will not be addressed |

## Area

| Label | Meaning |
|---|---|
| `area: retrieval` | Retrieval strategy module (strategies A/B/C) |
| `area: anchors` | Anchor detection & multi-signal module |
| `area: graph` | Evidence graph & structure-consistency module |
| `area: validation` | Progressive validation & early-stopping module |
| `area: dataset` | Synthetic corpus generation & evaluation data |
| `area: research` | Research artifacts: hypotheses/experiments/benchmarks/log |
| `area: docs` | Documentation & repo surface |
| `area: nets` | Dynamic information net (search_net) module |
| `area: stats` | Statistical inference module (perm/boot/effect size) |
| `area: benchmark` | Evaluation pipeline: experiment runners/configs/result JSONs |
| `area: memory` | Personal memory tiers/control plane (E3, not implemented) |
| `area: agents` | Multi-agent/capability interface/orchestration (E4, not implemented) |

## Rating (PR quality, low → high)

> Rating tiers are the only labels in this repo that **MUST carry an emoji**
> — the low→high gradient makes the ranking unambiguous. Theme: **research
> evidence tiers** (mirrors this project's hypothesis → experiment →
> conclusion culture).

| Rank | Label | Meaning |
|---|---|---|
| 1 | `rating: 🔬 假设` | lowest tier: unvalidated hypothesis / idea |
| 2 | `rating: 🧪 原型` | tier 2: prototype implemented, no experimental conclusion |
| 3 | `rating: 📊 实验` | tier 3: backed by experimental data |
| 4 | `rating: ✅ 已验证` | tier 4: hypothesis supported by experiments |
| 5 | `rating: 🏆 里程碑` | highest tier: establishes a phase conclusion / research milestone |

## Other

> Maintained by repo-standardizer — keep this file in sync whenever labels change.