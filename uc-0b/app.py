"""
UC-0B app.py — Policy summary generator.
Implements skills from uc-0b/skills.md and enforcement from uc-0b/agents.md.
"""
import argparse
import re

REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"
]


def retrieve_policy(file_path: str) -> dict:
    """Loads a policy text file and returns its clauses keyed by clause number."""
    clauses = {}
    current_clause = None
    current_lines = []
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = clause_re.match(line)
            if m:
                # Save previous clause
                if current_clause is not None:
                    clauses[current_clause] = "\n".join(current_lines).strip()
                current_clause = m.group(1)
                current_lines = [m.group(2).strip()]
            elif current_clause is not None:
                # continuation of the current clause
                current_lines.append(line.strip())
    if current_clause is not None:
        clauses[current_clause] = "\n".join(current_lines).strip()

    return clauses


def summarize_policy(clauses: dict, required_clause_ids: list) -> str:
    """Produces a compliant summary that preserves all obligations and conditions."""
    output_lines = []
    for clause_id in required_clause_ids:
        if clause_id not in clauses:
            output_lines.append(f"CLAUSE MISSING: {clause_id} (not found in source document)")
            continue
        clause_text = clauses[clause_id]
        output_lines.append(f"Clause {clause_id}:")
        output_lines.append(clause_text)
        output_lines.append("")
    return "\n".join(output_lines).strip()


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary text file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses, REQUIRED_CLAUSES)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
