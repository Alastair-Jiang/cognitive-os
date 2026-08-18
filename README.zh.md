< [English](./README.md) | 简体中文 >

# Cognitive OS — 个人认知操作系统研究仓库

<div align="center">

*研究"个人智能基础设施 / Personal Cognitive OS"的开放式实验平台。*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![GitHub issues](https://img.shields.io/github/issues/Alastair-Jiang/cognitive-os)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Alastair-Jiang/cognitive-os)
![GitHub stars](https://img.shields.io/github/stars/Alastair-Jiang/cognitive-os)

</div>

> **这不是一个 AGI 项目声明。**
> 项目最终是否能够向 AGI 靠近, 不应该由概念判断, 而应该由实验结果决定。
> 正确的定位是:
>
> > *An experimental architecture for studying persistent, personalized,
> > adaptive intelligence.*

---

## 当前状态(2026-08-19)

| 项 | 状态 |
|---|---|
| Phase 0 仓库初始化 | ✅ 完成(本仓库) |
| Phase 1 Dynamic Retrieval Prototype | ✅ 首轮实验完成 |
| Phase 1b 假设修订实验(EXP-002) | ✅ 完成(扫描 10 档 + 共识诊断 + H-003 重设计) |
| 三策略实现(A 传统 / B Anchor / C Multi-Net) | ✅ 已实现, 51/51 测试通过 |
| Benchmark EXP-001 | ✅ 完成(主模式 + 截断模式 + medium 档) |
| Benchmark EXP-002 | ✅ 完成(歧义档位扫描 / 共识聚合 / H-003 重设计) |
| H-001 Anchor 效率 | ❌ REFUTED(质量组件; 效率组件 10 档全成立, 召回损失不随歧义收敛) |
| H-002 多网渐进验证 | ❌ REFUTED(按原表述; 早停有效, mean 聚合无实质改善) |
| H-003 结构一致性 | 🔶 REFUTED(纯度口径) / PARTIAL(链恢复口径, 连通率 0.940) |

**EXP-001 核心结论(诚实记录, 详见 [research/experiments/EXP-001](research/experiments/EXP-001-dynamic-nets-vs-baseline.md))**:
在高歧义合成语料上, **扁平语义基线 A 在 F1/NDCG/Recall 上全部领先**。
Dynamic Net 尚未被证明更有效——但 Anchor 带来 4.3× 计算节省与 MRR 反超
(0.933 vs 0.794), 渐进验证早停有效(75% 查询)。**在证据充分前,
Dynamic Net / Anchor 机制保持为实验模块, 不进核心架构。**

**EXP-002 核心结论(详见 [EXP-002](research/experiments/EXP-002-ambiguity-scan-and-diagnostics.md))**:
歧义档位扫描(10 档)证实 H-001 效率组件稳健(节省 4-5×)而质量组件全败
(召回损失 26.2-56.0pp, 与歧义度无单调关系); C 的共识聚合 max/mean 无实质
差异; H-003 重设计揭示结构信号对**链恢复**有效(连通率 0.940 vs 0.29-0.40)
但对**事件聚类纯度**有害(引用硬桥接)——指标的选取决定结论。

**诚实原则**: 本文档及 docs/ 中的所有论断, 未标注 [V] 的一律是假设。
任何"更优/更高效"的说法都必须指向 research/experiments/ 中的可复现实验。

---

## 这个仓库要研究什么

项目最初来源于一个信息安全问题: 一条有效信息在网络中被切分成多个碎片,
通过不同节点、不同路径传播。传统方式必须等信息完整后才能验证,
成本很高。因此本项目研究反向问题:

> **能否在信息尚未完整形成之前, 通过动态变化的"网"、局部锚点、向量关系
> 和渐进式验证, 提前识别哪些碎片更可能属于同一个有效信息结构?**

核心概念(全部为假设, 详见 [docs/vision.md](docs/vision.md)):

- **Dynamic Information Net**: 多个可配置搜索网并行, 而非单条检索链路;
- **Progressive Validation**: 验证从"末端一次性"变为"过程中持续";
- **Anchor Mechanism**: 用少量多信号 Anchor 代替 O(N²) 两两比较;
- **Structure Consistency ≠ Semantic Similarity**: "苹果新品/苹果财报/
  苹果产区灾害"语义相似但不是同一结构;
- **Information Topology**: 从检索相关点走向恢复关系结构;
- 长期方向: Search Strategy Learning → Personal Memory → Multi-Agent →
  Cognitive OS → World Model → Physical Interface。

## 仓库结构

```text
cognitive-os/
├── docs/                  vision / architecture / research_questions /
│                          system_constitution / roadmap
├── research/              研究记录区
│   ├── hypotheses/        假设(H-001..003, 状态 UNVALIDATED)
│   ├── experiments/       预注册/完成实验(EXP-001)
│   ├── benchmarks/        Benchmark 规格(BM-001)
│   ├── results/           实验结果 JSON(原始数据)
│   └── log/               研究日志(Problem/Hypothesis/Change/Experiment/
│                          Result/Interpretation/Next Step)
├── src/cognitive_os/
│   ├── datasets/          合成事件碎片信息空间(带 ground truth)
│   ├── nets/              检索网(可配置搜索策略原语)
│   ├── anchors/           锚点检测(多信号综合)
│   ├── validation/        渐进式验证(无硬性提前淘汰)
│   ├── graph/             证据图(多信号一致性)
│   ├── retrieval/         三策略: A 传统 / B Anchor / C Multi-Net
│   ├── memory/            [STUB] 未来阶段
│   ├── agents/            [STUB] 未来阶段
│   └── orchestration/     [STUB] 未来阶段
├── tests/                 单元测试(unittest, 零依赖)
├── configs/               Benchmark 配置(small / medium)
├── examples/              quickstart
└── scripts/               run_benchmark.py
```

## 快速开始

**零运行时依赖**(纯 Python 标准库, Python ≥ 3.10), 无需 pip install:

```bash
# 1. 跑一次快速示例(合成语料 + 三策略对比)
python examples/quickstart.py

# 2. 跑 Benchmark(首轮实验, 结果写入 research/results/)
python scripts/run_benchmark.py --config configs/benchmark.small.json

# 3. 信息未完整场景(查询时刻 = 事件 60% 处)
python scripts/run_benchmark.py --config configs/benchmark.small.json --truncate 0.6

# 4. 运行测试(标准库 unittest)
python -m unittest discover -s tests -v
```

## 三种检索策略

| 策略 | 文件 | 思想 |
|---|---|---|
| A: Traditional | `src/cognitive_os/retrieval/strategy_a_traditional.py` | 全库扁平 top-k(基线) |
| B: Anchor-based | `src/cognitive_os/retrieval/strategy_b_anchor.py` | 多信号 Anchor + 局部扩张 |
| C: Dynamic Multi-Net | `src/cognitive_os/retrieval/strategy_c_multinet.py` | 多网并行 + 渐进验证 + 早停 |

每个策略都诚实记录 `similarity_calls` / `index_lookups` / `iterations` /
`latency_ms`(见 [docs/system_constitution.md](docs/system_constitution.md) 第 3 条)。

## 如何参与研究(研究纪律)

1. 新想法先写进 [research/hypotheses/](research/hypotheses/), 状态 UNVALIDATED;
2. 设计实验并预注册到 [research/experiments/](research/experiments/);
3. 运行脚本, 原始数据落到 [research/results/](research/results/);
4. 用实验更新假设状态, 被否定就记录 REFUTED, 不强行保留;
5. 每次重要修改写 [research/log/](research/log/) 条目。

**禁止**: 把假设包装成已验证结论; 用"听起来先进"代替实验;
只写 "Added feature X" 而不写假设与实验结果。

## 相关文档

- [Vision(愿景)](docs/vision.md)
- [Architecture(架构)](docs/architecture.md)
- [Research Questions(研究问题)](docs/research_questions.md)
- [System Constitution(系统宪法/行为约束)](docs/system_constitution.md)
- [Roadmap(路线图)](docs/roadmap.md)

## 参与贡献

- [贡献指南](CONTRIBUTING.md) / [安全政策](SECURITY.md) / [行为准则](CODE_OF_CONDUCT.md)
- [Label 指南](LABELS.md) / [AI 代理指南](AGENTS.md) / [更新日志](CHANGELOG.md)

## License

MIT © 2026 Alastair(Dongxu-Jiang)。详见 [LICENSE](LICENSE)。