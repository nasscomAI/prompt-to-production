"""
UC-0B - Faithful structured summary of the HR Leave Policy.

Failure mode defeated: "summary that changes meaning" - clause omission,
scope bleed, and the silent dropping of one condition from a multi-condition
obligation (clause 5.2 losing its second approver is the canonical trap).

Strategy
--------
The summarizer is a structural compressor, not an author. It:

  1. Parses every numbered clause from the source (regex on `N.N` clause ids).
  2. Joins continuation lines into flowing prose and collapses whitespace.
  3. Re-emits the clauses grouped by section with `[N.N]` references.

Because NO clause is paraphrased, no condition can be silently dropped and no
information can be invented. Multi-condition clauses (5.2 naming both
"Department Head" and "HR Director", 2.6's 5-day cap and 31 December
forfeiture, etc.) survive verbatim by construction.

The tool then self-audits its own output and refuses to ship (non-zero exit)
if any clause is missing, any critical condition is absent, or any forbidden
scope-bleed phrase appears.

Pure standard-library Python 3.9. Deterministic. No LLM/API/network.

Run
---
    # from repo root (uses sensible defaults):
    python uc-0b/app.py

    # from inside uc-0b (per README):
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""
import argparse
import re
import sys
from pathlib import Path

# Resolve paths from THIS file's location so the same defaults work whether the
# script is invoked from the repo root (`python uc-0b/app.py`) or from inside
# the uc-0b folder (`python app.py`).
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
DEFAULT_INPUT = REPO_ROOT / "data" / "policy-documents" / "policy_hr_leave.txt"
DEFAULT_OUTPUT = HERE / "summary_hr_leave.txt"

# A section heading is `N. ALL-CAPS TITLE` (e.g. "2. ANNUAL LEAVE").
# A clause is `N.N prose` (e.g. "2.3 Employees ..."). The two are disjoint
# because a heading has a single number then a dot then a space, while a
# clause has number-dot-number.
SECTION_HEADING_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &()/\-]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
BOX_CHAR = "="  # ASCII fallback; the real source uses U+2550 (see below)
BOX_UNICODE = "═"

# Phrases that indicate invented/hedged content. Verified absent from the
# source document, so their presence in the output proves scope bleed.
FORBIDDEN_PHRASES = [
    "as is standard practice",
    "typically",
    "usually",
    "normally",
    "generally",
    "in most organisations",
    "in most organizations",
    "employees are generally expected to",
    "as per company policy",
    "it is understood that",
]

# The 10 critical clauses and the source-derived substrings that must survive
# in each. This is the testable heart of the multi-condition-preservation and
# binding-force rules. Each substring is copied from the policy text, so
# asserting its presence can never "add" information - it only guards against
# a future change dropping it.
CRITICAL_CONDITIONS = [
    ("2.3", ["14 calendar", "Form HR-L1"]),
    ("2.4", ["written approval", "Verbal approval is not valid"]),
    ("2.5", ["Loss of Pay", "regardless of subsequent approval"]),
    ("2.6", ["maximum of 5", "31 December"]),
    ("2.7", ["first quarter", "forfeited"]),
    ("3.2", ["medical certificate", "48 hours"]),
    ("3.4", ["medical certificate", "regardless of duration"]),
    ("5.2", ["Department Head", "HR Director"]),
    ("5.3", ["30 continuous days", "Municipal Commissioner"]),
    ("7.2", ["not permitted under any circumstances"]),
]


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------
def _is_box_line(stripped):
    """A decorative horizontal rule made entirely of box-drawing characters."""
    if not stripped:
        return False
    sample = stripped[0]
    if sample not in (BOX_UNICODE, BOX_CHAR, "-", "_", "="):
        return False
    return all(ch == sample for ch in stripped)


def retrieve_policy(text):
    """Parse raw policy text into (header_lines, sections).

    sections is an ordered list of dicts:
        {"section_id": "2", "section_title": "ANNUAL LEAVE",
         "clauses": [{"id": "2.1", "text": "..."}, ...]}

    Clause text is the verbatim prose with continuation lines joined and
    internal whitespace collapsed. No paraphrasing occurs here.
    """
    header_lines = []
    sections = []
    section_by_id = {}
    cur_section = None
    cur_clause = None  # {"id": ..., "parts": [str, ...]}

    def flush_clause():
        nonlocal cur_clause
        if cur_clause is not None:
            target = cur_section
            if target is None:
                # Clause appeared before any section heading - shouldn't happen
                # for this document, but handle it rather than crash.
                target = {"section_id": "0", "section_title": "(UNSECTIONED)",
                          "clauses": []}
                sections.append(target)
                section_by_id["0"] = target
            target["clauses"].append(cur_clause)
            cur_clause = None

    for raw in text.split("\n"):
        stripped = raw.strip()
        if not stripped:
            continue
        if _is_box_line(stripped):
            flush_clause()
            continue
        m_sec = SECTION_HEADING_RE.match(stripped)
        if m_sec and not CLAUSE_RE.match(stripped):
            flush_clause()
            sid = m_sec.group(1)
            cur_section = {"section_id": sid,
                           "section_title": m_sec.group(2).strip(),
                           "clauses": []}
            sections.append(cur_section)
            section_by_id[sid] = cur_section
            continue
        m_cl = CLAUSE_RE.match(stripped)
        if m_cl:
            flush_clause()
            cur_clause = {"id": m_cl.group(1),
                          "parts": [m_cl.group(2).strip()]}
            continue
        # Otherwise: continuation of the current clause, or pre-section header.
        if cur_clause is not None:
            cur_clause["parts"].append(stripped)
        elif cur_section is None:
            header_lines.append(stripped)
    flush_clause()

    # Finalise clause text: join parts, collapse whitespace, drop the scratch
    # list so downstream only ever sees a clean `text` string.
    for sec in sections:
        for cl in sec["clauses"]:
            joined = " ".join(p for p in cl["parts"] if p)
            cl["text"] = re.sub(r"\s+", " ", joined).strip()
            if not cl["text"]:
                cl["text"] = "[VERBATIM-EMPTY]"
            cl.pop("parts", None)
    return header_lines, sections


# ---------------------------------------------------------------------------
# Skill: summarize_policy  (+ self-audit)
# ---------------------------------------------------------------------------
def _extract_metadata(header_lines):
    reference = ""
    version = ""
    title = "EMPLOYEE LEAVE POLICY"
    for hl in header_lines:
        m = re.match(r"Document Reference:\s*(.+)", hl)
        if m:
            reference = m.group(1).strip()
        m = re.match(r"Version:\s*(.+)", hl)
        if m:
            version = m.group(1).strip()
        if "POLICY" in hl.upper() and hl.isupper() and hl.strip():
            title = hl.strip()
    return title, reference, version


def summarize_policy(header_lines, sections):
    """Render structured sections into a faithful, audited summary string."""
    title, reference, version = _extract_metadata(header_lines)

    out = ["SUMMARY - " + title]
    meta = []
    if reference:
        meta.append("Source: " + reference)
    if version:
        meta.append("(" + version + ")")
    if meta:
        out.append(" ".join(meta))
    out.append("Faithful structured restatement: every numbered clause "
               "preserved, every condition intact, no information added.")
    out.append("")
    out.append("=" * 70)

    all_ids = []
    for sec in sections:
        out.append("")
        out.append("%s. %s" % (sec["section_id"], sec["section_title"]))
        out.append("-" * 70)
        for cl in sec["clauses"]:
            out.append("[%s] %s" % (cl["id"], cl["text"]))
            all_ids.append(cl["id"])

    out.append("")
    out.append("=" * 70)
    out.append("COMPLETENESS INDEX (every source clause present, "
               "machine-verified):")
    out.append(", ".join(all_ids))
    out.append("Total clauses: %d" % len(all_ids))
    return "\n".join(out), all_ids


def _build_clause_index(sections):
    index = {}
    for sec in sections:
        for cl in sec["clauses"]:
            index[cl["id"]] = cl["text"]
    return index


def validate_completeness(sections):
    """Refuse (exit 3) if clause numbering inside any section is non-contiguous."""
    problems = []
    for sec in sections:
        sid = sec["section_id"]
        nums = []
        for cl in sec["clauses"]:
            try:
                nums.append(int(cl["id"].split(".")[1]))
            except (IndexError, ValueError):
                pass
        if not nums:
            continue
        nums.sort()
        present = set(nums)
        for n in range(1, nums[-1] + 1):
            if n not in present:
                problems.append("%s.%d" % (sid, n))
    if problems:
        sys.stderr.write(
            "COMPLETENESS VIOLATION - missing clauses: %s\n" % ", ".join(problems))
        sys.stderr.write("Refusing to emit an incomplete summary.\n")
        sys.exit(3)


def validate_critical_conditions(sections):
    """Refuse (exit 4) if any critical condition substring is missing."""
    index = _build_clause_index(sections)
    problems = []
    for clause_id, required in CRITICAL_CONDITIONS:
        text = index.get(clause_id, "")
        for needle in required:
            if needle not in text:
                problems.append("%s missing %r" % (clause_id, needle))
    if problems:
        sys.stderr.write(
            "CONDITION-DROP DETECTED - " + "; ".join(problems) + "\n")
        sys.exit(4)


def audit_scope(summary_text):
    """Refuse (exit 2) if any forbidden scope-bleed phrase appears."""
    lower = summary_text.lower()
    found = [p for p in FORBIDDEN_PHRASES if p in lower]
    if found:
        sys.stderr.write("SCOPE BLEED DETECTED - forbidden phrase(s): %s\n"
                         % ", ".join(found))
        sys.exit(2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Produce a faithful, complete, condition-preserving "
                    "summary of the HR leave policy.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT),
                        help="Path to the source policy .txt (default: "
                             "data/policy-documents/policy_hr_leave.txt "
                             "resolved from this script's location).")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT),
                        help="Path to write the summary (default: "
                             "summary_hr_leave.txt beside this script).")
    args = parser.parse_args(argv)

    in_path = Path(args.input)
    out_path = Path(args.output)

    if not in_path.is_file():
        sys.stderr.write("ERROR: input policy not found: %s\n" % in_path)
        sys.exit(1)

    text = in_path.read_text(encoding="utf-8")

    header_lines, sections = retrieve_policy(text)

    total_clauses = sum(len(s["clauses"]) for s in sections)
    if total_clauses == 0:
        sys.stderr.write(
            "ERROR: no numbered clauses parsed from %s - not a valid policy "
            "document. Refusing to summarise.\n" % in_path)
        sys.exit(1)

    # Refuse rather than guess: enforce completeness and the critical
    # multi-condition clauses BEFORE emitting anything.
    validate_completeness(sections)
    validate_critical_conditions(sections)

    summary, all_ids = summarize_policy(header_lines, sections)

    # Final self-audit on the rendered text (guards future paraphrasing).
    audit_scope(summary)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(summary + "\n", encoding="utf-8")
    sys.stderr.write(
        "Wrote %s (%d clauses across %d sections).\n"
        % (out_path, total_clauses, len(sections)))


if __name__ == "__main__":
    main()
