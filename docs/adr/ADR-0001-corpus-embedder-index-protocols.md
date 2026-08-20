# ADR-0001: 检索核心以 Corpus/Embedder/Index 三协议抽象（E1）

- **状态**: Accepted（2026-08-20；E1 三协议 + 恒等适配器已落地，行为等价证明见
  `research/results/PROOF-E1-EQUIV-20260820-021634.json`；sqlite 持久化语料变体未做，遗留）
- **日期**: 2026-08-19
- **上下文**: 现行策略与 runner 直接耦合 `SyntheticEventCorpus` 具体类与
  O(N²) 暴力邻居索引（D-9），语料规模上限受制于此；真实 embedding、
  持久化语料、ANN 索引都无法替换接入。EXP-001 起三策略已冻结为对照基线，
  是抽取协议的最佳时机。

## 决策

  `src/cognitive_os/` 新增三协议（`types` 层或 `retrieval` 层内）:

  - Corpus: 点集与事件归属的只读接口（points / event_of / 相似度统计）;
  - Embedder: 文本→向量的可替换前端（合成语料为恒等实现）;
  - Index: top-m 邻居查询接口（合成现为 O(N²) 暴力实现，E1 后可换 ANN）。

  策略源码不得再 import 具体类（DoD 可用 grep 验证）。

## 理由

- 研究路线（vision §7）要求最终接入真实信息空间；协议先行是唯一不破坏
  既有实验可比性的路径；
- 替代方案"等真实数据阶段再重构"被否决：届时行为等价证明将无法构造
  （EXP-001 复跑基准会随重构窗口漂移）。

## 后果

- **正面**: D-9 规模上限解锁；EXP-004/005 的策略池可移植到任意语料。
- **负面/代价**: 双实现参数化测试成本；协议版本管理（schema 演进）。
- **不可逆点**: 一旦 EXP-00x 结果 JSON 引用协议版本号，协议字段语义
  冻结，变更需新 ADR。

## 关联

  `docs/engineering_plan.md` E1；行为等价护栏 = EXP-001 复跑聚合指标一致。
