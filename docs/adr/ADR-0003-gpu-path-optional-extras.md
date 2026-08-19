
# ADR-0003: GPU 路径走可选 extras，零依赖红线限定核心 stdlib 路径

- **状态**: Proposed（2026-08-19 注册；E1 三协议 + GPU 适配器落地并附行为等价证明后转 Accepted）
- **日期**: 2026-08-19
- **上下文**: 研究主旨变更为「用外接显卡（≤15 GiB VRAM 可用）进行大规模计算」。
  ADR-0002 零依赖红线禁止 torch/faiss 类重依赖进入核心；而真嵌入模型
  （BGE-M3 级，fp16 权重约 1.2 GiB）与 GPU ANN 索引（flat-fp32：百万级
  1024 维向量约 4 GiB）都离不开它们。D-9 的 O(N²) 暴力索引规模上限也只有
  GPU ANN 才能解锁。

## 决策

1. **红线范围收窄而非放弃**: `src/cognitive_os/` 默认导入路径维持
   纯标准库（ADR-0002 原文不变）；GPU 路径以**可选 extras** 引入
   （安装目标 cognitive-os[gpu]，候选栈 torch + transformers +
   faiss-gpu；无 GPU 环境的备选 ONNX Runtime + faiss-cpu）。
2. **接入点 = E1 三协议**（ADR-0001）: GPU 栈只实现
   Embedder（真模型推理）与 Index（GPU ANN）两个协议适配器，
   不穿透策略层——三策略源码不 import 任何 GPU 依赖（可用 grep 验证）。
3. **VRAM 预算是硬闸门**: 稳态显存预算 12 GiB（卡上 15 GiB，留 ≥3 GiB
   给驱动/碎片）；预算值写入 GPU 线配置（E1 落地时新增），运行器启动时
   预检 `nvidia-smi`，超线即拒绝运行（fail 而非降速）。
4. **模型本地锁定**: 嵌入模型离线下载、SHA256 钉死后入仓外缓存；
   运行期零联网。
5. **CI 不装 GPU**: stdlib-only 门禁保持全绿；GPU 实验离线跑，
   遥测落 `research/results/` JSON。GPU 不可用时该实验记
   INCONCLUSIVE，不装死也不造假。
6. **成本诚实口径扩编**（宪法 §3 延伸）: 原 3 计数器之外新增
   gpu_mem_peak_mb / embed_tokens / embed_ms / index_build_ms /
   knn_ms，与旧计数器同权重落盘，禁止只报好看的。

## 理由

- 不动红线就无法保住「零依赖核心可在任何机器复现」的下限；不动 GPU
  就无法兑现 15 GiB 算力主旨——协议插拔是同时满足两者的唯一路径；
- 先例: EXP-001 复跑等价护栏（ADR-0001）要求行为等价证明，本 ADR
  沿用同一验证哲学: GPU 适配器落地时，恒等 Embedder + 暴力 Index
  走新协议路径复跑 EXP-001，聚合指标须一致——协议换壳不换行为。

## 后果

- **正面**: D-9 规模上限解锁（目标 10³–10⁶ 碎片）；真嵌入令结论向真实
  信息空间靠近一步；GPU 遥测把「大量计算」变成可审计的账本。
- **负面/代价**: 双栈维护（stdlib 核心 + GPU extras）；行为等价证明
  的测试成本；模型文件不入仓带来的复现步骤（SHA256 清单）。
- **不可逆点**: 结果 JSON 一旦引用协议/嵌入器版本号，其字段语义冻结。

## 关联

`docs/adr/ADR-0001-corpus-embedder-index-protocols.md`；
`docs/adr/ADR-0002-zero-dependencies.md`；
`docs/engineering_plan.md` E1；
`research/experiments/EXP-006-real-embedder-parity.md`。
