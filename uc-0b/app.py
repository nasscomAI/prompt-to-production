"""
UC-0B app.py — Summary app for policy documents.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path
from typing import List, Dict

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(input_path: str) -> List[Dict[str, str]]:
    """Load the policy text and return numbered clauses as structured sections."""
    text = Path(input_path).read_text(encoding="utf-8")
    clauses: List[Dict[str, str]] = []
    current_clause: Dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        match = CLAUSE_PATTERN.match(line)
        if match:
            if current_clause:
                clauses.append(current_clause)

            current_clause = {
                "clause": match.group(1),
                "text": match.group(2).strip(),
            }
        elif current_clause and raw_line.startswith((" ", "\t")):
            current_clause["text"] += " " + line.strip()

    if current_clause:
        clauses.append(current_clause)

    if not clauses:
        raise ValueError(f"No numbered clauses found in {input_path}")

    return clauses


def summarize_policy(sections: List[Dict[str, str]]) -> str:
    """ Produce a compliant summary with every numbered clause referenced."""
    summary_lines: List[str] = []

    for section in sections:
        clause = section["clause"]
        text = " ".join(section["text"].split())
        summary_lines.append(f"Clause {clause}: {text}")

    return "\n".join(summary_lines) + "\n"


def write_summary(output_path: str, summary: str) -> None:
    Path(output_path).write_text(summary, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    write_summary(args.output, summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
