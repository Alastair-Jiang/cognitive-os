## LOG-2026-08-19-prereg-corrections — 预注册运行前更正（EXP-004 / EXP-005）

- 状态: 完成
- 关联: H-004, EXP-004, EXP-005, E2

### Problem
两个实验均未运行，预注册文本在对抗性复核中发现 1 处幻觉 + 4 处安排错误:

1. **归属性幻觉**: EXP-005 语料 seed 池写「延续 EXP-003 的 {20260819, 7, 42}
   + 边界扩展」——实际 `scripts/run_exp003_significance.py` 的 --seeds 默认为
   5 个固定值 "20260819,7,42,131,9999"，3+2 是 EXP-004 自有模式；
2. **成本计数失实**: EXP-005 写「五类成本计数」，而 NetSearchStats
   （src/cognitive_os/nets/search_net.py）只有 3 个计数器
   （similarity_calls / index_lookups / candidates_scored）；
3. **度量缺陷**: 有序路径恢复率硬编码 /4（应 /L），且未与既有
   chain_connectivity（`scripts/run_exp002_h003.py`，事后建图层无向成对
   口径，EXP-002 的 0.940 与 0.398/0.294 来源）消歧——不同层、不同定义；
4. **标签漂移风险**: EXP-004b 最优策略标签未冻结 λ，λ 敏感性扫描会漂移
   标签来源，破坏 G2 可比性；
5. **排程倒挂**: EXP-004 Next Step 把 EXP-005 写成「G1 失败后的重心回流」，
   与 E2 既定的并行设计冲突。

另录两项工程债（本轮不改代码，待排期）:

- BM-001 运行器 judgments 仍停 EXP-001 口径（`scripts/run_benchmark.py` 的
  H-003 PASS 条件未随 §7.3 纯度重设计更新，与文档表述并存冲突）；
- 卫生门禁拆词正则仅覆盖小写 1–2 字母 token，大写拆词（如 EXP 被拆为
  EX P）与 ≥3 字母半拆词可逃逸检测。

### Hypothesis
在零运行窗口期更正预注册（git 历史保留原误），可恢复实验可判定性:
seed 纪律与 EXP-003 对齐 → 跨 seed 判定直接可比；度量 /L 广义化 + 消歧
→ 结果不与既有 0.940 口径混淆；标签冻结主 λ=0.02 → G2 不被 λ 漂移污染；
排程更正 → 研究路线不被单一实验结果绑架。

### Change
- `research/experiments/EXP-005-cited-expansion.md`: seed 池（对齐 5 固定值，
  内含更正说明）、逐查询记录成本计数（对齐 3 计数器，含更正说明）、度量表
  /L 广义化 + 有序恢复 vs 连通率消歧、文末预注册声明（列出更正条目 ①②③）；
- `research/experiments/EXP-004-adaptive-strategy-selection.md`: 004b 检验
  方式段冻结标签 λ=0.02（含更正说明）、Next Step 排程纪律改写（EXP-005
  并行、不依赖 G1 失败）；
- `docs/repo_inventory.md`: EXP-005 行状态附注更正要点；
- `CHANGELOG.md` / `CHANGELOG.zh.md`: Fixed 段新增更正条目（含两项工程债）；
- 本日志文件。

### Experiment
验证步骤（仅文档更正，无代码路径变动）:

1. 编辑锚点唯一性自检（脚本拒写条件: 锚点非唯一 / 命中 U+200B）；
2. 仓库卫生门禁复扫 `python scripts/hygiene_scan.py` 退出码 0（0 findings）；
3. 全量测试 `python -m pytest tests/ -q` 维持 87/87。

### Result
锚点自检 9/9 唯一命中、ZW 零检出后写入；提交前复验:
`python scripts/hygiene_scan.py` 扫描 103 文件 0 异常（退出码 0）；
`python -m pytest tests/ -q` 87/87 通过（2.29s）。文档改动未触及任何
代码路径，门禁与测试维持全绿。

### Interpretation
更正不触碰任何已落盘结论（EXP-001/002/003 结果与 H-001/H-002/H-003 状态
不动）。暴露的系统性经验: 预注册文本落成后需要一步「对抗复核」——
seed 归属、计数器真实性、度量消歧、λ 锁定、排程前后置——作为惯例比
运行后 corrigendum 便宜一个数量级。

### Next Step
1. 把对抗复核清单固化为预注册模板核对项（或并入 OPENCLAW 工作循环）；
2. 工程债排期: BM-001 运行器 judgments 升级至 §7.3 口径（或显式冻结旧
   口径并在文档记录）；卫生拆词正则扩展（大写拆词 / ≥3 字母半拆词）+
   配套单测；
3. EXP-004a（R2）与 E2 工程前置（SearchNet 引用通道、计数器口径落地、
   有序路径恢复度量黄金值单测）并行启动。
