"""D-2 校验器测试: 漂移检出 / 一致通过 / 声明块解析 / 数值容差。"""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_specs_consistency import find_declared_blocks, num_eq  # noqa: E402

DOC_TEMPLATE = """# BM-001 test

## 2. 数据集

默认参数(configs/benchmark.small.json):
`{params}`

## 3. 其余
"""


class TestFindDeclaredBlocks(unittest.TestCase):
    def test_single_line_block(self):
        doc = DOC_TEMPLATE.format(params="n_events=12, seed=20260819")
        blocks = find_declared_blocks(doc)
        self.assertEqual(blocks, {"benchmark.small.json": {"n_events": 12, "seed": 20260819}})

    def test_multiline_block(self):
        doc = DOC_TEMPLATE.format(
            params="n_topics=5,\ntopics_per_event=4,\nwithin_event_noise=0.5"
        )
        blocks = find_declared_blocks(doc)
        self.assertEqual(
            blocks,
            {
                "benchmark.small.json": {
                    "n_topics": 5,
                    "topics_per_event": 4,
                    "within_event_noise": 0.5,
                }
            },
        )

    def test_no_block_returns_empty(self):
        self.assertEqual(find_declared_blocks("无声明"), {})

    def test_multiple_declared_configs(self):
        doc = (
            "默认参数(configs/a.json):\n`x=1`\n\n"
            "默认参数(configs/b.json):\n`y=2.5`\n"
        )
        blocks = find_declared_blocks(doc)
        self.assertEqual(blocks, {"a.json": {"x": 1}, "b.json": {"y": 2.5}})


class TestNumEq(unittest.TestCase):
    def test_int_float_equivalence(self):
        self.assertTrue(num_eq(100, 100.0))
        self.assertTrue(num_eq(5, 5.0))
        self.assertFalse(num_eq(5, 5.1))

    def test_string_literal(self):
        self.assertTrue(num_eq("a", "a"))
        self.assertFalse(num_eq("a", "b"))


class TestEndToEnd(unittest.TestCase):
    """端到端: 在临时目录跑真实脚本(副进程), 验证退出码。"""

    def _run(self, tmp: Path, *args: str) -> tuple[int, str]:
        import subprocess

        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_specs_consistency.py"), *args],
            capture_output=True,
            text=True,
            cwd=str(tmp),
        )
        return proc.returncode, proc.stdout + proc.stderr

    def test_drift_detected_exit_1(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            (tmp / "configs").mkdir()
            (tmp / "configs" / "benchmark.small.json").write_text(
                '{"corpus": {"n_topics": 5, "seed": 20260819}}', encoding="utf-8"
            )
            doc = tmp / "BM.md"
            doc.write_text(
                DOC_TEMPLATE.format(params="n_topics=8, seed=20260819"), encoding="utf-8"
            )
            code, out = self._run(tmp, "--doc", str(doc), "--configs-dir", str(tmp / "configs"))
            self.assertEqual(code, 1)
            self.assertIn("n_topics", out)
            self.assertIn("漂移", out)

    def test_consistent_exit_0(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            (tmp / "configs").mkdir()
            (tmp / "configs" / "benchmark.small.json").write_text(
                '{"corpus": {"n_topics": 5, "seed": 20260819.0}}', encoding="utf-8"
            )
            doc = tmp / "BM.md"
            doc.write_text(
                DOC_TEMPLATE.format(params="n_topics=5, seed=20260819"), encoding="utf-8"
            )
            code, out = self._run(tmp, "--doc", str(doc), "--configs-dir", str(tmp / "configs"))
            self.assertEqual(code, 0, out)
            self.assertIn("零漂移", out)

    def test_missing_config_reported(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            doc = tmp / "BM.md"
            doc.write_text(DOC_TEMPLATE.format(params="n_topics=5"), encoding="utf-8")
            code, out = self._run(tmp, "--doc", str(doc), "--configs-dir", str(tmp / "configs"))
            self.assertEqual(code, 1)
            self.assertIn("配置文件不存在", out)


if __name__ == "__main__":
    unittest.main()
