"""卫生扫描器测试: 五类损坏均能检出, 干净仓库零 finding。"""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from hygiene_scan import scan_file  # noqa: E402


def _scan(tmp_root: Path, rel: str, content: str) -> list[tuple[str, str, str]]:
    """在临时根下写文件并扫描, 返回 findings。"""
    p = tmp_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    findings: list[tuple[str, str, str]] = []
    scan_file(p, p.relative_to(tmp_root), findings, root=tmp_root)
    return findings


class TestHygieneScan(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_zero_width_detected(self):
        f = _scan(self.root, "a.md", "hello\u200bworld")
        self.assertTrue(any(k == "ZW" for k, _, _ in f))

    def test_html_entity_in_py_detected(self):
        # 用 chr 构造避免源码字面命中扫描器自身
        entity = chr(38) + "gt;"
        f = _scan(self.root, "s.py", f"x = 'a {entity} b'")
        self.assertTrue(any(k == "ENTITY" for k, _, _ in f))

    def test_html_entity_in_md_allowed(self):
        # markdown 里 & 符 + gt; 是合法转义(防 blockquote), 不查
        entity = chr(38) + "gt;"
        f = _scan(self.root, "a.md", f"C {entity} A")
        self.assertFalse(any(k == "ENTITY" for k, _, _ in f))

    def test_split_words_detected(self):
        f = _scan(self.root, "a.md", "ov er la p-mi d 是格点")
        self.assertTrue(any(k == "SPLIT" for k, _, _ in f))

    def test_common_english_not_flagged(self):
        f = _scan(self.root, "a.md", "to be or not to be, that is the question")
        self.assertFalse(any(k == "SPLIT" for k, _, _ in f))

    def test_missing_path_detected(self):
        f = _scan(self.root, "a.md", "见 `src/cognitive_os/not_exist.py`")
        self.assertTrue(any(k == "PATH" for k, _, _ in f))

    def test_existing_path_ok(self):
        (self.root / "src" / "cognitive_os").mkdir(parents=True)
        (self.root / "src" / "cognitive_os" / "stats.py").write_text("", encoding="utf-8")
        f = _scan(self.root, "a.md", "见 `src/cognitive_os/stats.py`")
        self.assertFalse(any(k == "PATH" for k, _, _ in f))

    def test_stray_backtick_detected(self):
        f = _scan(self.root, "a.md", "详见 EX`P-003` 文档")
        self.assertTrue(any(k == "STRAYBT" for k, _, _ in f))

    def test_chinese_code_span_not_flagged(self):
        # `runner 库` 这类中文代码跨度是合法写法, 不报
        f = _scan(self.root, "a.md", "把 `runner 库` 公共化")
        self.assertFalse(any(k == "STRAYBT" for k, _, _ in f))

    def test_clean_file_zero_findings(self):
        (self.root / "src" / "cognitive_os").mkdir(parents=True)
        (self.root / "src" / "cognitive_os" / "stats.py").write_text("", encoding="utf-8")
        f = _scan(
            self.root,
            "a.md",
            "干净文档, 引用 `src/cognitive_os/stats.py` 与 EXP-003。\n> 引用块",
        )
        self.assertEqual(f, [])


if __name__ == "__main__":
    unittest.main()
