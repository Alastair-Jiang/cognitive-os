## LOG-2026-08-20-e2-cite-channel — E2 前置: 引用扩张通道 + /L 度量

- 状态: 完成
- 关联: EXP-005 预注册(冻结), H-004, E1 协议层, BM-001 §7.3

### Problem
EXP-005 要把引用边作为检索**扩张通道**(而非事后建图)。预注册 §前置工程
三项: ① SearchNet 引用扩张通道(可配置开关, 独立计费); ② 成本计数器
口径(扩张步计 index_lookups); ③ 有序路径恢复率 /L 度量 + 黄金值可手算的
单元测试(先于实验运行落盘, E2 DoD)。

### Hypothesis
工程前置, 无可证伪假设; 判定归属 EXP-005 G1/G2。

### Change
- protocols.py: Corpus 协议增 mentions(加性; SyntheticEventCorpus 与
  CorpusView 均天然满足);
- search_net.py: SearchNetConfig.cite_expansion(默认 False, 向后兼容);
  search() 每跳前沿对 mentions(pid) 拉入硬结构候选——豁免语义半径与来源
  门槛(引用=确定性结构信号, evidence_graph 先例), 计费: 每引用拉取
  index_lookups += 1, 计分 similarity_calls += 1;
- metrics.py: ordered_path_recovery(链的最长相邻有序子路径长 / L,
  全链平均), 与 chain_connectivity(无向成对连通)分层消歧;
- tests/test_cite_channel.py: 5 测试(黄金值手算对照 + 均值 + 协议一致性
  + 引用拉取豁免半径 + 计费差异)。

### Experiment
纯工程轮(无运行实验)。验证链: 落盘编译到导入到 pytest 到卫生扫描。

### Result
- pytest 118/118(113 + 5 新增);
- 黄金值手算对照: 3/4=0.75, 1/4=0.25, 2/4=0.5, 0, 2/4=0.5(全过);
- 引用通道在半径 0.999 下仍拉入被引用碎片; 计费 index_lookups 增加;
- 卫生扫描 127 文件 0 异常(本 LOG 落盘后计数)。

### Interpretation
B'/C' 可由运行器对冻结策略模板深拷贝并置 cite_expansion=True 构造
(A/B/C 原样不动, 不新增策略类, 满足预注册「实验模块不替换」)。/L 度量
与 chain_connectivity 分层消歧, 供 EXP-005 G1 主判定使用。

### Next Step
1. EXP-005 运行器(五臂 A/B/B'/C'/C' + A-large k'=15, 四闸门 G1-G4);
2. EXP-006 运行器 + GPU 适配器 + VRAM 预检。
