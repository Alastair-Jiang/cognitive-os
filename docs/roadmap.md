# Roadmap — 研究路线图

> 原则(见 system_constitution.md 第 2 条): **不要跳过前面的实验直接进入
> 后面的复杂系统。** 每个阶段有明确的验收标准, 验收失败就如实报告,
> 不强行进入下一阶段。

## Phase 0: 仓库初始化 — ✅ 完成(2026-08-19)

- [x] 仓库骨架、LICENSE、pyproject
- [x] docs 体系: vision / architecture / research_questions / system_constitution / roadmap
- [x] research 脚手架: hypotheses / benchmarks / log
- [x] 第一个 Dynamic Retrieval Prototype + 首轮 Benchmark(EXP-001, 40/40 测试通过)
- **验收**: ✅ 三策略可运行、测试通过、首轮实验诚实记录(含失败判定)。

## Phase 1: Dynamic Retrieval Prototype(第一块砖)— ✅ 首轮完成, 结论待修订

目标: 验证 RQ-1/RQ-2/RQ-3/RQ-4 中最基础的部分。

- [x] 合成事件数据集(可配置主题重叠/噪声/时间/来源)
- [x] 三策略: A 传统 / B Anchor-based / C Dynamic Multi-Net
- [x] 指标: Precision / Recall / F1 / NDCG / MRR + 效率指标
- [x] Evidence Graph 结构一致性分析
- [x] Benchmark 脚本 + 结果 JSON + 实验文档 EXP-001
- **验收(结论)**: 高歧义档位上 **A 基线质量最优**; H-001 部分成立(效率✅,
  Recall 损失 22.6pp 超 10pp 线), H-002 按原表述否定(机制部分有效),
  H-003 测量待重设计。→ 进入 Phase 1b: 歧义档位扫描 + 网配置诊断(EXP-002),
  在证据充分前 Dynamic Net / Anchor 不进核心架构。

## Phase 1b: 检索假设修订实验(EXP-002)— ✅ 完成(2026-08-19)

EXP-001 的诚实结论(H-001 部分成立 / H-002 否定 / H-003 待重设计)已修订验证:

- [x] 歧义档位扫描: noise/主题重叠 × 三策略, 10 档全跑——H-001 效率组件
      全成立(sim 节省 4-5×), 质量组件全失败(召回损失 26.2-56.0pp),
      损失与歧义度无单调关系 → 修订预期被否定;
- [x] 诊断 C 的共识聚合(max vs mean): mean 无实质收益且成本上升,
      聚合不是主要杠杆;
- [x] 重设计 H-003 测量: 因果链语料 + 聚类级纯度 + 链连通率——
      纯度口径 FAIL(引用边硬桥接), 链恢复口径支持(连通率 0.940 vs 0.29-0.40),
      指标选取决定结论;
- [x] 中档语料(medium config)基准运行: H-001 同样 FAIL(损失 32.9pp)。
- **验收**: 每个假设有可复现的量化结论, 状态已更新于 hypotheses/ 与
  research_questions.md。详见 [EXP-002](research/experiments/EXP-002-ambiguity-scan-and-diagnostics.md)。

⚠️ 附带观察(未定论): noise=0.3 档位单 seed 下 C F1@k=0.892 > A 0.755,
→ 已定: [EXP-003](../research/experiments/EXP-003-multiseed-significance.md) 复核 **SUPPORTED**(5 seed × 12 查询, mean_diff=+0.081, p=0.0001, CI=[+0.044,+0.115], d_z=+0.58)。仅对该格点成立, 按宪法第 2 条不写入核心(边界/成本见该文)。

## Phase 2: Anchor Mechanism 深化

- 多信号 Anchor(时间一致性/来源可靠性/因果一致性/历史证据)
- 复杂度-质量权衡曲线(不同 anchor 数量下的 Recall 损失)
- **验收**: RQ-2 有可复现的量化结论。

## Phase 3: Progressive Validation 深化

- 信息未完整场景(查询时刻早于事件结束)的早期识别度量
- 早停策略与验证预算的权衡
- **验收**: RQ-3 有量化结论。

## Phase 4: Information Graph / Topology

- 事件结构重建(不只是检索相关点)
- 关系结构恢复(A→B→C→D)的度量
- **验收**: RQ-4 消融实验(纯语义 vs 多信号)。

## Phase 5: Adaptive Search Strategy

- P(SearchStrategy | Query, Context, History) 的建模与度量
- **验收**: RQ-5/RQ-6 有实验。

## Phase 6: Personal Memory

- L1-L4 分层记忆 + 行为证据要求 + 回声室度量
- **验收**: RQ-7/RQ-8 有实验, 隐私/记忆控制 API 落地。

## Phase 7: Cognitive Recommendation

- Cognitive Utility 目标函数(非 CTR)
- 认知路径推荐的度量
- **验收**: "下一条最有认知价值的信息"可度量。

## Phase 8: Multi-Agent Orchestration

- Capability Interface + 可插拔模型 Provider
- 权限分级落地(Level 0-4)
- **验收**: RQ-9 模型可插拔性实验。

## Phase 9: Biomimetic Cognitive Architecture

- Information Flow 研究(什么进工作记忆/长期记忆/被遗忘/获得更多计算资源)
- Dynamic Cognitive Graph(W 随反馈更新)
- **验收**: 有可度量的信息流策略, 非比喻式架构。

## Phase 10: World Model

- 人/事件/时间/地点/因果统一关系空间
- **验收**: RQ-10 有实验。

## Phase 11: Physical / Robotic Interface

- Search / Reason / Remember / Plan / Navigate / Communicate / Manipulate / Observe
- Cognitive Core → Capability API → Physical Action 闭环
- **验收**: RQ-11 延迟/可靠性边界有测量。

---

## 长期目标(不是阶段)

- AGI 相关问题的研究(泛化/迁移/长时记忆/持续学习/规划/世界建模/
  元认知/工具使用/具身智能)——**AGI 是研究方向, 不是当前结论**。

## 状态约定

| 状态 | 含义 |
|---|---|
| ⏳ 未开始 | 尚未进入 |
| 🔄 进行中 | 正在做 |
| ✅ 完成 | 验收通过 |
| ❌ 放弃/否定 | 实验否定, 记录于 research/log |
