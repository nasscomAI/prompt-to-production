"""
UC-0B app.py — Summary That Changes Meaning.
Build this using the RICE + agents.md + skills.md workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

REQUIRED_CLAUSES = [
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
]

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*\S)")


def retrieve_policy(file_path: str) -> dict:
    """Load a policy file and return numbered clauses with full clause text."""
    clauses = {}
    current_clause = None

    with open(file_path, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.rstrip("\n")
            match = CLAUSE_PATTERN.match(stripped)
            if match:
                current_clause = match.group(1)
                clauses[current_clause] = match.group(2).strip()
                continue
            if current_clause and stripped.strip():
                clauses[current_clause] += " " + stripped.strip()

    return clauses


def summarize_policy(clauses: dict) -> str:
    """Produce a compliant summary for the required numbered clauses."""
    lines = [
        "HR Leave Policy Summary",
        "Summary of the required numbered clauses from the source document:",
        "",
    ]

    for clause_number in REQUIRED_CLAUSES:
        clause_text = clauses.get(clause_number)
        if clause_text is None:
            lines.append(f"{clause_number}: [MISSING CLAUSE TEXT]")
        else:
            lines.append(f"{clause_number}: {clause_text}")

    lines.append("")
    lines.append("Note: required clauses are preserved as sourced to avoid meaning loss.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as output_handle:
        output_handle.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
