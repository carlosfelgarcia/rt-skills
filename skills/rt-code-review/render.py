#!/usr/bin/env python3
"""Render an rt-code-review run folder into the report and the findings file.

A run folder whose meta.md has `- Walkthrough: yes` is an rt-walkthrough: the page has the change
summary only, and no findings file is written. `- Stack: none` leaves out the reversibility section.

Usage: render.py <run folder> [out dir, default /tmp/rt-code-review]
"""
import datetime
import html
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


def keep(template, parts):
    """Keep or drop each `<!-- if <part> -->` … `<!-- end <part> -->` block, as `parts` says."""
    for name, wanted in parts.items():
        block = r"[ \t]*<!-- if %s -->\n(.*?)[ \t]*<!-- end %s -->\n" % (name, name)
        template = re.sub(block, (lambda m: m.group(1)) if wanted else "", template, flags=re.S)
    return template


def fill(template, values):
    missing = set(re.findall(r"\{\{([A-Z_]+)\}\}", template)) - set(values)
    if missing:
        raise RenderError("no value for placeholders: " + ", ".join(sorted(missing)))
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values[m.group(1)], template)


# Findings

def fix_context(run):
    """The fix context table: its header cells, and one {header: cell} dict per row."""
    path = run / "fix-context.md"
    table = [[c.strip() for c in line.strip().strip("|").split("|")]
             for line in (path.read_text().splitlines() if path.exists() else []) if line.strip().startswith("|")]
    return (table[0], [dict(zip(table[0], row)) for row in table[2:]]) if table else ([], [])


BEFORE = "Before the fix run"


def origin_of(proposed, at_base, rows):
    """Settle a re-review finding's origin, as the Origin table of findings-file.md says (ADR 0010)."""
    answer = re.match(r"\W*(present|absent)\b", at_base or "", re.I)
    if not answer:
        return "Not settled"
    if answer.group(1).lower() == "absent":
        return "Added by a fix"
    named = re.search(r"Failed fix of\W*(\d+) ([ATQB]\d+)", proposed or "")
    row = next((r for r in rows if named and (r.get("Run"), r.get("Finding")) == named.groups()
                and r.get("Outcome") == "Fixed"), None)
    return "Failed fix of %s %s" % named.groups() if row else BEFORE


def judge(fid, parts, rows=None):
    """Apply the verdict table of SKILL.md step 3 to one finding."""
    title, f = fields(parts.get("finding", ""))
    tags, score = [], score_of(f.get("Score"))
    if score is None:
        b = re.match(r"\[(Blocking|Should-fix|Nit)\]", title, re.I)
        score = {"blocking": 8, "should-fix": 5, "nit": 2}[b.group(1).lower()] if b else 5
        tags.append("score inferred")
    d = dict(id=fid, num=int(fid[1:]), title=re.sub(r"^\[[^\]]*\]\s*", "", title), f=f, parts=parts,
             reviewer_score=score, score=score, fix=f.get("Fix", ""), tags=tags, verification="", dismissed=False,
             origin=None)

    _, v = fields(parts.get("verdict"))
    verdict = next((x for x in VERDICTS if v.get("Verdict", "").startswith(x)), None)
    proof = re.match(r"(?i)(not proven|proven)", v.get("Proof", ""))
    new_score = score_of(v.get("Score"))
    broken = (verdict is None
              or verdict in ("Confirmed", "Regraded") and not proof
              or verdict == "Regraded" and new_score is None
              or verdict == "Unproven" and not (v.get("Probe") and v.get("Expect")))
    if rows is not None:
        d["origin"] = origin_of(f.get("Origin"), None if broken else v.get("At base"), rows)
        if not broken and not v.get("At base"):
            warnings.append("%s: the verdict has no At base line, so its origin is not settled" % fid)
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
    if d["origin"] == BEFORE and not d["dismissed"]:
        d.update(dismissed=True, verification="<strong>%s</strong>: the issue is in the code before the fix run, "
                 "so this re-review does not judge it. %s" % (BEFORE, d["verification"] or reason))
    return d


def card(d, entries=()):
    score = d["reviewer_score"] if d["dismissed"] else d["score"]
    f = d["f"]
    diagram = None if d["dismissed"] else graph(f.get("Structure", ""))
    rows = [(k, md(f[k], block=False)) for k in ("Where", "What", "Why") if f.get(k)]
    inside = [e for e in entries if d["id"] in e["finding_ids"]]
    rows += [("In", " · ".join('<a href="#change-%d">%d. %s</a>' % (e["num"], e["num"], inline(e["title"]))
                                for e in inside))] if inside else []
    rows += [("Fix", md(d["fix"], diagrams=False, block=False))] if d["fix"] else []
    rows += [("Structure", md(f["Structure"], block=False))] if f.get("Structure") and not diagram else []
    rows += [("Verification", d["verification"])] if d["verification"] else []
    return ('<article class="finding %s" id="finding-%s"><h3><span class="id">%s</span> <span class="badge">%s</span> '
            '<span class="score">%d/10</span> %s%s</h3><dl>%s</dl>%s</article>') % (
        band(score).lower(), d["id"], d["id"], band(score), score, inline(d["title"]),
        "".join(' <span class="tag">%s</span>' % t for t in d["tags"]) + (
            ' <span class="tag origin">%s</span>' % esc(d["origin"][0].lower() + d["origin"][1:]) if d["origin"] else ""),
        "".join("<dt>%s</dt><dd>%s</dd>" % row for row in rows),
        '<pre class="mermaid">%s</pre>' % esc(diagram) if diagram else "")


def load_findings(run, rows=None):
    parts = {}
    for m, body in split((run / "findings.md").read_text() if (run / "findings.md").exists() else "",
                         r"=== ([ATQ]\d+) (finding|verdict|probe)\s*$"):
        if m:
            parts.setdefault(m.group(1), {})[m.group(2)] = body
    for fid, p in parts.items():
        if "finding" not in p:
            raise RenderError("%s has no '=== %s finding' block" % (fid, fid))
    return [judge(fid, p, rows) for fid, p in parts.items()]


def lane(findings, entries):
    shown = sorted((d for d in findings if not d["dismissed"]), key=lambda d: (-d["score"], d["num"]))
    gone = [d for d in findings if d["dismissed"]]
    out = "".join(card(d, entries) for d in shown) or '<p class="clean">No findings.</p>'
    if gone:
        out += '<details class="dismissed"><summary>Dismissed by verification (%d)</summary>%s</details>' % (
            len(gone), "".join(card(d, entries) for d in gone))
    return out


# Summary, change entries, findings file

def paths(text):
    """The file paths in a Files or Where value, less any `:line` suffix."""
    found = re.findall(r"`([^`]+)`", text or "") or re.split(r"[,\s]+", text or "")
    return [re.sub(r"^\./|:[\d-]+$", "", p.strip()) for p in found if p.strip()]


def same_file(a, b):
    return a == b or a.endswith("/" + b) or b.endswith("/" + a)


def change_entry(num, title, body):
    parts = split(body, r"#### (Before|Now)\s*$")
    _, f = fields(parts[0][1])
    sides = {m.group(1).lower(): text for m, text in parts[1:]}
    for side in ("before", "now"):
        if side not in sides:
            warnings.append("summary.md: change entry %d has no '#### %s' view" % (num, side.capitalize()))
    if not f.get("Files"):
        warnings.append("summary.md: change entry %d has no Files line, so no finding links to it" % num)
    return dict(num=num, title=title, files=paths(f.get("Files")), why=f.get("Why", ""),
                before=sides.get("before", ""), now=sides.get("now", ""), finding_ids=[])


def load_summary(run, has_stack=True):
    """Overview HTML, change entries, Other changes HTML, reversibility level and notes."""
    path = run / "summary.md"
    if not path.exists():
        warnings.append("summary.md is missing")
        return '<p class="clean">The change summariser returned nothing.</p>', [], "", None, ""
    overview, entries, others, level, notes = "", [], "", None, ""
    for m, body in split(path.read_text(), r"### (.+?)\s*$"):
        name = m.group(1).strip() if m else ""
        entry = re.match(r"(?i)change:\s*(.+)", name)
        if name.lower() == "overview":
            overview = md(body)
        elif name.lower() == "reversibility":
            lv = re.match(r"(?:- \*\*)?Level:?\**:?\s*(.+)", body)
            level = LEVELS.get(lv.group(1).strip().lower().rstrip(".")) if lv else None
            notes = body[lv.end():] if lv else body
        elif entry:
            entries.append(change_entry(len(entries) + 1, entry.group(1), body))
        elif name.lower() == "other changes":
            others = md(body)
        elif m:
            overview += "<h3>%s</h3>%s" % (inline(name), md(body))
    if level is None and has_stack:
        warnings.append("summary.md has no Reversibility level in the brief's shape")
    if not entries and not others:
        warnings.append("summary.md has no change entries and no Other changes")
    return overview, entries, others, level, notes


def link_findings(entries, findings):
    """Give each change entry the findings shown in the report whose file it lists."""
    for e in entries:
        mine = [d for d in findings if not d["dismissed"]
                and any(same_file(w, f) for w in paths(d["f"].get("Where")) for f in e["files"])]
        e["finding_ids"] = [d["id"] for d in sorted(mine, key=lambda d: (-d["score"], "ATQ".index(d["id"][0]), d["num"]))]


def summary_html(overview, entries):
    index = "".join('<li><a href="#change-%d">%s</a></li>' % (e["num"], inline(e["title"])) for e in entries)
    return overview + ('<ol class="change-index">%s</ol>' % index if index else "")


def changes_html(entries, others, by_id):
    out = []
    for e in entries:
        found = " · ".join('<a href="#finding-%s">%s</a> (%d/10)' % (i, i, by_id[i]["score"]) for i in e["finding_ids"])
        out.append(
            '<article class="change" id="change-%d"><h3><span class="num">%d</span> %s</h3>%s'
            '<div class="pair"><div><h4>Before</h4>%s</div><div><h4>Now</h4>%s</div></div>'
            '<p class="meta">Files: %s</p>%s</article>' % (
                e["num"], e["num"], inline(e["title"]),
                '<p class="why">%s</p>' % inline(e["why"]) if e["why"] else "",
                md(e["before"]), md(e["now"]),
                ", ".join("<code>%s</code>" % esc(f) for f in e["files"]) or "none given",
                '<p class="meta">Findings: %s</p>' % found if found else ""))
    if others:
        out.append('<h3 id="other-changes">Other changes</h3>' + others)
    return "".join(out) or '<p class="clean">No change entries.</p>'


def findings_file(meta, findings, report, level, run):
    out = ["# Findings: " + meta["Target"], ""]
    out += ["- %s: %s" % (k, v) for k, v in (
        ("Repo", meta["Repo"]), ("Branch", meta["Branch"]), ("Report", report),
        ("Stack", re.sub(r"\s*\(.*\)$", "", meta["Stack"])), ("Base", meta["Base"]), ("Head", meta["Head"]),
        ("Uncommitted", meta["Uncommitted"]), ("Reversibility", level or "unknown"))]
    out += ["- Re-review: yes"] if meta.get("Re-review") == "yes" else []
    out += ["", "## Findings", ""] + ([] if findings else ["No findings.", ""])
    for d in sorted(findings, key=lambda d: ("ATQ".index(d["id"][0]), d["num"])):
        p = d["parts"]
        out += ["### " + d["id"], "- **Status:** " + d["status"], "- **Score:** %d (%s)" % (d["score"], band(d["score"]))] + (
                ["- **Origin:** " + d["origin"]] if d["origin"] else []) + ["", p["finding"], ""] + ([p["verdict"], ""] if p.get("verdict") else []) + (
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
    walkthrough, has_stack = meta.get("Walkthrough") == "yes", not re.match(r"none\b", meta["Stack"])
    out_dir.mkdir(parents=True, exist_ok=True)
    report, findings_md = out_dir.absolute() / (run.name + ".html"), out_dir.absolute() / (run.name + ".findings.md")
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    heads, context = fix_context(run)
    findings = [] if walkthrough else load_findings(run, context if meta.get("Re-review") == "yes" else None)
    overview, entries, others, level, notes = load_summary(run, has_stack)
    link_findings(entries, findings)
    rev = '<span class="rev %s">%s</span>' % (LEVEL_CLASS[level], level) if level else ""
    values = {
        "KIND": "Walkthrough" if walkthrough else "Code review", "TARGET_TITLE": esc(meta["Target"]), "REPO": esc(meta["Repo"]), "MODE": esc(meta["Mode"]),
        "STACK": esc(meta["Stack"]), "STACK_SETTINGS": esc(meta.get("Stack settings", "none")),
        "BASE": esc(meta["Base"]), "HEAD": esc(meta["Head"]), "DATE": date,
        "SUMMARY": summary_html(overview, entries), "CHANGES": changes_html(entries, others, {d["id"]: d for d in findings}),
        "RE_REVIEW": " · re-review of one fix run" if meta.get("Re-review") == "yes" else "",
        "REVERSIBILITY_BADGE": " · " + rev if rev and has_stack else "",
        "REVERSIBILITY": "<p>%s</p>%s" % (rev, md(notes)) if rev else '<p class="clean">No reversibility given.</p>',
        "EARLIER": ('<section id="earlier"><h2>Earlier findings</h2><table class="earlier"><tr>%s</tr>%s</table></section>' % (
            "".join("<th>%s</th>" % esc(h) for h in heads),
            "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(row.get(h, "")) for h in heads) for row in context))) if context else "",
    }
    for letter, key in LANES.items():
        mine = [d for d in findings if d["id"][0] == letter]
        values["FINDINGS_" + key] = lane(mine, entries)
        for b in ("Blocking", "Should-fix", "Nit"):
            values["%s_%s" % (key, b.upper().replace("-", "_"))] = str(sum(1 for d in mine if not d["dismissed"] and band(d["score"]) == b))
        values[key + "_DISMISSED"] = str(sum(d["dismissed"] for d in mine))

    template = keep((HERE / "report-template.html").read_text(), {"review": not walkthrough, "reversibility": has_stack})
    report.write_text(fill(template, values))
    if walkthrough:
        return report, None, findings
    findings_md.write_text(findings_file(meta, findings, report, level, run))
    return report, findings_md, findings


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        report, findings_md, findings = render(
            pathlib.Path(argv[1]).absolute(), pathlib.Path(argv[2] if len(argv) == 3 else "/tmp/rt-code-review"))
    except RenderError as e:
        print("error: %s" % e, file=sys.stderr)
        return 1
    print("report: %s" % report + ("\nfindings: %s" % findings_md if findings_md else ""))
    for d in findings:
        print("finding: %s %s %d/10%s" % (d["id"], d["status"], d["score"], " · " + d["origin"] if d["origin"] else ""))
    print("".join("warning: %s\n" % w for w in warnings), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
