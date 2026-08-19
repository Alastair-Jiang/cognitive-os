"""D-2 一致性校验: BM-001 规格文档声明的默认参数 vs configs/*.json 零漂移。

对应 `docs/engineering_plan.md` §1 D-2: BM-001 §2 声明参数与配置文件漂移
(实测 n_topics/topics_per_event/within_event_noise 三处不一致, 2026-08-19)。

校验规则:
- 从 BM-001 规格文档提取「默认参数(configs/<name>.json):」之后反引号
  代码块中的 key=value 列表;
- 与同名 `configs/<name>.json` 的 corpus 段逐 key 对比;
- 数值比较容忍类型差异(100 == 100.0), 字符串按字面;
- 任何漂移 → 逐条列出并退出码 1(可挂 CI 门禁, 漂移零容忍)。

用法:
    python scripts/check_specs_consistency.py            # 校验全部声明
    python scripts/check_specs_consistency.py --verbose  # 含通过项明细
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DOC = REPO / "research" / "benchmarks" / "BM-001-synthetic-event-reconstruction.md"

# key=value 对(整数/浮点; key 为下划线小写标识符)
_KV_RE = re.compile(r"\b([a-z][a-z0-9_]*)=(\d+(?:\.\d+)?)\b")


def find_declared_blocks(md_text: str) -> dict[str, dict[str, float | int]]:
    """提取文档中所有「默认参数(configs/X.json):」声明块。

    返回 {config 文件名: {参数名: 值}}。声明块 = 紧跟该行的反引号代码块
    (可跨行, 到闭合反引号结束)。
    """
    blocks: dict[str, dict[str, float | int]] = {}
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        m = re.search(r"默认参数\(configs/([\w.\-]+\.json)\)", lines[i])
        if m:
            # 收集从下一行开始的反引号块(可能起始于当前行行尾)
            chunk = lines[i]
            j = i + 1
            while "`" not in chunk or chunk.count("`") < 2:
                if j >= len(lines):
                    break
                chunk += "\n" + lines[j]
                j += 1
            # 去掉外围反引号, 收集 key=value
            values: dict[str, float | int] = {}
            for k, v in _KV_RE.findall(chunk):
                values[k] = float(v) if "." in v else int(v)
            if values:
                blocks[m.group(1)] = values
            i = j
        else:
            i += 1
    return blocks


def load_corpus(cfg_path: Path) -> dict[str, object]:
    """读取 config JSON 的 corpus 段(缺失返回空 dict)。"""
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FATAL: 无法读取配置 {cfg_path}: {exc}") from exc
    return data.get("corpus", {})


def num_eq(a: object, b: object) -> bool:
    """数值等价(100 == 100.0 / 1 == 1.0), 否则字面比较。"""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return float(a) == float(b)
    return a == b


def check_doc_against_config(
    cfg_name: str,
    declared: dict[str, float | int],
    corpus: dict[str, object],
    verbose: bool,
) -> list[str]:
    """单文件校验, 返回漂移描述列表(空 = 通过)。"""
    diffs: list[str] = []
    for key, doc_val in sorted(declared.items()):
        cfg_val = corpus.get(key)
        if cfg_val is None:
            diffs.append(f"{cfg_name}: 文档声明 `{key}={doc_val}` 但配置中不存在")
            continue
        if not num_eq(doc_val, cfg_val):
            diffs.append(
                f"{cfg_name}: `{key}` 漂移 — 文档={doc_val}, 配置={cfg_val}"
            )
        elif verbose:
            print(f"  ok  {cfg_name}: {key}={doc_val}")
    for key in sorted(set(corpus) - set(declared)):
        if verbose:
            print(f"  --  {cfg_name}: 配置额外字段 `{key}`(文档未声明, 不校验)")
    return diffs


def main() -> None:
    ap = argparse.ArgumentParser(description="BM-001 声明参数与 configs/*.json 一致性校验")
    ap.add_argument("--doc", default=str(DEFAULT_DOC), help="规格文档路径")
    ap.add_argument("--configs-dir", default=str(REPO / "configs"), help="配置文件目录")
    ap.add_argument("--verbose", action="store_true", help="输出通过项明细")
    args = ap.parse_args()

    doc_path = Path(args.doc)
    if not doc_path.exists():
        raise SystemExit(f"FATAL: 规格文档不存在: {doc_path}")
    blocks = find_declared_blocks(doc_path.read_text(encoding="utf-8"))
    if not blocks:
        raise SystemExit("FATAL: 文档中未找到任何「默认参数(configs/*.json):」声明块")
    print(f"[specs-consistency] 文档 {doc_path.name} 声明 {len(blocks)} 个配置档位")

    all_diffs: list[str] = []
    for cfg_name, declared in sorted(blocks.items()):
        cfg_path = Path(args.configs_dir) / cfg_name
        if not cfg_path.exists():
            all_diffs.append(f"{cfg_name}: 声明的配置文件不存在: {cfg_path}")
            continue
        print(f"\n== 校验 {cfg_name} ==")
        corpus = load_corpus(cfg_path)
        all_diffs += check_doc_against_config(cfg_name, declared, corpus, args.verbose)

    if all_diffs:
        print(f"\n❌ 发现 {len(all_diffs)} 处漂移:")
        for d in all_diffs:
            print(f"  - {d}")
        raise SystemExit(1)
    print("\n✅ 全部声明参数与配置一致, 零漂移")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
