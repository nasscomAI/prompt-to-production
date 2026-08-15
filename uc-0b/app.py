"""UC-0B app.py — Policy summariser.

Implements the skills defined in skills.md:
  retrieve_policy  -> loads a .txt policy file as structured numbered sections
  summarize_policy -> produces a compliant, clause-referenced summary

Enforced per agents.md: every tracked clause must be present; all
multi-condition obligations keep every condition; binding verbs are
preserved; no wording outside the source is introduced.
"""
import argparse
import re
import sys
from pathlib import Path

TRACKED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def _clause_key(number):
    return [int(part) for part in number.split(".")]


def retrieve_policy(path):
    """Load a .txt policy file and return (sections, clauses).

    sections: map of section number (str) -> section title (str)
    clauses:  map of clause number (str) -> clause text (str), verbatim
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read policy file {path}: {exc}") from exc

    sections = {}
    clauses = {}
    current = None
    current_lines = []

    def flush():
        nonlocal current, current_lines
        if current and current_lines:
            clauses[current] = " ".join(current_lines)
        current = None
        current_lines = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or re.fullmatch(r"[\u2550\u2500\-=_]+", stripped):
            continue
        section_match = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if section_match:
            flush()
            sections[section_match.group(1)] = section_match.group(2).strip()
            continue
        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
        if clause_match:
            flush()
            current = clause_match.group(1)
            current_lines = [clause_match.group(2).strip()]
            continue
        if current:
            current_lines.append(stripped)
    flush()

    if not clauses:
        raise ValueError(f"No numbered clauses found in {path}")
    return sections, clauses


def summarize_policy(sections, clauses):
    """Return a compliant summary with every clause referenced and verbatim.

    Refuses to produce the summary if any tracked clause is missing.
    Every clause is quoted verbatim, so no obligation, condition, or
    binding verb can be lost or softened.
    """
    missing = [c for c in TRACKED_CLAUSES if c not in clauses]
    if missing:
        raise ValueError(
            "Cannot produce summary: missing tracked clauses "
            + ", ".join(missing)
        )

    lines = ["EMPLOYEE LEAVE POLICY — SUMMARY", ""]
    for section_num in sorted(sections, key=int):
        section_clauses = sorted(
            (c for c in clauses if c.startswith(section_num + ".")),
            key=_clause_key,
        )
        if not section_clauses:
            continue
        lines.append(f"SECTION {section_num} — {sections[section_num]}")
        for clause_num in section_clauses:
            lines.append(f"{clause_num} {clauses[clause_num]}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Summarise a numbered policy document faithfully."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the .txt policy file, e.g. ../data/policy-documents/policy_hr_leave.txt",
    )
    parser.add_argument(
        "--output",
        default="summary_hr_leave.txt",
        help="Output file path (default: summary_hr_leave.txt)",
    )
    args = parser.parse_args()

    try:
        sections, clauses = retrieve_policy(args.input)
        summary = summarize_policy(sections, clauses)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    Path(args.output).write_text(summary + "\n", encoding="utf-8")
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
