import contextlib
import importlib.util
import io
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
        self.assertNotIn("**Origin:**", text)
        self.assertNotIn("Fix base", text)

    def test_lesson(self):
        page = self.lesson.read_text()
        self.assertTrue(self.lesson.name.startswith("0001-"))
        self.assertIn('"id": "L0001"', page)
        self.assertNotRegex(page, r"\{\{[A-Z_]+\}\}")
        self.assertTrue((self.tmp / "learning" / "index.html").exists())
        self.assertTrue(render.render(self.run, self.tmp / "out")[2].name.startswith("0002-"))


def finding(fid, origin=None, at_fix_base=None, verdict="Confirmed"):
    proposed = "- **Origin:** %s\n" % origin if origin else ""
    settled = "- **At fix base:** %s\n" % at_fix_base if at_fix_base else ""
    return ("=== {0} finding\n### Claim {0}\n- **Where:** `Sources/A.swift:{1}`\n- **Score:** 6 (Should-fix)\n"
            "- **What:** x.\n- **Why:** y.\n{2}\n=== {0} verdict\n- **Verdict:** {3}\n- **Proof:** Proven\n"
            "- **Reason:** r.\n- **Evidence:** `Sources/A.swift:1`: `x`\n{4}\n").format(
        fid, fid[1:], proposed, verdict, settled)


CONTEXT = ("| Run | Finding | Origin | Where | What | Outcome | Commit or reason |\n|---|---|---|---|---|---|---|\n"
           "| 1 | Q3 | — | `A.swift:1` | x. | Fixed | abc1234 |\n"
           "| 1 | Q4 | — | `A.swift:2` | x. | Skipped | Score 2 below threshold 4 |\n"
           "| 2 | Q2 | Added by a fix | `B.swift:5` | x. | Fixed | def5678 |\n")


class RenderReReview(unittest.TestCase):
    """A re-review: meta.md names a fix base, so each finding gets an origin."""

    def rerender(self, findings, meta_extra="- Fix base: 3333333\n", context=CONTEXT):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.run_dir = self.tmp / "re-run"
        self.run_dir.mkdir()
        (self.run_dir / "meta.md").write_text(
            "- Target: feature/x (Ref)\n- Repo: demo-app\n- Branch: feature/x\n- Mode: Ref\n"
            "- Stack: swift-app (argument)\n- Base: 1111111\n- Head: 4444444\n- Uncommitted: no\n" + meta_extra)
        (self.run_dir / "summary.md").write_text("### Overview\nA change.\n\n### Reversibility\nLevel: Revert-safe\n")
        (self.run_dir / "findings.md").write_text("".join(findings))
        if context:
            (self.run_dir / "fix-context.md").write_text(context)
        report, findings_md, _, out = render.render(self.run_dir, self.tmp / "out")
        return report.read_text(), findings_md.read_text(), {d["id"]: d for d in out}

    def origins(self, *findings):
        return {k: d["origin"] for k, d in self.rerender(list(findings))[2].items()}

    def test_origin_is_added_by_a_fix_when_the_issue_is_absent_at_the_fix_base(self):
        _, text, by_id = self.rerender([finding("Q1", origin="Missed", at_fix_base="Absent")])
        self.assertEqual(by_id["Q1"]["origin"], "Added by a fix")
        self.assertIn("- Fix base: 3333333\n", text)
        self.assertIn("### Q1\n- **Status:** Confirmed (Proven)\n- **Score:** 6 (Should-fix)\n- **Origin:** Added by a fix\n", text)

    def test_an_issue_present_at_the_fix_base_is_a_failed_fix_only_when_it_names_a_fixed_row(self):
        origins = self.origins(
            finding("Q1", origin="Failed fix of 1 Q3", at_fix_base="Present"),
            finding("Q2", origin="Failed fix of 1 Q9", at_fix_base="Present"),
            finding("Q3", origin="Failed fix of 1 Q4", at_fix_base="Present"),
            finding("Q4", origin="Added by a fix", at_fix_base="Present"),
            finding("T1", at_fix_base="Present"))
        self.assertEqual(origins, {"Q1": "Failed fix of 1 Q3", "Q2": "Missed", "Q3": "Missed",
                                   "Q4": "Missed", "T1": "Missed"})

    def test_a_failed_fix_of_a_bug_that_a_fix_added_is_still_a_failed_fix(self):
        origins = self.origins(finding("Q1", origin="Failed fix of 2 Q2", at_fix_base="Absent"),
                               finding("Q2", origin="Failed fix of 1 Q3", at_fix_base="Absent"))
        self.assertEqual(origins, {"Q1": "Failed fix of 2 Q2", "Q2": "Added by a fix"})

    def test_an_unclear_answer_leaves_the_origin_not_settled(self):
        origins = self.origins(
            finding("T2", origin="Added by a fix", at_fix_base="Unsettled"),
            finding("A1", origin="Added by a fix"),
            "=== A2 finding\n### Claim\n- **Where:** `Sources/A.swift:2`\n- **Score:** 9 (Blocking)\n"
            "- **Origin:** Added by a fix\n\n=== A2 verdict\nnot a verdict\n")
        self.assertEqual(origins, {"T2": "Missed (not settled)", "A1": "Missed (not settled)", "A2": "Missed (not settled)"})
        self.assertIn("A1: the verdict has no At fix base line, so its origin is not settled", render.warnings)

    def test_answers_and_proposals_may_carry_extra_words(self):
        origins = self.origins(finding("Q1", at_fix_base="Absent, the guard is new."),
                               finding("Q2", origin="Failed fix of `1 Q3`", at_fix_base="**Present**: line 3"))
        self.assertEqual(origins, {"Q1": "Added by a fix", "Q2": "Failed fix of 1 Q3"})

    def test_the_report_tags_each_finding_with_its_origin(self):
        html, _, _ = self.rerender([finding("Q1", at_fix_base="Absent"),
                                    finding("Q2", origin="Failed fix of 1 Q3", at_fix_base="Present")])
        self.assertIn('<span class="tag origin">added by a fix</span>', html)
        self.assertIn('<span class="tag origin">failed fix of 1 Q3</span>', html)
        self.assertIn("fix base <code>3333333</code>", html)

    def test_the_findings_file_keeps_the_fix_commits_for_the_next_fix_run(self):
        _, text, _ = self.rerender([], meta_extra="- Fix base: 3333333\n- Fix commits: aaaaaaa bbbbbbb\n")
        self.assertIn("- Fix base: 3333333\n- Fix commits: aaaaaaa bbbbbbb\n", text)

    def test_the_earlier_findings_table_takes_its_columns_from_the_fix_context(self):
        html, _, _ = self.rerender([finding("Q1", at_fix_base="Present")])
        self.assertIn("<th>Origin</th>", html)
        self.assertIn("<td>Added by a fix</td>", html)

    def test_the_status_lines_name_each_origin(self):
        self.rerender([finding("Q1", at_fix_base="Absent")])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            render.main(["render.py", str(self.run_dir), str(self.tmp / "out")])
        self.assertIn("finding: Q1 Confirmed (Proven) 6/10 · Added by a fix\n", out.getvalue())


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
