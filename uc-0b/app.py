"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path


CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_START = re.compile(r"^(\d+)\.\s+(.+)$")


def retrieve_policy(input_path):
    """Return policy sections as dictionaries containing ordered clauses."""
    sections = []
    current_section = None
    current_clause = None

    for raw_line in Path(input_path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or set(line) in ({"="}, {"═"}):
            continue

        clause_match = CLAUSE_START.match(line)
        section_match = SECTION_START.match(line)
        if section_match and not clause_match:
            current_section = {
                "number": section_match.group(1),
                "title": section_match.group(2),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
        elif clause_match:
            if current_section is None:
                raise ValueError(f"Clause {clause_match.group(1)} has no section")
            current_clause = [clause_match.group(1), clause_match.group(2)]
            current_section["clauses"].append(current_clause)
        elif current_clause is not None:
            current_clause[1] += " " + line

    if not sections or not any(section["clauses"] for section in sections):
        raise ValueError("Input does not contain numbered policy clauses")
    return sections


def summarize_policy(sections):
    """Render every retrieved clause without changing its conditions."""
    lines = ["EMPLOYEE LEAVE POLICY - CLAUSE-PRESERVING SUMMARY", ""]
    for section in sections:
        lines.append(f"{section['number']}. {section['title']}")
        for reference, text in section["clauses"]:
            lines.append(f"- {reference}: {text}")
        lines.append("")

    summary = "\n".join(lines).rstrip() + "\n"
    clause_count = sum(len(section["clauses"]) for section in sections)
    rendered_count = len(re.findall(r"(?m)^- \d+\.\d+: ", summary))
    if rendered_count != clause_count:
        raise ValueError("Summary clause count does not match retrieved policy")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Create a clause-preserving policy summary")
    parser.add_argument("--input", required=True, help="Path to the policy text file")
    parser.add_argument("--output", required=True, help="Path for the summary text file")
    args = parser.parse_args()

    summary = summarize_policy(retrieve_policy(args.input))
    Path(args.output).write_text(summary, encoding="utf-8")

if __name__ == "__main__":
    main()
