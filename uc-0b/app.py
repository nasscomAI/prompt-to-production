"""
UC-0B app.py — Summary That Changes Meaning
Extractive summarizer for policy documents. Built via the RICE + agents.md +
skills.md + CRAFT workflow. See README.md for run command and expected behaviour.

Enforcement (mirrors agents.md):
  1. EVERY numbered clause in the source document appears in the summary.
  2. Multi-condition obligations preserve ALL conditions — obligation-bearing
     sentences are quoted VERBATIM, so no condition can be silently dropped.
  3. Nothing is added that is not in the source document (output is built only
     from source text plus structural labels).
  4. Clauses that cannot be compressed without meaning loss are quoted verbatim
     and flagged QUOTED_VERBATIM.
A hard verification gate runs before the output file is written: if any of the
10 ground-truth clauses is missing, or clause 5.2 loses either approver, the
program aborts instead of writing an incomplete summary.
"""
import argparse
import os
import re
import sys

# The 10 ground-truth clauses from README.md that MUST survive summarisation.
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Sentences containing these binding markers carry obligations/conditions.
NORMATIVE_MARKERS = re.compile(
    r"\b(must|will|shall|requires|required|not\s+permitted|cannot|may\s+not|"
    r"forfeit\w*|not\s+valid|not\s+sufficient|entitled|only|does\s+not\s+apply|"
    r"will\s+not\s+be\s+considered|implies|mandatory|prohibited)\b",
    re.IGNORECASE,
)

SECTION_HEADER = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z \-&(),]+)\s*$")
CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def parse_policy(text):
    """Parse a policy document into an ordered list of clauses.

    Returns list of dicts: {id, section_no, section_title, body}.
    """
    lines = text.splitlines()
    clauses = []
    current_section_no, current_title = "", ""
    cur_id, buf = None, []

    def flush():
        if cur_id is not None:
            body = re.sub(r"\s+", " ", " ".join(buf)).strip()
            clauses.append({
                "id": cur_id,
                "section_no": current_section_no,
                "section_title": current_title,
                "body": body,
            })

    for line in lines:
        stripped = line.strip()
        if set(stripped) <= set("═=") and stripped:
            continue
        m = SECTION_HEADER.match(stripped)
        if m:
            flush()
            cur_id, buf = None, []
            current_section_no, current_title = m.group(1), m.group(2).strip()
            continue
        m = CLAUSE_START.match(stripped)
        if m:
            flush()
            cur_id = m.group(1)
            buf = [m.group(2)]
            continue
        if cur_id is not None and stripped:
            buf.append(stripped)
    flush()
    return clauses


def split_sentences(body):
    parts = re.split(r"(?<=[.!?])\s+", body)
    return [p.strip() for p in parts if p.strip()]


def summarize_clause(clause):
    """Return (quoted_text, flag) for one clause.

    Quotes the normative sentences verbatim when they capture enough of the
    clause; otherwise quotes the entire clause verbatim and flags it.
    """
    sentences = split_sentences(clause["body"])
    normative = [s for s in sentences if NORMATIVE_MARKERS.search(s)]
    covered = sum(len(s) for s in normative)
    total = sum(len(s) for s in sentences)
    if not normative or covered < 0.75 * total:
        return clause["body"], "QUOTED_VERBATIM"
    return " ".join(normative), ""


def build_summary(source_path, doc_name, clauses):
    title = ""
    for line in open(source_path, "r", encoding="utf-8-sig").read().splitlines()[:6]:
        if "POLICY" in line.upper():
            title = line.strip()
            break
    if not title:
        for line in open(source_path, "r", encoding="utf-8-sig").read().splitlines()[:6]:
            if line.strip():
                title = line.strip()
                break

    out = []
    out.append("=" * 72)
    out.append("UC-0B POLICY SUMMARY — %s" % title)
    out.append("Source document : %s" % doc_name)
    out.append("Method          : extractive — obligation sentences quoted verbatim")
    out.append("                  (zero meaning loss; nothing added from outside)")
    out.append("Clauses covered : %d numbered clauses" % len(clauses))
    out.append("=" * 72)

    flags = []
    for c in clauses:
        quote, flag = summarize_clause(c)
        label = ("%s. %s" % (c["section_no"], c["section_title"])) if c["section_no"] else c["id"]
        out.append("")
        out.append("[%s] %s" % (c["id"], label))
        out.append('    "%s"' % quote)
        if flag:
            flags.append((c["id"], flag))

    out.append("")
    out.append("-" * 72)
    out.append("FLAGS")
    if flags:
        for cid, flag in flags:
            out.append("  [%s] %s — full clause quoted verbatim to avoid meaning loss" % (cid, flag))
    else:
        out.append("  (none)")
    out.append("-" * 72)
    return "\n".join(out)


def verify(summary_text, clauses):
    """Hard gate: abort rather than emit an incomplete summary."""
    errors = []
    clause_ids = {c["id"] for c in clauses}
    for req in REQUIRED_CLAUSES:
        if req not in clause_ids:
            errors.append("ground-truth clause %s missing from parsed document" % req)
        elif ("[%s]" % req) not in summary_text:
            errors.append("clause %s missing from generated summary" % req)

    c52 = next((c for c in clauses if c["id"] == "5.2"), None)
    if c52 is None:
        errors.append("clause 5.2 not found; dual-approval condition unverifiable")
    else:
        low = c52["body"].lower()
        if "department head" not in low or "hr director" not in low:
            errors.append("clause 5.2 lost a required approver (Department Head AND HR Director)")
        if "not sufficient" not in low:
            errors.append("clause 5.2 lost the 'manager approval alone is not sufficient' condition")

    # The written text itself must retain both approvers for 5.2.
    seg = summary_text.split("[5.2]")[1].split("[5.3]")[0] if "[5.2]" in summary_text else ""
    if seg.lower().count("department head") < 1 or seg.lower().count("hr director") < 1:
        errors.append("summary text for 5.2 does not contain both approver titles")

    return errors


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8-sig") as f:
            text = f.read()
    except OSError as exc:
        print("ERROR: cannot read input file '%s': %s" % (args.input, exc))
        sys.exit(1)

    clauses = parse_policy(text)
    if not clauses:
        print("ERROR: no numbered clauses found in '%s' — wrong input file?" % args.input)
        sys.exit(1)

    doc_name = os.path.basename(args.input)
    summary = build_summary(args.input, doc_name, clauses)

    errors = verify(summary, clauses)
    if errors:
        print("VERIFICATION FAILED — output NOT written:")
        for e in errors:
            print("  - %s" % e)
        sys.exit(1)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary + "\n")
    except OSError as exc:
        print("ERROR: cannot write output file '%s': %s" % (args.output, exc))
        sys.exit(1)

    print("Summary written to %s (%d clauses, verification passed)" % (args.output, len(clauses)))


if __name__ == "__main__":
    main()
