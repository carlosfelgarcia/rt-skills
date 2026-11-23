import contextlib
import importlib.util
import io
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "comment_ratchet", HERE.parent / "skills" / "rt-comment-audit" / "comment_ratchet.py")
ratchet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ratchet)


def kinds(comments):
    return [(c.start, c.end, c.kind, c.own_line) for c in comments]


class Swift(unittest.TestCase):
    def test_strings_hide_comment_markers(self):
        src = '\n'.join([
            'let a = "// not a comment"',
            'let b = #"raw "/* still a string */" here"#',
            'let c = """',
            '  // inside a multi-line string',
            '  """',
            'let d = "\\(f("// nested")) x" // real',
            'let e = "\\"" // after an escaped quote',
        ])
        self.assertEqual(kinds(ratchet.swift_comments(src)),
                         [(6, 6, "comment", False), (7, 7, "comment", False)])

    def test_kinds_and_grouping(self):
        src = '\n'.join([
            '#!/usr/bin/swift',
            '/// Doc one',
            '/// Doc two',
            'func f() {}',
            '// swiftlint:disable force_cast',
            '/* outer /* nested */ still outer',
            '*/',
            '// one',
            '// two',
            '',
            '// three',
        ])
        self.assertEqual(kinds(ratchet.swift_comments(src)), [
            (1, 1, "shebang", True), (2, 3, "doc", True), (5, 5, "directive", True),
            (6, 7, "comment", True), (8, 9, "comment", True), (11, 11, "comment", True)])

    def test_license_header_only_at_the_top(self):
        src = '// SPDX-License-Identifier: MIT\nimport Foundation\n// a license note\n'
        self.assertEqual([c.kind for c in ratchet.swift_comments(src)], ["license", "comment"])

    def test_xcode_header_is_a_comment(self):
        src = ('//\n//  App.swift\n//  Created by Me on 1/1/26.\n'
               '//  Copyright (c) 2026 Me. All rights reserved.\n//\nimport SwiftUI\n')
        self.assertEqual(kinds(ratchet.swift_comments(src)), [(1, 5, "comment", True)])

    def test_xcode_header_with_a_license_is_a_license(self):
        src = '//\n//  App.swift\n//  Created by Me on 1/1/26.\n//  Licensed under MIT.\n//\nimport SwiftUI\n'
        self.assertEqual(kinds(ratchet.swift_comments(src)), [(1, 5, "license", True)])

    def test_block_copyright_header(self):
        src = '/*\n * Copyright 2024 Acme. All rights reserved.\n */\nimport Foundation\n'
        self.assertEqual(kinds(ratchet.swift_comments(src)), [(1, 3, "license", True)])

    def test_tools_version_comes_before_the_license_header(self):
        src = '// swift-tools-version:5.9\n// Copyright 2024 Acme\nimport PackageDescription\n// later\n'
        self.assertEqual(kinds(ratchet.swift_comments(src)), [
            (1, 1, "tools-version", True), (2, 2, "license", True), (4, 4, "comment", True)])


class Python(unittest.TestCase):
    def test_kinds(self):
        src = '\n'.join([
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            '"""Module doc."""',
            's = "# not a comment"',
            'import os  # noqa: F401',
            '',
            '',
            'def f():',
            '    """Two-line',
            '    doc."""',
            '    # one',
            '    # two',
            '    return 1  # trailing',
        ])
        self.assertEqual(kinds(ratchet.python_comments(src)), [
            (1, 1, "shebang", True), (2, 2, "encoding", True), (3, 3, "doc", True),
            (5, 5, "directive", False), (9, 10, "doc", True), (11, 12, "comment", True),
            (13, 13, "comment", False)])

    def test_docstring_license_header(self):
        src = '"""Copyright 2024 Acme.\n\nLicensed under the Apache License 2.0.\n"""\nimport os\n'
        self.assertEqual(kinds(ratchet.python_comments(src)), [(1, 4, "license", True)])

    def test_copyright_only_header(self):
        src = '# Copyright 2024 Acme. All rights reserved.\nimport os\n'
        self.assertEqual(kinds(ratchet.python_comments(src)), [(1, 1, "license", True)])

    def test_header_grows_across_blank_lines_only_while_marked(self):
        src = '\n'.join([
            '#!/usr/bin/env python3',
            '# Copyright 2024 Acme',
            '',
            '# Licensed under MIT',
            '',
            '# Parses shot lists.',
            'import os',
        ])
        self.assertEqual(kinds(ratchet.python_comments(src)), [
            (1, 1, "shebang", True), (2, 2, "license", True), (4, 4, "license", True),
            (6, 6, "comment", True)])

    def test_unmarked_first_comment_is_not_a_header(self):
        src = '# Parses shot lists.\n\n# Copyright 2024 Acme\nimport os\n'
        self.assertEqual([c.kind for c in ratchet.python_comments(src)], ["comment", "comment"])

    def test_counted_lines_skip_exempt_kinds(self):
        src = '# Licensed under the Apache License\nx = 1  # type: int\ny = 2  # why\n'
        self.assertEqual(ratchet.counted_lines(ratchet.python_comments(src)), 1)

    def test_unparsable_file_is_skipped(self):
        self.assertIsNone(ratchet.python_comments('def f(:\n'))


class Repo(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.write("a.py", "x = 1  # one\n# two\n")
        self.write("Pods/vendor.swift", "// vendored\n")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "init")
        self.base = self.git("rev-parse", "HEAD").strip()

    def tearDown(self):
        shutil.rmtree(self.root)

    def git(self, *args):
        return subprocess.run(("git",) + args, cwd=self.root, check=True, capture_output=True, text=True).stdout

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = ratchet.main(list(args) + ["--root", str(self.root)])
        return code, out.getvalue()

    def baseline(self):
        return json.loads((self.root / ".comment-ratchet.json").read_text())

    def test_init_honours_excludes(self):
        self.run_cli("init", "--exclude", "Pods/*")
        self.assertEqual(self.baseline(), {"exclude": ["Pods/*"], "files": {"a.py": 2}})

    def test_check_fails_on_a_rise_and_on_a_new_file(self):
        self.run_cli("init", "--exclude", "Pods/*")
        self.write("a.py", "x = 1  # one\n# two\n# three\n")
        self.write("b.swift", "let y = 2 // new\n")
        code, out = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("a.py: 3 comment lines, limit 2", out)
        self.assertIn("b.swift: 1 comment lines, limit 0", out)

    def test_lower_only_moves_down(self):
        self.run_cli("init", "--exclude", "Pods/*")
        self.write("a.py", "x = 1  # one\n")
        self.assertEqual(self.run_cli("check")[0], 0)
        self.assertEqual(self.baseline()["files"], {"a.py": 2})
        self.assertEqual(self.run_cli("check", "--lower")[0], 0)
        self.assertEqual(self.baseline()["files"], {"a.py": 1})
        self.write("a.py", "x = 1\n")
        self.run_cli("check", "--lower")
        self.assertEqual(self.baseline(), {"exclude": ["Pods/*"], "files": {}})

    def test_check_without_baseline(self):
        self.assertEqual(self.run_cli("check")[0], 2)

    def test_list_diff_covers_changed_hunks_and_untracked_files(self):
        far = "".join("v%d = %d\n" % (k, k) for k in range(20))
        self.write("a.py", "x = 1  # one\n# two\n" + far + "# far\n")
        self.git("commit", "-qam", "more")
        base = self.git("rev-parse", "HEAD").strip()
        self.write("a.py", "x = 1  # one\n# two\n" + far + "# far\ny = 2  # new\n")
        self.write("c.py", "# untracked\n")
        _, out = self.run_cli("list", "--base", base)
        where = [line.split("\t")[0] for line in out.splitlines()]
        self.assertEqual(where, ["a.py:23", "a.py:24", "c.py:1"])

    def test_list_leaves_out_headers_shebangs_and_encoding_lines(self):
        self.write("h.py", "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n"
                           "# SPDX-License-Identifier: MIT\nimport os  # noqa: F401\n")
        _, out = self.run_cli("list")
        rows = [line.split("\t")[:2] for line in out.splitlines() if line.startswith("h.py")]
        self.assertEqual(rows, [["h.py:4", "directive"]])

    def test_list_everything_without_a_base(self):
        _, out = self.run_cli("list")
        self.assertEqual([line.split("\t")[:3] for line in out.splitlines()], [
            ["Pods/vendor.swift:1", "comment", "own-line"],
            ["a.py:1", "comment", "trailing"],
            ["a.py:2", "comment", "own-line"]])


if __name__ == "__main__":
    unittest.main()
