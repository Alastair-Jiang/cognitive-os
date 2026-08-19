
## LOG-2026-08-19-gpu-line-prereg — GPU 线立项预注册（ADR-0003 / H-006 / EXP-006）

- 状态: 完成
- 关联: ADR-0001/0002/0003, H-006, EXP-006, E1

### Problem
研究主旨变更为「外接显卡（可用显存 ≤15 GiB）进行大规模计算」。三条既有
约束同时受压: ADR-0002 零依赖红线禁止重依赖入核心；D-9 暴力索引锁死语料
规模；EXP-001/003 的结论全部建立在合成恒等嵌入上、离真实信息空间一步之遥。
需要一个不破坏既有纪律的 GPU 接入方案与第一条 GPU 实验。

### Hypothesis
用「可选 extras + E1 三协议插拔」接入 GPU（红线只收窄不放弃），并以
「换真嵌入平价复核」作为 GPU 线第一实验（H-006 四分量），可以同时:
解锁规模（D-9）、让结论靠近真实嵌入、且不触碰任何已冻结预注册
（EXP-004/005 原栈原样）。

### Change
- 新增 `docs/adr/ADR-0003-gpu-path-optional-extras.md`（Proposed）:
  红线收窄、协议插拔、VRAM 12 GiB 硬闸门、模型 SHA256 锁定、CI 不装
  GPU、成本口径扩编六条决策；
- 新增 `research/hypotheses/H-006-real-embedder-parity.md`
  （UNVALIDATED，四分量 a/b/c/d，各自可证伪）；
- 新增 `research/experiments/EXP-006-real-embedder-parity.md`
  （预注册冻结: 前置三项、5 固定 seed、P1–P4 判据、四闸门口径沿用
  `decide()`、GPU 遥测五件套、INCONCLUSIVE 护栏）；
- `docs/repo_inventory.md` 增 H-006/EXP-006/ADR-0003 三行；
- `CHANGELOG.md` / `CHANGELOG.zh.md` Added 双语条目；
- 本日志。

### Experiment
纯文档轮（无代码、无运行）。验证链: 落盘经 D() 方法脚本（抗网关注入）
+ 锚点唯一性自检；`python scripts/hygiene_scan.py` 退出码 0
（新文件反引号路径全部真实存在）；`python -m pytest tests/ -q`
维持 87/87。

### Result
锚点自检 4/4 唯一命中、ZW 零检出后写入；提交前复验:
`python scripts/hygiene_scan.py` 扫描 109 文件 0 异常（退出码 0）；
`python -m pytest tests/ -q` 87/87 通过（2.37s）。纯文档轮，代码路径
零改动。

### Interpretation
本轮回填了「GPU 主旨 → 仓库纪律」的完整投影: 决策（ADR）、假设（H-006）、
预注册（EXP-006）、盘点与变更记录五层齐备，且明确宣示 EXP-004/005 预注册
一个字不动。GPU 线与旧栈并行，互不前置——排程纪律延续。

### Next Step
1. E1 三协议实现 + 行为等价证明（复跑 EXP-001 聚合指标一致）；
2. 文本碎片语料发生器（参数同 small 档）；
3. GPU 栈 extras 安装目标 + VRAM 预检脚本 + BGE-M3 SHA256 清单；
4. 以上三项齐备后运行 EXP-006，按四分量三态回填。
