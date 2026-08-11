"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path

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


def retrieve_policy(input_path: str) -> dict:
    sections = {}
    current_clause = None
    clause_text = []
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    with open(input_path, encoding="utf-8") as input_file:
        for line in input_file:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            match = clause_pattern.match(line)
            if match:
                if current_clause is not None:
                    sections[current_clause] = " ".join(clause_text).strip()
                current_clause = match.group(1)
                clause_text = [match.group(2).strip()]
            elif current_clause is not None:
                clause_text.append(line.strip())
    if current_clause is not None:
        sections[current_clause] = " ".join(clause_text).strip()
    return sections


def summarize_policy(sections: dict) -> str:
    missing = [clause for clause in REQUIRED_CLAUSES if clause not in sections]
    if missing:
        raise ValueError(f"Missing required clauses in policy: {', '.join(missing)}")

    summary_lines = [
        "HR Leave Policy Summary",
        "========================",
        "",
        "This summary preserves each required numbered clause verbatim to avoid obligation softening or clause omission.",
        "",
    ]
    for clause in REQUIRED_CLAUSES:
        summary_lines.append(f"Clause {clause}: {sections[clause]}")
    summary_lines.append("")
    summary_lines.append("Note: All 10 required clauses are included and multi-condition approvals are preserved exactly.")
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
