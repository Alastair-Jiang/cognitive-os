# LOG-2026-08-19-D2-SPECS — D-2 关闭: 规格-配置一致性校验 + 仓库卫生门禁

- **类型**: 工程化收口(E0 遗留债务 D-2 闭合 + D-6 前置卫生门禁)
- **范围**: `scripts/check_specs_consistency.py`(新增)、
  `scripts/hygiene_scan.py`(新增)、`tests/test_specs_consistency.py`(新增,
  6 例)、`tests/test_hygiene_scan.py`(新增, 12 例)、
  `research/benchmarks/BM-001*.md`(§2 默认参数修正 + 修正注记)、
  `.github/workflows/ci.yml`(两个校验 step 挂入门禁)

## Problem / 背景

- D-2(engineering_plan §1): BM-001 §2 声明默认参数与 `configs/benchmark.small.json`
  漂移——文档写 `n_topics=8, topics_per_event=3, within_event_noise=0.25`,
  配置实为 `5/4/0.5`。规格与配置二义, 复现时以哪个为准不可判定;
- 无卫生门禁: D-6 的 CI 只有 ruff + pytest, 拆词乱码/零宽字符/失效路径引用
  这类落地损坏(EXP-003 曾发生 14+ 处)不会被 CI 拦截, 只能靠人工事后发现。

## Change(交付一项一项)

1. **`scripts/check_specs_consistency.py`**(纯 stdlib, ~120 行):
   自动解析 BM-001 文档中「默认参数(configs/*.json):」反引号块, 与同名
   config 的 corpus 段逐 key 对比; 数值容差(100 == 100.0); 漂移逐条列出
   并退出码 1; 支持 `--doc` / `--configs-dir` / `--verbose`;
2. **BM-001 §2 修正**: 文档旧值 `8/3/0.25` → 配置实况 `5/4/0.5`
   (small.json 是 EXP-001/002/003 实际运行基准, §7.1 歧义扫描亦为 n_topics=5;
   以配置为准, 文档加修正注记, 不静默改配置);
3. **`scripts/hygiene_scan.py`**(纯 stdlib, ~140 行): 全仓库五类卫生扫描——
   ZW 零宽字符 / ENTITY .py 内 HTML 实体 / SPLIT 拆词乱码(白名单过滤自然词) /
   PATH 反引号路径存在性(包内相对路径与计划文件豁免) / STRAYBT 字母`字母
   拆断(ASCII 限定, 中文代码跨度不误报); 任何 finding 退出码 1;
4. **测试**: specs 6 例(单行/跨行块解析、多配置档、数值容差、端到端漂移检出
   退出码、一致通过、缺配置报告); hygiene 12 例(五类检出 + 中文跨度/自然
   短语/已存在路径/干净文件不误报);
5. **CI 门禁**: `.github/workflows/ci.yml` 在 ruff 后新增
   `check_specs_consistency.py` + `hygiene_scan.py` 两步(三 Python 版本矩阵),
   规格漂移与卫生损坏在 PR 阶段拦截, 零容忍。

## 验证

- 修复前: 校验器准确检出 3 处漂移(n_topics/topics_per_event/within_event_noise);
- 修复后: 零漂移, exit 0;
- hygiene 扫描 90 文件(含全部新增) 0 异常; 自命中问题已处理
  (扫描器 docstring 实体示例改用 `& 符 + gt;` 描述, 测试 fixture 用 chr 构造,
  STRAYBT 限 ASCII 防中文代码跨度误报);
- pytest 87/87(基线 68 + 新增 19); ruff 全绿(E/F/I/N/W/UP, line-length 100);
- 冒烟: 两脚本 `--help` 正常, 全量扫描 < 1s。

## Next Step

1. **D-5/D-3 尾**: runner 公共化 + 结果 JSON 增补 config_hash/code_sha
   (本校验器正是 config_hash 的前置: 配置先归一化才有哈希基准);
2. **hygiene 路径豁免清单**: 若 E1 起新增"计划中文件"引用增多, PATH 豁免
   前缀需随 repo_inventory 计划资产表同步维护;
3. **覆盖率门禁(D-6 主体)**: ratchet 机制, 先于 E1 大重构落地, 防回归。