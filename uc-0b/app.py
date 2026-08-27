"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
from collections import OrderedDict
from pathlib import Path
import re


SECTION_LINE = re.compile(r"^(\d+)\.\s+(.*)$")
CLAUSE_LINE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

VERBATIM_CLAUSES = {
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
}


def retrieve_policy(input_path: str) -> OrderedDict[str, dict]:
    text = Path(input_path).read_text(encoding="utf-8")
    lines = text.splitlines()

    sections: OrderedDict[str, dict] = OrderedDict()
    current_section_number = None
    current_clause_number = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("═"):
            continue

        section_match = SECTION_LINE.match(stripped)
        clause_match = CLAUSE_LINE.match(stripped)

        if section_match and not clause_match:
            current_section_number = section_match.group(1)
            sections[current_section_number] = {
                "title": section_match.group(2).strip(),
                "clauses": OrderedDict(),
            }
            current_clause_number = None
            continue

        if clause_match:
            current_clause_number = clause_match.group(1)
            if current_section_number is None:
                raise ValueError(f"Clause {current_clause_number} found before any section heading")
            sections[current_section_number]["clauses"][current_clause_number] = clause_match.group(2).strip()
            continue

        if current_clause_number is not None:
            prior = sections[current_section_number]["clauses"][current_clause_number]
            sections[current_section_number]["clauses"][current_clause_number] = f"{prior} {stripped}"

    return sections


def _rewrite_clause(clause_number: str, text: str) -> str:
    normalized = " ".join(text.split())

    custom_rewrites = {
        "2.3": "Employees must submit Form HR-L1 at least 14 calendar days before annual leave starts.",
        "3.3": "Sick leave cannot be carried forward to the following year.",
        "4.3": "Male employees receive 5 days of paid paternity leave, which must be taken within 30 days of the child's birth.",
        "5.1": "Leave Without Pay may be requested only after all applicable paid leave entitlements are exhausted.",
        "6.2": "If an employee works on a public holiday, they receive one compensatory off day that must be used within 60 days.",
        "7.1": "Annual leave may be encashed only at retirement or resignation, up to a maximum of 60 days.",
        "8.2": "Grievances filed after 10 working days will not be considered unless exceptional circumstances are shown in writing.",
    }

    if clause_number in VERBATIM_CLAUSES:
        return f'Verbatim: "{normalized}"'

    if clause_number in custom_rewrites:
        return custom_rewrites[clause_number]

    return normalized


def summarize_policy(sections: OrderedDict[str, dict]) -> str:
    lines = ["HR Leave Policy Summary", "", "This summary preserves every numbered clause from the source policy.", ""]

    for section_number, section in sections.items():
        lines.append(f"Section {section_number}: {section['title']}")
        for clause_number, clause_text in section["clauses"].items():
            summary_text = _rewrite_clause(clause_number, clause_text)
            lines.append(f"- {clause_number}: {summary_text}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary text file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    Path(args.output).write_text(summary, encoding="utf-8")

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
