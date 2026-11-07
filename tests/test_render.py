import importlib.util
import pathlib
import re
import shutil
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("render", HERE.parent / "skills" / "rt-code-review" / "render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


class RenderFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.run = self.tmp / "demo-run"
        shutil.copytree(HERE / "fixtures" / "run", self.run)
        meta = self.run / "meta.md"
        meta.write_text(meta.read_text().replace("LEARNING_WORKSPACE", str(self.tmp / "learning")))
        self.report, self.findings_md, self.lesson, findings = render.render(self.run, self.tmp / "out")
        self.html = self.report.read_text()
        self.by_id = {d["id"]: d for d in findings}

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_verdict_table(self):
        status = {k: d["status"] for k, d in self.by_id.items()}
        self.assertEqual(status, {"A1": "Confirmed (Proven)", "A2": "Refuted", "T1": "Regraded (Proven)",
                                  "T2": "Unverified", "Q1": "Unproven", "Q2": "Unverified"})
        self.assertTrue(self.by_id["A2"]["dismissed"])
        self.assertEqual(self.by_id["T1"]["score"], 8)
        self.assertEqual(self.by_id["Q2"]["score"], 8)

    def test_report(self):
        ids = re.findall(r'<span class="id">(\w+)</span>', self.html)
        self.assertEqual(sorted(ids), sorted(self.by_id))
        qa = self.html[self.html.index('id="qa"'):]
        self.assertLess(qa.index(">Q2<"), qa.index(">Q1<"))
        self.assertIn("<td>1</td><td>0</td><td>1</td><td>0</td>", self.html)
        self.assertIn('class="rev cleanup"', self.html)
        self.assertIn(self.lesson.as_uri(), self.html)
        self.assertIn("Score 2 below threshold 4", self.html)
        self.assertNotRegex(self.html, r"\{\{[A-Z_]+\}\}")

    def test_findings_file(self):
        text = self.findings_md.read_text()
        self.assertIn("- Reversibility: Revert with cleanup", text)
        self.assertIn("- Stack: swift-app\n", text)
        self.assertIn("### T1\n- **Status:** Regraded (Proven)\n- **Score:** 8 (Blocking)", text)
        self.assertIn("## Fix context", text)

    def test_lesson(self):
        page = self.lesson.read_text()
        self.assertTrue(self.lesson.name.startswith("0001-"))
        self.assertIn('"id": "L0001"', page)
        self.assertNotRegex(page, r"\{\{[A-Z_]+\}\}")
        self.assertTrue((self.tmp / "learning" / "index.html").exists())
        self.assertTrue(render.render(self.run, self.tmp / "out")[2].name.startswith("0002-"))


class RenderPieces(unittest.TestCase):
    def test_pieces(self):
        _, f = render.fields("### t\n- **Fix:**\n  ```diff\n  -<a>\n  ```\n- **What:** x")
        self.assertIn("&lt;a&gt;", render.md(f["Fix"]))
        self.assertEqual(f["What"], "x")
        self.assertEqual(render.fill("{{A}}", {"A": "{{B}}"}), "{{B}}")
        self.assertEqual(render.graph("`A -> B -> C`").count("-->"), 2)
        self.assertEqual([render.band(s) for s in (3, 4, 7, 8)], ["Nit", "Should-fix", "Should-fix", "Blocking"])
        for quiz in ("1. Q\n - [ ] a\n - [ ] b", "1. Q\n - [x] a\n - [x] b"):
            with self.assertRaises(render.RenderError):
                render.parse_quiz(quiz)
        self.assertEqual(render.judge("T9", {"finding": "### t\n- **Score:** 5",
                                             "verdict": "- **Verdict:** Regraded\n- **Proof:** Proven"})["status"], "Unverified")


if __name__ == "__main__":
    unittest.main()
