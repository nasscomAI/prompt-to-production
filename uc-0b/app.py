"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_PATTERN = re.compile(r"^(\d+)\.\s+([A-Z].+)$")
VERBATIM_CLAUSES = {"2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}


def retrieve_policy(input_path: str) -> list[dict]:
    """Load the policy document and return structured numbered sections and clauses."""
    lines = Path(input_path).read_text(encoding="utf-8").splitlines()
    sections: list[dict] = []
    current_section: dict | None = None
    current_clause: dict | None = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("═"):
            continue

        section_match = SECTION_PATTERN.match(stripped)
        clause_match = CLAUSE_PATTERN.match(stripped)

        if section_match and not clause_match:
            current_section = {
                "section_number": section_match.group(1),
                "section_title": section_match.group(2),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
            continue

        if clause_match:
            if current_section is None:
                raise ValueError(f"Clause found before section heading: {stripped}")
            current_clause = {
                "clause_number": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
            current_section["clauses"].append(current_clause)
            continue

        if current_clause is not None:
            current_clause["text"] += " " + stripped

    return sections


def _normalize_clause_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def summarize_policy(sections: list[dict]) -> str:
    """Create a clause-preserving summary with references and verbatim flags."""
    output_lines = [
        "HR Leave Policy Summary",
        "Source: policy_hr_leave.txt",
        "Method: clause-preserving summary with verbatim flags for high-risk obligations.",
        "",
    ]

    for section in sections:
        output_lines.append(f"Section {section['section_number']}: {section['section_title']}")
        for clause in section["clauses"]:
            clause_number = clause["clause_number"]
            clause_text = _normalize_clause_text(clause["text"])
            if clause_number in VERBATIM_CLAUSES:
                output_lines.append(f"- {clause_number} [VERBATIM]: {clause_text}")
            else:
                output_lines.append(f"- {clause_number}: {clause_text}")
        output_lines.append("")

    return "\n".join(output_lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary_text = summarize_policy(sections)
    Path(args.output).write_text(summary_text, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
