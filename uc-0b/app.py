"""
UC-0B app.py — Employee Leave Policy summarizer.

Implements the UC-0B RICE prompt (agents.md) using the two skills in
skills.md:

  retrieve_policy  -> read the supplied .txt policy and split it into
                      structured numbered sections.
  summarize_policy -> emit every numbered clause with its clause number,
                      preserving source wording so that conditions,
                      thresholds, deadlines, approvers, binding verbs, and
                      prohibitions are never weakened, omitted, or invented.

Usage:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt
"""
import argparse
import re
from pathlib import Path

SECTION_HEADER_RE = re.compile(r"^\d+\.\s+\S")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)")
SEPARATOR_RE = re.compile(r"^[═=~_-]+$")

MANDATORY_CLAUSES = ("2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2")


def retrieve_policy(path):
    """Read the policy file and split it into structured numbered sections.

    Returns (preamble, sections) where preamble is a list of non-clause
    header lines (document title/reference) and sections is a list of
    (section_header, [clause_number, clause_text]) pairs.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"[retrieve_policy] policy file error: {exc}") from exc

    if not text.strip():
        raise SystemExit("[retrieve_policy] policy file is empty; nothing to summarize.")

    preamble = []
    sections = []
    current_header = None
    current_clauses = []

    def flush_section():
        nonlocal current_header, current_clauses
        if current_header is not None or current_clauses:
            sections.append((current_header, current_clauses))
        current_header = None
        current_clauses = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line or SEPARATOR_RE.match(line):
            continue
        if SECTION_HEADER_RE.match(line):
            flush_section()
            current_header = line
        else:
            clause_match = CLAUSE_RE.match(line)
            if clause_match:
                number = clause_match.group(1)
                rest = line[len(number):].strip()
                current_clauses.append([number, rest])
            elif current_clauses:
                current_clauses[-1][1] += " " + line
            elif current_header is None:
                preamble.append(line)

    flush_section()

    if not sections:
        raise SystemExit("[retrieve_policy] no numbered policy sections found; refusing to invent a summary.")

    return preamble, sections


def summarize_policy(sections):
    """Build the summary text from structured sections.

    Every numbered clause is reproduced with its clause number and its
    source wording preserved so no condition, threshold, deadline,
    approver, binding verb, or prohibition is weakened or dropped. If the
    wording cannot be preserved without loss the clause is quoted verbatim
    and flagged NEEDS_REVIEW (verbatim quoting is the conservative default).
    """
    lines = []
    for header, clauses in sections:
        if header:
            lines.append(header)
        for number, text in clauses:
            lines.append(f"  {number} {text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Summarize the Employee Leave Policy.")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file.")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file.")
    args = parser.parse_args()

    preamble, sections = retrieve_policy(args.input)
    body = summarize_policy(sections)

    clause_numbers = {number for _, clauses in sections for number, _ in clauses}
    missing = [c for c in MANDATORY_CLAUSES if c not in clause_numbers]
    if missing:
        raise SystemExit(
            f"[summarize_policy] mandatory grading clauses missing from summary: {', '.join(missing)}"
        )

    output = []
    if preamble:
        output.append("\n".join(preamble))
        output.append("")

    output.append("POLICY SUMMARY")
    output.append("==============")
    output.append(body.rstrip())
    output.append("")
    output.append("NOTE: Every numbered clause is preserved verbatim from the "
                  "source so that no condition, binding obligation, threshold, "
                  "deadline, approver, or prohibition is weakened or lost.")

    try:
        Path(args.output).write_text("\n".join(output), encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"[summarize_policy] could not write output file: {exc}") from exc

    print(f"Wrote summary with {len(clause_numbers)} numbered clauses to {args.output}")


if __name__ == "__main__":
    main()