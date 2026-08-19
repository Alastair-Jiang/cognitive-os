# REPORT-2026-08-19 — D-2 收口: 规格-配置一致性门禁 + 仓库卫生扫描

- **日期**: 2026-08-19
- **执行**: OpenClaw(LiGuiyu-AI), 按 `OPENCLAW.md` 工作提示词自主推进
- **关联**: `docs/engineering_plan.md` §1(D-2/D-6)、PR #6(merged `9ea17d9`)
- **状态**: ✅ 完成

---

## 1. 任务背景

`docs/engineering_plan.md` E0 阶段遗留七项工程债(D-1 ~ D-7)。按 `OPENCLAW.md`
§5 的优先级排序, 本轮交付 **D-2**: BM-001 规格文档声明的默认参数与
`configs/*.json` 实际配置漂移, 导致"复现实验以哪个为准"不可判定。

顺带落地 D-6 的前置: 仓库**卫生门禁**(五类落地损坏扫描)——EXP-003 曾发生
14+ 处拆词乱码, 只靠人工事后发现, CI 不拦截。

## 2. 发现的问题(实测)

| 参数 | BM-001 §2 文档声明 | `configs/benchmark.small.json` 实况 | 判定 |
|---|---|---|---|
| `n_topics` | 8 | **5** | ❌ 漂移 |
| `topics_per_event` | 3 | **4** | ❌ 漂移 |
| `within_event_noise` | 0.25 | **0.5** | ❌ 漂移 |
| 其余 8 项 | — | — | ✅ 一致 |

修复前, 校验器(本次新写)精确检出以上 3 处漂移。

## 3. 解决方案

### 3.1 `scripts/check_specs_consistency.py`(新增, 纯 stdlib)

- 自动解析 BM-001 文档中「默认参数(configs/*.json):」反引号声明块;
- 与同名 `configs/*.json` 的 `corpus` 段逐 key 对比, **数值容差**
  (`100 == 100.0`), 字符串字面比较;
- 任何漂移 → 逐条列出并 `exit 1`(CI 门禁, 零容忍);
- 可配置 `--doc` / `--configs-dir` / `--verbose`;

### 3.2 BM-001 §2 文档修正(先报告后修, 不静默改配置)

- 配置 `5/4/0.5` 是 EXP-001/002/003 **实际运行基准**(§7.1 歧义扫描亦为
  `n_topics=5`), 文档旧值 `8/3/0.25` 是过时文本 → **以配置为准修文档**;
- 文档内附修正注记(何时修、为什么以配置为准、由谁持续校验)。

### 3.3 `scripts/hygiene_scan.py`(新增, 纯 stdlib)

全仓库五类落地损坏扫描(对 `OPENCLAW.md` §2.6 的四类 + stray backtick):

| 类 | 检查 | 示例 |
|---|---|---|
| ZW | 零宽字符 U+200B | `hello\u200bworld` |
| ENTITY | .py 内 HTML 实体字面量 | `'a &gt; b'` |
| SPLIT | 拆词乱码(英文词被空格拆断) | `ov er la p` → `overlap` |
| PATH | 反引号引用的仓库路径不存在 | `` `src/not_exist.py` `` |
| STRAYBT | 字母被反引号拆断(仅 ASCII) | `EX`P-003`` |

误报防护: 自然短词白名单(`to be or not` 不报)、markdown 合法
`&gt;` 转义不查、中文代码跨度 `` `runner 库` `` 不报、包内相对路径惯例豁免。

### 3.4 测试(基线 68 → 87/87)

- `tests/test_specs_consistency.py`(6 例): 声明块解析(单行/跨行/多配置)、
  数值容差、端到端退出码(漂移→1 / 一致→0 / 缺配置→1);
- `tests/test_hygiene_scan.py`(12 例): 五类均能检出 + 四类误报防护全过;
- 扫描器"自命中"问题已处理(示例文本用 `chr(38)` 构造, 不污染源码)。

### 3.5 CI 门禁

`.github/workflows/ci.yml` 三 Python 版本矩阵, 在 ruff 后新增两步:

```yaml
- run: python scripts/check_specs_consistency.py
- run: python scripts/hygiene_scan.py
```

规格漂移与卫生损坏在 PR 阶段拦截, **零容忍、无豁免**。

## 4. 验证结果(完整验证链)

| 检查 | 结果 |
|---|---|
| `ruff check .` | ✅ 全绿(E/F/I/N/W/UP, line-length 100) |
| `pytest` | ✅ **87/87**(基线 68 + 新增 19) |
| `hygiene_scan.py` | ✅ 91 文件 0 异常 |
| `check_specs_consistency.py` | ✅ 零漂移 |
| 冒烟 | ✅ 两脚本 `--help` 正常; 全量扫描 < 1s |
| CI(PR #6) | ✅ 3.10 / 3.11 / 3.12 三版本全绿 |

## 5. 交付物清单

| 文件 | 类型 | 说明 |
|---|---|---|
| `scripts/check_specs_consistency.py` | 新增 | D-2 校验器(纯 stdlib) |
| `scripts/hygiene_scan.py` | 新增 | 五类卫生扫描(纯 stdlib) |
| `research/benchmarks/BM-001-*.md` | 修改 | §2 默认参数修正 + 注记 |
| `.github/workflows/ci.yml` | 修改 | +2 门禁 step |
| `tests/test_specs_consistency.py` | 新增 | 6 例 |
| `tests/test_hygiene_scan.py` | 新增 | 12 例 |
| `CHANGELOG.md` / `.zh.md` | 修改 | Unreleased 双语条目 |
| `docs/repo_inventory.md` | 修改 | 管线/测试表同步 |
| `research/log/LOG-2026-08-19-d2-specs-consistency.md` | 新增 | 工程日志 |

## 6. 后续(按 OPENCLAW.md §5)

1. **D-5/D-3 尾**: `scripts/` runner 公共化(消除三份复制) + 结果 JSON 增补
   `config_hash`/`code_sha`——本校验器正是 config_hash 的前置
   (配置先归一化才有哈希基准);
2. **E1 检索核心抽象化**: Corpus/Embedder/Index 三协议, 行为等价证明
   (EXP-001 复跑聚合指标与历史一致), 回填 ADR-0001;
3. **D-6 主体**: 覆盖率门禁(ratchet 机制, 只升不降)。

---

*由 🦞 桂鱼养的龙虾 生成 · 2026-08-19 · 数据与结论可在仓库中复现*