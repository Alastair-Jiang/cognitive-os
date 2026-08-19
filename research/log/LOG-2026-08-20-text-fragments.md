## LOG-2026-08-20-text-fragments — E0.5 文本碎片语料发生器

- 状态: 完成
- 关联: EXP-006 前置 2/3, H-006, ADR-0003, E1 协议层(2fbbe42)

### Problem
EXP-006 需要把语料从「合成恒等嵌入」换成「真文本碎片 + GPU 嵌入」,
预注册要求发生器参数与 `configs/benchmark.small.json` 同源——
此前的合成语料把向量直接生成为主题插值, 没有文本层, 真嵌入无料可嵌。

### Hypothesis
以独立模块复刻旧语料的结构纪律(事件主题集 / 主来源 / 时间窗 /
因果链 / 提及抽取, 参数一一对应, 仅去掉 embed_dim 与 index_top_m
两个表示层字段), 碎片以中文模板文本产出(主题句 + 事件谓词句 +
因果链提及句): 事件实体与谓词锚定事件内相似度, 跨事件共享主题词
制造重叠, within_event_noise 以词表外干扰词注入噪声——即可在不触碰
冻结语料代码的前提下, 给 GPU 嵌入路径提供同分布族的文本语料。

### Change
- 新增 `src/cognitive_os/datasets/text_fragments.py`:
  TextFragmentConfig(13 字段, 与 SyntheticCorpusConfig 同名对齐) +
  TextFragmentCorpus(两遍生成: 事件层到碎片层; 查询接口镜像旧语义);
- 新增 `tests/test_text_fragments.py`: 8 个测试(结构计数 / 配置同族
  守护 / 确定性 / 文本分层 / 因果提及 / 查询语义 / 截断可观测 /
  结构黄金哈希);
- 文档: 盘点表 +1 行, CHANGELOG 双语, 各处测试计数 96 更新为 104。

### Experiment
纯工程轮(无运行实验)。验证链: 落盘脚本自校验(编译 / ZW / 实体) 到
pytest 全量到卫生扫描; 任一失败整体回退。

### Result
- pytest **104/104** 通过(4.04s, 96 + 8 新增);
- 结构黄金哈希(seed=20260819): sha256=13f34914...66dbec(测试钉死,
  生成端任何无意变动即刻红);
- 卫生扫描 **121 文件 0 异常**。

### Interpretation
文本层就位后, EXP-006 的语料管线只剩嵌入段: 文本到 BGE-M3 向量到
协议层 CorpusView(嵌入 / 索引协议已由 E1 落地)。半径与语义阈值的真嵌入
标定留给 EXP-006 预检(先记录相似度统计再检索, 不预设结论)。

### Next Step
1. EXP-004a 运行器(R2, G1 闸门 0.03, λ=0.02 冻结);
2. GPU 栈 extras + BGE-M3 SHA256 清单 + VRAM 预检;
3. EXP-006 运行器。
