#!/usr/bin/env python3
"""Render an rt-code-review run folder into the report, the findings file and the lesson.

Usage: render.py <run folder> [out dir, default /tmp/rt-code-review]
"""
import datetime
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LANES = {"A": "ARCHITECTURE", "T": "TESTS", "Q": "QA"}
VERDICTS = ("Confirmed", "Regraded", "Not worth fixing", "Refuted", "Unproven")
DISMISSED = ("Not worth fixing", "Refuted")
LEVELS = {"revert-safe": "Revert-safe", "revert with cleanup": "Revert with cleanup", "one-way": "One-way"}
LEVEL_CLASS = {"Revert-safe": "safe", "Revert with cleanup": "cleanup", "One-way": "oneway"}
warnings = []


class RenderError(Exception):
    pass


def band(score):
    return "Blocking" if score >= 8 else "Should-fix" if score >= 4 else "Nit"


def esc(text):
    return html.escape(text or "")


def score_of(text):
    m = re.match(r"\s*(\d+)", text or "")
    return int(m.group(1)) if m and 1 <= int(m.group(1)) <= 10 else None


def fence_step(fence, line):
    """Track ``` fences: return the open fence's length, or None outside one."""
    m = re.match(r"\s*(`{3,})(.*)", line)
    if not m:
        return fence
    if fence is None:
        return len(m.group(1))
    return None if len(m.group(1)) >= fence and not m.group(2).strip() else fence


def split(text, pattern):
    """Split on lines matching `pattern` outside code fences: [(match or None, body)]."""
    parts, fence = [(None, [])], None
    for line in (text or "").splitlines():
        m = None if fence else re.match(pattern, line)
        if m:
            parts.append((m, []))
            continue
        fence = fence_step(fence, line)
        parts[-1][1].append(line)
    return [(m, "\n".join(body).strip()) for m, body in parts]


def fields(text):
    """A block: an optional '### title' line, then '- **Name:** value' fields."""
    parts = split(text, r"- \*\*([^*]+?):\*\*\s?(.*)$")
    title = parts[0][1][4:].strip() if parts[0][1].startswith("### ") else ""
    return title, {m.group(1): (m.group(2) + "\n" + body).strip() for m, body in parts[1:]}


def inline(text):
    out = []
    for i, part in enumerate(re.split(r"(`[^`]+`)", text or "")):
        if i % 2:
            out.append("<code>%s</code>" % esc(part[1:-1]))
        else:
            part = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(part))
            out.append(re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', part))
    return "".join(out)


def md(text, diagrams=True, block=True):
    """Paragraphs, '- ' lists and fenced code to HTML. With block=False one line stays inline."""
    text = (text or "").strip()
    if not block and "\n" not in text and not text.startswith("- "):
        return inline(text)
    out, para, items, code, fence = [], [], [], [], None

    def flush():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
        if items:
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(i) for i in items))
        del para[:], items[:]

    for line in text.splitlines():
        if fence is not None:
            if fence_step(fence, line) is None:
                cls = {"diff": ' class="diff"', "mermaid": ' class="mermaid"' if diagrams else ""}.get(lang, "")
                out.append("<pre%s>%s</pre>" % (cls, esc("\n".join(code))))
                fence, code = None, []
            else:
                code.append(line[indent:] if not line[:indent].strip() else line)
            continue
        m = re.match(r"(\s*)(`{3,})\s*(\S*)", line)
        s = line.strip()
        if m:
            flush()
            fence, indent, lang = len(m.group(2)), len(m.group(1)), m.group(3)
        elif not s:
            flush()
        elif s.startswith("- "):
            if para:
                out.append("<p>%s</p>" % inline(" ".join(para)))
                del para[:]
            items.append(s[2:])
        elif items and line.startswith(" "):
            items[-1] += " " + s
        else:
            para.append(s)
    flush()
    return "".join(out)


def graph(structure):
    """`A -> B -> C, A -> C` as a Mermaid graph, or None."""
    ids, edges = {}, []
    for chain in re.split(r"[,;\n]", structure.replace("`", "")):
        names = [n.strip() for n in re.split(r"-+>|→", chain) if n.strip()]
        edges += zip(names, names[1:])
    node = lambda n: '%s["%s"]' % (ids.setdefault(n, "n%d" % len(ids)), n.replace('"', "'"))
    return "graph LR\n" + "\n".join("  %s --> %s" % (node(a), node(b)) for a, b in edges) if edges else None


def fill(template, values):
    missing = set(re.findall(r"\{\{([A-Z_]+)\}\}", template)) - set(values)
    if missing:
        raise RenderError("no value for placeholders: " + ", ".join(sorted(missing)))
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values[m.group(1)], template)


# Findings

def judge(fid, parts):
    """Apply the verdict table of SKILL.md step 3 to one finding."""
    title, f = fields(parts.get("finding", ""))
    tags, score = [], score_of(f.get("Score"))
    if score is None:
        b = re.match(r"\[(Blocking|Should-fix|Nit)\]", title, re.I)
        score = {"blocking": 8, "should-fix": 5, "nit": 2}[b.group(1).lower()] if b else 5
        tags.append("score inferred")
    d = dict(id=fid, num=int(fid[1:]), title=re.sub(r"^\[[^\]]*\]\s*", "", title), f=f, parts=parts,
             reviewer_score=score, score=score, fix=f.get("Fix", ""), tags=tags, verification="", dismissed=False)

    _, v = fields(parts.get("verdict"))
    verdict = next((x for x in VERDICTS if v.get("Verdict", "").startswith(x)), None)
    proof = re.match(r"(?i)(not proven|proven)", v.get("Proof", ""))
    new_score = score_of(v.get("Score"))
    broken = (verdict is None
              or verdict in ("Confirmed", "Regraded") and not proof
              or verdict == "Regraded" and new_score is None
              or verdict == "Unproven" and not (v.get("Probe") and v.get("Expect")))
    if broken:
        if parts.get("verdict"):
            warnings.append("%s: the verdict block is not in the brief's shape, so it is Unverified" % fid)
        tags.append("unverified")
        return dict(d, status="Unverified")

    reason = inline(v.get("Reason")) + md(v.get("Evidence"), diagrams=False)
    if v.get("Fix") and verdict not in DISMISSED:
        d["fix"] = v["Fix"]
        tags.append("fix revised by verification")
    if verdict in ("Confirmed", "Regraded"):
        proven = proof.group(1).lower() == "proven"
        d["status"] = "%s (%s)" % (verdict, "Proven" if proven else "Not proven")
        if not proven:
            tags.append("not proven")
        if verdict == "Regraded":
            d["score"] = new_score
            tags.append("was %d/10" % score)
            d["verification"] = "<strong>Regraded</strong>: " + reason
    elif verdict in DISMISSED:
        d.update(status=verdict, dismissed=True, verification="<strong>%s</strong>: %s" % (verdict, reason))
    else:
        _, p = fields(parts.get("probe"))
        result, run = p.get("Result", "").split(" ")[0], md(p.get("Run"), diagrams=False)
        if result in ("Confirmed", "Refuted"):
            d.update(status="Confirmed (Proven)" if result == "Confirmed" else "Refuted",
                     dismissed=result == "Refuted",
                     verification="<strong>%s by host probe</strong>: %s%s" % (result, inline(v.get("Reason")), run))
        else:
            tags.append("unproven")
            d.update(status="Unproven", verification="<strong>Unproven</strong>: %s%s<p>Probe:</p>%s<p>Expect: %s</p>%s" % (
                inline(p.get("Reason") or "No host probe ran."), md(v.get("Evidence"), False),
                md(v.get("Probe"), False), inline(v.get("Expect")), run))
    return d


def card(d):
    score = d["reviewer_score"] if d["dismissed"] else d["score"]
    f = d["f"]
    diagram = None if d["dismissed"] else graph(f.get("Structure", ""))
    rows = [(k, md(f[k], block=False)) for k in ("Where", "What", "Why") if f.get(k)]
    rows += [("Fix", md(d["fix"], diagrams=False, block=False))] if d["fix"] else []
    rows += [("Structure", md(f["Structure"], block=False))] if f.get("Structure") and not diagram else []
    rows += [("Verification", d["verification"])] if d["verification"] else []
    return ('<article class="finding %s"><h3><span class="id">%s</span> <span class="badge">%s</span> '
            '<span class="score">%d/10</span> %s%s</h3><dl>%s</dl>%s</article>') % (
        band(score).lower(), d["id"], band(score), score, inline(d["title"]),
        "".join(' <span class="tag">%s</span>' % t for t in d["tags"]),
        "".join("<dt>%s</dt><dd>%s</dd>" % row for row in rows),
        '<pre class="mermaid">%s</pre>' % esc(diagram) if diagram else "")


def load_findings(run):
    parts = {}
    for m, body in split((run / "findings.md").read_text() if (run / "findings.md").exists() else "",
                         r"=== ([ATQ]\d+) (finding|verdict|probe)\s*$"):
        if m:
            parts.setdefault(m.group(1), {})[m.group(2)] = body
    for fid, p in parts.items():
        if "finding" not in p:
            raise RenderError("%s has no '=== %s finding' block" % (fid, fid))
    return [judge(fid, p) for fid, p in parts.items()]


def lane(findings):
    shown = sorted((d for d in findings if not d["dismissed"]), key=lambda d: (-d["score"], d["num"]))
    gone = [d for d in findings if d["dismissed"]]
    out = "".join(map(card, shown)) or '<p class="clean">No findings.</p>'
    if gone:
        out += '<details class="dismissed"><summary>Dismissed by verification (%d)</summary>%s</details>' % (
            len(gone), "".join(map(card, gone)))
    return out


# Summary, lesson, findings file

def load_summary(run):
    path = run / "summary.md"
    if not path.exists():
        warnings.append("summary.md is missing")
        return '<p class="clean">The change summariser returned nothing.</p>', None, ""
    overview, views, level, notes = "", "", None, ""
    for m, body in split(path.read_text(), r"### (.+?)\s*$"):
        name = m.group(1).lower() if m else ""
        if name == "overview":
            overview = md(body)
        elif name == "reversibility":
            lv = re.match(r"(?:- \*\*)?Level:?\**:?\s*(.+)", body)
            level = LEVELS.get(lv.group(1).strip().lower().rstrip(".")) if lv else None
            notes = body[lv.end():] if lv else body
        elif m:
            views += "<h3>%s</h3>%s" % (inline(m.group(1)), md(body))
    if level is None:
        warnings.append("summary.md has no Reversibility level in the brief's shape")
    return overview + views, level, notes


def parse_quiz(body):
    questions = []
    for line in body.splitlines():
        q, o, fb = re.match(r"\d+\.\s+(.*)", line), re.match(r"\s*-\s*\[([ xX])\]\s+(.*)", line), re.match(r"\s*>\s?(.*)", line)
        if q:
            questions.append({"text": inline(q.group(1)), "options": [], "answer": -1, "feedback": ""})
        elif o and questions:
            if o.group(1) != " ":
                if questions[-1]["answer"] >= 0:
                    raise RenderError("lesson.md: quiz question %d marks two answers" % len(questions))
                questions[-1]["answer"] = len(questions[-1]["options"])
            questions[-1]["options"].append(inline(o.group(2)))
        elif fb and questions:
            questions[-1]["feedback"] += inline(fb.group(1)) + " "
    for i, q in enumerate(questions, 1):
        if q["answer"] < 0:
            raise RenderError("lesson.md: quiz question %d marks no answer with [x]" % i)
    return questions


def render_lesson(run, meta, report, date):
    ws = pathlib.Path(meta.get("Learning workspace", "")).expanduser()
    if not meta.get("Learning workspace"):
        return None
    if not ws.is_absolute():
        raise RenderError("meta.md: Learning workspace must be an absolute path")
    if not (run / "lesson.md").exists():
        warnings.append("lesson.md is missing, so there is no lesson")
        return None
    s = {(m.group(1).split(":")[0].strip().lower() if m else ""): (m, body)
         for m, body in split((run / "lesson.md").read_text(), r"### (.+?)\s*$")}
    for need in ("lesson", "before", "now", "quiz"):
        if need not in s:
            raise RenderError("lesson.md has no '### %s' section" % need.capitalize())
    title = s["lesson"][0].group(1).split(":", 1)[1].strip()
    quiz = parse_quiz(s["quiz"][1])
    if not quiz:
        raise RenderError("lesson.md: the Quiz section has no questions")
    sec = lambda name: s.get(name, (None, ""))[1]

    (ws / "lessons").mkdir(parents=True, exist_ok=True)
    number = 1 + max([int(p.name[:4]) for p in (ws / "lessons").glob("[0-9][0-9][0-9][0-9]-*")], default=0)
    name = "%04d-%s" % (number, re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50])
    if sec("reference"):
        (ws / "reference").mkdir(exist_ok=True)
        (ws / "reference" / (name + ".md")).write_text("# From lesson %04d: %s\n\n%s\n" % (number, title, sec("reference")))

    css, js = ((HERE / "lesson-assets" / f).read_text() for f in ("lesson.css", "quiz.js"))
    out = ws / "lessons" / (name + ".html")
    out.write_text(fill((HERE / "lesson-template.html").read_text(), {
        "CSS": css, "QUIZ_JS": js, "LESSON_ID": "L%04d" % number, "TITLE": esc(title), "DATE": date,
        "QUIZ_JSON": json.dumps({"id": "L%04d" % number, "questions": quiz}).replace("</", "<\\/"),
        "WIN": inline(fields(sec("lesson"))[1].get("Win")), "TARGET": esc(meta["Target"]), "REPO": esc(meta["Repo"]),
        "BEFORE": md(sec("before")), "NOW": md(sec("now")),
        "WHY": md(sec("why it changed")) or "<p>The commits do not say.</p>",
        "CONCEPTS": md(sec("concepts")) or "<p>None needed beyond the code above.</p>",
        "READ_NEXT": md(sec("read next")), "INDEX_HREF": "../index.html", "REPORT_HREF": esc(report.as_uri()),
    }))

    lessons = "".join('<li><a href="lessons/%s">%s</a></li>' % (esc(p.name), re.search(r"<title>(.*?)</title>", p.read_text()).group(1))
                      for p in sorted((ws / "lessons").glob("[0-9]*.html")))
    refs = "".join("<section>%s</section>" % md(p.read_text().replace("# ", "", 1))
                   for p in sorted((ws / "reference").glob("*.md"))) if (ws / "reference").exists() else ""
    (ws / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Lessons: %s</title><style>%s</style></head>'
        "<body><main><h1>Lessons: %s</h1><h2>Lessons</h2><ol>%s</ol><h2>Reference</h2>%s</main></body></html>\n"
        % (esc(meta["Repo"]), css, esc(meta["Repo"]), lessons, refs or "<p>No reference entries yet.</p>"))
    return out


def findings_file(meta, findings, report, level, lesson, run):
    out = ["# Findings: " + meta["Target"], ""]
    out += ["- %s: %s" % (k, v) for k, v in (
        ("Repo", meta["Repo"]), ("Branch", meta["Branch"]), ("Report", report),
        ("Stack", re.sub(r"\s*\(.*\)$", "", meta["Stack"])), ("Base", meta["Base"]), ("Head", meta["Head"]),
        ("Uncommitted", meta["Uncommitted"]), ("Reversibility", level or "unknown"), ("Lesson", lesson or "none"))]
    out += ["", "## Findings", ""] + ([] if findings else ["No findings.", ""])
    for d in sorted(findings, key=lambda d: ("ATQ".index(d["id"][0]), d["num"])):
        p = d["parts"]
        out += ["### " + d["id"], "- **Status:** " + d["status"], "- **Score:** %d (%s)" % (d["score"], band(d["score"])), "",
                p["finding"], ""] + ([p["verdict"], ""] if p.get("verdict") else []) + (
                ["**Probe result:**", "", p["probe"], ""] if p.get("probe") else [])
    if (run / "fix-context.md").exists():
        out += ["## Fix context", "", (run / "fix-context.md").read_text().strip(), ""]
    return "\n".join(out)


def render(run, out_dir):
    if not (run / "meta.md").exists():
        raise RenderError("%s has no meta.md" % run)
    meta = dict(re.findall(r"(?m)^- ([^:]+):\s*(.*)$", (run / "meta.md").read_text()))
    for key in ("Target", "Repo", "Branch", "Mode", "Stack", "Base", "Head", "Uncommitted"):
        if not meta.get(key):
            raise RenderError("meta.md has no '- %s:' line" % key)
    out_dir.mkdir(parents=True, exist_ok=True)
    report, findings_md = out_dir.absolute() / (run.name + ".html"), out_dir.absolute() / (run.name + ".findings.md")
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    findings = load_findings(run)
    summary, level, notes = load_summary(run)
    lesson = render_lesson(run, meta, report, date)
    rev = '<span class="rev %s">%s</span>' % (LEVEL_CLASS[level], level) if level else ""
    context = [line.strip().strip("|").split("|") for line in
               ((run / "fix-context.md").read_text().splitlines() if (run / "fix-context.md").exists() else [])
               if line.strip().startswith("|")][2:]
    values = {
        "TARGET_TITLE": esc(meta["Target"]), "REPO": esc(meta["Repo"]), "MODE": esc(meta["Mode"]),
        "STACK": esc(meta["Stack"]), "STACK_SETTINGS": esc(meta.get("Stack settings", "none")),
        "BASE": esc(meta["Base"]), "HEAD": esc(meta["Head"]), "DATE": date, "SUMMARY": summary,
        "REVERSIBILITY_BADGE": " · " + rev if rev else "",
        "REVERSIBILITY": "<p>%s</p>%s" % (rev, md(notes)) if rev else '<p class="clean">No reversibility given.</p>',
        "LESSON_LINK": ' · <a href="%s">Lesson</a>' % esc(lesson.as_uri()) if lesson else "",
        "EARLIER": ('<section id="earlier"><h2>Earlier findings</h2><table class="earlier"><tr><th>Run</th><th>Finding</th>'
                    "<th>Where</th><th>What</th><th>Outcome</th><th>Commit or reason</th></tr>%s</table></section>" % "".join(
                        "<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c.strip()) for c in row) for row in context)) if context else "",
    }
    for letter, key in LANES.items():
        mine = [d for d in findings if d["id"][0] == letter]
        values["FINDINGS_" + key] = lane(mine)
        for b in ("Blocking", "Should-fix", "Nit"):
            values["%s_%s" % (key, b.upper().replace("-", "_"))] = str(sum(1 for d in mine if not d["dismissed"] and band(d["score"]) == b))
        values[key + "_DISMISSED"] = str(sum(d["dismissed"] for d in mine))

    report.write_text(fill((HERE / "report-template.html").read_text(), values))
    findings_md.write_text(findings_file(meta, findings, report, level, lesson, run))
    return report, findings_md, lesson, findings


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        report, findings_md, lesson, findings = render(
            pathlib.Path(argv[1]).absolute(), pathlib.Path(argv[2] if len(argv) == 3 else "/tmp/rt-code-review"))
    except RenderError as e:
        print("error: %s" % e, file=sys.stderr)
        return 1
    print("report: %s\nfindings: %s\nlesson: %s" % (report, findings_md, lesson or "none"))
    for d in findings:
        print("finding: %s %s %d/10" % (d["id"], d["status"], d["score"]))
    print("".join("warning: %s\n" % w for w in warnings), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
