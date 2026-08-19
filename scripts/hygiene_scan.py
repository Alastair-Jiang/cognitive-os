"""仓库文件卫生扫描: 四类落地损坏 + stray backtick, 全仓库零容忍。

对应 `OPENCLAW.md` §2.6 文件卫生(四类) + EX`P` 类 stray backtick(补充):
1. ZW     — 零宽字符(U+200B);
2. ENTITY — .py 文件内 HTML 实体字面量(& 符紧跟 gt; / lt; / amp; 的连写);
3. SPLIT  — 英文词被空格拆断的拆词乱码(连续 1–2 字母小写 token,
           白名单过滤自然短词), 如 `ov er la p` 应为 `overlap`;
4. PATH   — 反引号引用的仓库相对路径不存在(glob/纯文件名/计划文件豁免);
5. STRAYBT — 字母`字母 的 stray backtick(代码跨度被拆坏), 如 EX`P-003`。

任何 finding → 打印 `TYPE rel:line: 描述` 并以退出码 1 结束(可挂 CI)。
用法:
    python scripts/hygiene_scan.py                 # 全仓库扫描
    python scripts/hygiene_scan.py --verbose       # 含扫描文件清单
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ZW = "\u200b"
_BT = "`"
ENTITIES = ["&" + "gt;", "&" + "lt;", "&" + "amp;"]
SPLIT_RE = re.compile(r"\b(?:[a-z]{1,2} ){2,}[a-z]{1,2}\b")
PATH_RE = re.compile(r"`([A-Za-z0-9_.\-/]+\.(?:py|json|md|toml|yml|yaml|txt|sh|cfg|ini))`")
# 自然语言中的合法短词(拆词乱码误报白名单)
OKALIAS = {
    "a", "an", "as", "at", "be", "by", "do", "e", "g", "i", "if", "in", "is",
    "it", "me", "my", "no", "of", "on", "or", "q", "so", "to", "up", "we",
}
# 反引号路径豁免: 计划中/未来文件(尚未存在但文档已引用), 或包内相对写法
PATH_EXEMPT_PREFIX = ("check_specs", "adr-", "ADR-")
PATH_EXEMPT_GLOB = ("*", "{", "[", "?")


def scan_file(
    path: Path, rel: Path, findings: list[tuple[str, str, str]], root: Path | None = None
) -> None:
    """扫描单个文件; root 用于反引号路径存在性判断(默认仓库根)。"""
    root = root or REPO
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        findings.append(("DECODE", str(rel), "非 UTF-8 文本"))
        return
    except OSError as exc:
        findings.append(("READ", str(rel), f"读取失败: {exc}"))
        return

    # 1) 零宽字符
    if ZW in text:
        findings.append(("ZW", str(rel), f"零宽字符 U+200B x{text.count(ZW)}"))

    suffix = path.suffix
    lines = text.splitlines()

    # 2) .py 内 HTML 实体字面量
    if suffix == ".py":
        for n, line in enumerate(lines, 1):
            for ent in ENTITIES:
                if ent in line:
                    findings.append(("ENTITY", f"{rel}:{n}", f"HTML 实体 {ent}"))
        return  # .py 不查 markdown 类检查

    if suffix not in {".md", ".txt"}:
        return

    # 3) 拆词乱码
    for n, line in enumerate(lines, 1):
        for m in SPLIT_RE.finditer(line):
            toks = m.group(0).split(" ")
            if any(t not in OKALIAS for t in toks):
                findings.append(("SPLIT", f"{rel}:{n}", repr(m.group(0))))

    # 4) 反引号路径不存在
    for n, line in enumerate(lines, 1):
        for m in PATH_RE.finditer(line):
            tok = m.group(1)
            if any(tok.startswith(p) for p in PATH_EXEMPT_PREFIX):
                continue
            if any(ch in tok for ch in PATH_EXEMPT_GLOB):
                continue
            if "/" not in tok:
                continue  # 纯文件名(可能是任意位置的包文件), 弱检查跳过
            cand = root / tok
            if cand.exists():
                continue
            # 包内相对路径惯例: docs 常以 src/cognitive_os 为根
            if (root / "src" / "cognitive_os" / tok).exists():
                continue
            findings.append(("PATH", f"{rel}:{n}", f"反引号路径不存在: `{tok}`"))

    # 5) stray backtick(仅 ASCII 字母; 中文代码跨度如 `runner 库` 是合法写法)
    for n, line in enumerate(lines, 1):
        for j in range(len(line) - 2):
            a, b = line[j], line[j + 2]
            if (
                a.isascii()
                and b.isascii()
                and a.isalpha()
                and line[j + 1] == _BT
                and b.isalpha()
            ):  # noqa: E501
                findings.append(
                    ("STRAYBT", f"{rel}:{n}", f"字母被反引号拆断: {line[max(0, j-4):j+7]!r}")
                )


def main() -> None:
    ap = argparse.ArgumentParser(description="仓库文件卫生扫描(四类 + stray backtick)")
    ap.add_argument("--root", default=str(REPO), help="扫描根目录")
    ap.add_argument("--verbose", action="store_true", help="输出扫描文件清单")
    args = ap.parse_args()

    root = Path(args.root)
    findings: list[tuple[str, str, str]] = []
    n_files = 0
    for f in sorted(root.rglob("*")):
        rel = f.relative_to(root)
        if any(p.startswith(".") for p in rel.parts):
            continue
        if "node_modules" in rel.parts or ".git" in rel.parts:
            continue
        if f.suffix not in {".py", ".md", ".json", ".toml", ".yml", ".yaml", ".txt"}:
            continue
        n_files += 1
        if args.verbose:
            print(f"  scan {rel}")
        scan_file(f, rel, findings)

    print(f"[hygiene-scan] 扫描 {n_files} 个文件, 发现 {len(findings)} 处异常")
    for kind, loc, msg in findings:
        print(f"  {kind:<8} {loc}: {msg}")

    if findings:
        print("\n❌ 卫生检查未通过, 修复后重跑(不得豁免)")
        raise SystemExit(1)
    print("✅ 仓库卫生干净(零宽/实体/拆词/路径/stray backtick 全部为零)")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
