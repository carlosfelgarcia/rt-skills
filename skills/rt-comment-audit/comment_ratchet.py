#!/usr/bin/env python3
import argparse
import ast
import fnmatch
import io
import json
import os
import re
import subprocess
import sys
import tokenize

USAGE = """List the comments in a repo's Swift and Python files, and hold their count to a ratchet.

  list [--base SHA]   every comment, or only those a diff from SHA adds or sits inside
  count               counted comment lines per file, with totals
  init                write the baseline from the current counts
  check [--lower]     fail when a file has more counted comment lines than the baseline allows

Listed and counted: comment and doc lines. Listed, never counted: directives.
Never listed or counted: shebangs, encoding lines, the swift-tools-version line and a
license header at the top of a file.
"""

BASELINE = ".comment-ratchet.json"
COUNTED = ("comment", "doc")
LISTED = COUNTED + ("directive",)
BEFORE_HEADER = ("shebang", "encoding", "tools-version")
LICENSE = re.compile(r"SPDX-License-Identifier|\blicen[cs]e", re.IGNORECASE)
COPYRIGHT = re.compile(r"\bcopyright\b|©|all rights reserved", re.IGNORECASE)
XCODE_TEMPLATE = re.compile(r"^\W*created by\b", re.IGNORECASE | re.MULTILINE)
SWIFT_TOOLS_VERSION = re.compile(r"^//\s*swift-tools-version\s*:")
ENCODING = re.compile(r"^#.*coding[:=]")
PY_DIRECTIVE = re.compile(
    r"^#\s*(noqa\b|type:|pragma\b|pylint:|pyright:|mypy:|fmt:|isort:|ruff:|nosec\b|pyre-)")
SWIFT_DIRECTIVE = re.compile(r"^//\s*(swiftlint:|swiftformat:|sourcery:|periphery:)")


class Comment:
    def __init__(self, start, end, text, kind, own_line):
        self.start = start
        self.end = end
        self.text = text
        self.kind = kind
        self.own_line = own_line

    def lines(self):
        return range(self.start, self.end + 1)


def python_comments(src):
    raw = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                line, col = tok.start
                raw.append(Comment(line, line, tok.string, "comment", not tok.line[:col].strip()))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return None
    for c in raw:
        if c.start == 1 and c.text.startswith("#!"):
            c.kind = "shebang"
        elif c.start <= 2 and ENCODING.match(c.text):
            c.kind = "encoding"
        elif PY_DIRECTIVE.match(c.text):
            c.kind = "directive"
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    docs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                expr = body[0]
                docs.append(Comment(expr.lineno, expr.end_lineno, body[0].value.value.strip(), "doc", True))
    return _finish(src, _group(raw) + docs)


def swift_comments(src):
    found = []
    i, n, line = 0, len(src), 1
    if src.startswith("#!"):
        end = src.find("\n")
        end = n if end < 0 else end
        found.append(Comment(1, 1, src[:end], "shebang", True))
        i = end
    stack = [("code", None)]
    while i < n:
        top = stack[-1]
        c = src[i]
        if top[0] == "code":
            if src.startswith("//", i):
                end = src.find("\n", i)
                end = n if end < 0 else end
                text = src[i:end]
                own = not src[src.rfind("\n", 0, i) + 1:i].strip()
                if line == 1 and SWIFT_TOOLS_VERSION.match(text):
                    kind = "tools-version"
                elif SWIFT_DIRECTIVE.match(text):
                    kind = "directive"
                elif text.startswith("///") and not text.startswith("////"):
                    kind = "doc"
                else:
                    kind = "comment"
                found.append(Comment(line, line, text, kind, own))
                i = end
                continue
            if src.startswith("/*", i):
                start_line, j, depth = line, i + 2, 1
                while j < n and depth:
                    if src.startswith("/*", j):
                        depth, j = depth + 1, j + 2
                    elif src.startswith("*/", j):
                        depth, j = depth - 1, j + 2
                    else:
                        if src[j] == "\n":
                            line += 1
                        j += 1
                text = src[i:j]
                own = not src[src.rfind("\n", 0, i) + 1:i].strip()
                doc = text.startswith("/**") and not text.startswith("/**/")
                found.append(Comment(start_line, line, text, "doc" if doc else "comment", own))
                i = j
                continue
            if c in "#\"":
                h = 0
                while i + h < n and src[i + h] == "#":
                    h += 1
                if i + h < n and src[i + h] == '"':
                    multi = src.startswith('"""', i + h)
                    stack.append(("str", h, multi))
                    i += h + (3 if multi else 1)
                    continue
                i += max(h, 1)
                continue
            if top[1] is not None:
                if c == "(":
                    stack[-1] = ("code", top[1] + 1)
                elif c == ")":
                    if top[1] == 0:
                        stack.pop()
                        i += 1
                        continue
                    stack[-1] = ("code", top[1] - 1)
            if c == "\n":
                line += 1
            i += 1
        else:
            _, h, multi = top
            if c == "\\" and src[i + 1:i + 1 + h] == "#" * h:
                j = i + 1 + h
                if j < n and src[j] == "(":
                    stack.append(("code", 0))
                    i = j + 1
                    continue
                if j < n and src[j] == "\n":
                    line += 1
                i = j + 1
                continue
            closing = ('"""' if multi else '"') + "#" * h
            if src.startswith(closing, i):
                stack.pop()
                i += len(closing)
                continue
            if c == "\n":
                line += 1
                if not multi:
                    stack.pop()
            i += 1
    return _finish(src, _group(found))


def _group(comments):
    groups = []
    for c in sorted(comments, key=lambda c: c.start):
        prev = groups[-1] if groups else None
        if (prev and c.kind in COUNTED and prev.kind == c.kind and prev.own_line and c.own_line
                and prev.text.startswith(("//", "#")) and c.start == prev.end + 1):
            prev.end = c.end
            prev.text += "\n" + c.text
        else:
            groups.append(c)
    return groups


def _finish(src, comments):
    comments.sort(key=lambda c: c.start)
    skip = {c.start for c in comments if c.kind in BEFORE_HEADER}
    lines = src.splitlines()
    first = next((k + 1 for k, text in enumerate(lines) if text.strip() and k + 1 not in skip), None)
    header = _header(lines, comments, first)
    text = "\n".join(c.text for c in header)
    if LICENSE.search(text) or (COPYRIGHT.search(text) and not XCODE_TEMPLATE.search(text)):
        for c in header:
            c.kind = "license"
    return comments


def _header(lines, comments, first):
    blocks = [c for c in comments if c.own_line and c.kind in COUNTED]
    start = next((k for k, c in enumerate(blocks) if c.start == first), None)
    if start is None or not _has_marker(blocks[start]):
        return []
    header = [blocks[start]]
    for c in blocks[start + 1:]:
        gap = lines[header[-1].end:c.start - 1]
        if any(text.strip() for text in gap) or not _has_marker(c):
            break
        header.append(c)
    return header


def _has_marker(comment):
    return bool(LICENSE.search(comment.text) or COPYRIGHT.search(comment.text))


LANGUAGES = {".py": python_comments, ".swift": swift_comments}


def comments_in(path):
    parse = LANGUAGES.get(os.path.splitext(path)[1])
    if not parse:
        return []
    with open(path, encoding="utf-8", errors="replace") as f:
        src = f.read()
    found = parse(src)
    if found is None:
        print("skipped, does not parse: " + path, file=sys.stderr)
        return []
    return found


def git(root, *args):
    return subprocess.run(("git",) + args, cwd=root, check=True, capture_output=True, text=True).stdout


def load_baseline(root):
    path = os.path.join(root, BASELINE)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def excluded(rel, patterns):
    return any(fnmatch.fnmatch(rel, p) for p in patterns)


def repo_files(root, patterns):
    names = git(root, "ls-files", "-co", "--exclude-standard").splitlines()
    return sorted(rel for rel in set(names)
                  if os.path.splitext(rel)[1] in LANGUAGES and not excluded(rel, patterns)
                  and os.path.isfile(os.path.join(root, rel)))


def diff_ranges(root, base, patterns):
    ranges, path = {}, None
    for text in git(root, "diff", "--no-color", "--no-ext-diff", "-U3", base, "--").splitlines():
        if text.startswith("+++ "):
            path = None if text == "+++ /dev/null" else text[6:]
        elif text.startswith("@@") and path:
            m = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", text)
            start, count = int(m.group(1)), int(m.group(2) or "1")
            ranges.setdefault(path, []).append((start, start + count - 1))
    for rel in git(root, "ls-files", "--others", "--exclude-standard").splitlines():
        ranges[rel] = [(1, float("inf"))]
    return {rel: r for rel, r in ranges.items()
            if os.path.splitext(rel)[1] in LANGUAGES and not excluded(rel, patterns)
            and os.path.isfile(os.path.join(root, rel))}


def counted_lines(comments):
    return len({line for c in comments if c.kind in COUNTED for line in c.lines()})


def counts(root, patterns):
    result = {}
    for rel in repo_files(root, patterns):
        n = counted_lines(comments_in(os.path.join(root, rel)))
        if n:
            result[rel] = n
    return result


def cmd_list(root, args, patterns):
    if args.base:
        targets = diff_ranges(root, args.base, patterns)
    else:
        targets = {rel: [(1, float("inf"))] for rel in repo_files(root, patterns)}
    for rel in sorted(targets):
        for c in comments_in(os.path.join(root, rel)):
            if c.kind in LISTED and any(c.start <= hi and c.end >= lo for lo, hi in targets[rel]):
                where = "%s:%d" % (rel, c.start) + ("-%d" % c.end if c.end != c.start else "")
                first = c.text.splitlines()[0].strip() if c.text.strip() else ""
                print("\t".join((where, c.kind, "own-line" if c.own_line else "trailing", first[:100])))


def cmd_count(root, patterns):
    files = counts(root, patterns)
    own = 0
    for rel in files:
        comments = comments_in(os.path.join(root, rel))
        own += len({line for c in comments if c.kind in COUNTED and c.own_line for line in c.lines()})
    print(json.dumps({"files": files, "total": sum(files.values()), "own_line": own}, indent=2))


def write_baseline(root, baseline):
    baseline["files"] = dict(sorted(baseline["files"].items()))
    with open(os.path.join(root, BASELINE), "w") as f:
        json.dump(baseline, f, indent=2)
        f.write("\n")


def cmd_init(root, patterns):
    write_baseline(root, {"exclude": patterns, "files": counts(root, patterns)})


def cmd_check(root, args, baseline):
    if baseline is None:
        print("no %s at %s; run init first" % (BASELINE, root), file=sys.stderr)
        return 2
    limits = baseline.get("files", {})
    now = counts(root, baseline.get("exclude", []))
    over = {rel: n for rel, n in now.items() if n > limits.get(rel, 0)}
    for rel in sorted(over):
        print("%s: %d comment lines, limit %d" % (rel, over[rel], limits.get(rel, 0)))
    if over:
        print("This repo bans code comments. Move what each new comment says into a name, a test, "
              "an ADR or an issue; /rt-comment-audit does it.")
        return 1
    if args.lower:
        lowered = {rel: n for rel, n in now.items() if n < limits.get(rel, 0)}
        gone = [rel for rel in limits if rel not in now]
        if lowered or gone:
            baseline["files"] = now
            write_baseline(root, baseline)
            print("lowered %d files, dropped %d" % (len(lowered), len(gone)))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("list", "count", "init", "check"))
    parser.add_argument("--root", help="repo root; defaults to the git top level of the working directory")
    parser.add_argument("--base", help="list: only comments a diff from this commit adds or sits inside")
    parser.add_argument("--exclude", action="append", default=[], help="glob of paths to skip, repeatable")
    parser.add_argument("--lower", action="store_true", help="check: lower the baseline to counts that fell")
    args = parser.parse_args(argv)
    root = args.root or git(os.getcwd(), "rev-parse", "--show-toplevel").strip()
    baseline = load_baseline(root)
    patterns = (baseline or {}).get("exclude", []) + args.exclude
    if args.command == "list":
        cmd_list(root, args, patterns)
    elif args.command == "count":
        cmd_count(root, patterns)
    elif args.command == "init":
        cmd_init(root, patterns)
    else:
        return cmd_check(root, args, baseline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
