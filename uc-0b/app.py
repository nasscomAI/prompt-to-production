"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path
from typing import Optional


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_PATTERN = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s\-/&()]+)$")
RISKY_TERMS = ("must", "requires", "not permitted", "forfeited", "approval", "within", "only", "regardless")


def retrieve_policy(input_path: str) -> list[dict]:
    lines = Path(input_path).read_text(encoding="utf-8").splitlines()
    sections: list[dict] = []
    current_section: Optional[dict] = None
    current_clause: Optional[dict] = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or set(stripped) == {"═"}:
            continue

        section_match = SECTION_PATTERN.match(stripped)
        if section_match:
            current_section = {
                "number": section_match.group(1),
                "title": section_match.group(2).title(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
            continue

        clause_match = CLAUSE_PATTERN.match(stripped)
        if clause_match and current_section is not None:
            current_clause = {
                "number": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
            current_section["clauses"].append(current_clause)
            continue

        if current_clause is not None:
            current_clause["text"] += " " + stripped

    if not any(section["clauses"] for section in sections):
        raise ValueError("No numbered clauses found in policy document")

    return sections


def _summarize_clause(clause_text: str) -> tuple[str, bool]:
    normalized = " ".join(clause_text.split())
    lowered = normalized.lower()
    if any(term in lowered for term in RISKY_TERMS) or ";" in normalized:
        return normalized, True
    return normalized, False


def summarize_policy(sections: list[dict]) -> str:
    output_lines = ["Policy Summary", "==============", ""]

    for section in sections:
        output_lines.append(f"Section {section['number']}: {section['title']}")
        for clause in section["clauses"]:
            summary_text, verbatim = _summarize_clause(clause["text"])
            prefix = "VERBATIM" if verbatim else "SUMMARY"
            output_lines.append(f"- {clause['number']} [{prefix}] {summary_text}")
        output_lines.append("")

    return "\n".join(output_lines).rstrip() + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    Path(args.output).write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
