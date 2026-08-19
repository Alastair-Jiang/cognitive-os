## LOG-2026-08-20-e1-protocols — E1 协议层落地 + 行为等价证明

- 状态: 完成
- 关联: ADR-0001/0002/0003, E1, EXP-006/007 前置

### Problem
策略栈(retrieval / nets / anchors)直接 import 具体语料类
SyntheticEventCorpus, 与 ADR-0001「三协议插拔」目标冲突: 真嵌入
(EXP-006)与 ANN 索引(EXP-007)没有接入缝; 且解耦主张无机器验证,
无法回归防退化。

### Hypothesis
以 typing.Protocol 定义最小策略面(四成员: point_ids / get /
embed_seed / neighbors), 策略栈只依赖协议; 用恒等适配器
(IdentityEmbedder + BruteForceIndex + CorpusView)组合出与
具体语料行为完全一致的视图路径: 解耦可由纯度单测机器验证; 行为等价用
「视图路径 vs 直接路径逐字段对账 + 冻结 EXP-001 聚合对账(时延除外)」
证明, 不依赖口头保证。

### Change
- 新增 `src/cognitive_os/protocols.py`: 三协议(Corpus / Embedder /
  Index), 纯标准库, 结构化鸭子类型(旧语料天然满足 Corpus);
- 新增 `src/cognitive_os/adapters/`(identity.py): 恒等适配器 +
  CorpusView(附评估层便利成员 event_of / event_fragments / mentions);
- 解耦编辑: retrieval/base.py、nets/search_net.py、
  anchors/anchor_detector.py 改依赖协议(锚点密度行 points 走
  point_ids, 行为不变); run_benchmark.py 的 build_strategies
  注解放宽为协议;
- 新增测试: test_protocols.py(结构一致 + 逐成员对账 + 三策略跨路径
  逐字段一致 + 运行器接缝)、test_protocol_purity.py(ADR-0001 验收
  条件机器验证)、test_protocol_equivalence.py(小配置全量 + 截断 0.6
  两轮);
- 新增 `scripts/prove_protocol_equivalence.py`: 等价证明脚本, 回执落
  `research/results/`;
- 文档: repo_inventory(+2 行, nets 行状态更新)、CHANGELOG 双语、
  AGENTS / README / project_manual 测试计数 87 到 96。

### Experiment
纯工程轮。验证链: 证明脚本(逐字段对账 + 冻结对账)到 pytest 全量到
卫生扫描, 任何一步失败整体回退不提交。

### Result
- 行为等价证明: 路径差异 **0 处**(12 查询 × 3 策略 × 排序/分数/证据/
  四计数器/早停全部逐字段一致); 冻结对账对 EXP-001 benchmark.small
  k10-q12 冻结聚合 **0 偏差**(1e-12 容差内), 判定 **PASS**; 回执
  `research/results/PROOF-E1-EQUIV-20260820-021634.json`。
- 过程缺陷(如实记录): 首跑冻结对账误选 t0.6 截断文件(非截断 glob
  模式未排除 -t 后缀文件名), 修复为时间戳首字符锚定后复跑 PASS;
  两张误配对象的 FAIL 回执已删除(对账对象错误, 不构成证据)。
- pytest **96/96** 通过(3.54s, 87 + 9 新增)。
- 卫生扫描 **117 文件 0 异常**。

### Interpretation
协议层把「可插拔」从 ADR 文字变成机器约束: 纯度单测守住策略栈不回引
具体语料, 等价证明守住「换壳不换行为」。EXP-006 的 GPU 适配器(真嵌入)
与 EXP-007 的 ANN 索引有了明确落点: 各自实现 Embedder / Index
协议即可, 策略代码零改动。

### Next Step
1. EXP-006 前置: 文本碎片语料发生器(参数同 small 档);
2. GPU 栈 extras + BGE-M3 SHA256 清单 + VRAM 预检;
3. EXP-004a 运行器(R2)。
