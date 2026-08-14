"""
UC-0B policy summarizer.
"""
import argparse
import re

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        lines = handle.readlines()

    clauses = {}
    current_clause = None
    for raw_line in lines:
        line = raw_line.rstrip("\n")
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line.strip())
        if match:
            current_clause = match.group(1)
            clauses[current_clause] = match.group(2).strip()
            continue
        if (
            current_clause
            and line.strip()
            and not re.match(r"^═+", line.strip())
            and not re.match(r"^\d+\.\s+", line.strip())
        ):
            clauses[current_clause] += f" {line.strip()}"

    missing = [clause for clause in REQUIRED_CLAUSES if clause not in clauses]
    if missing:
        raise ValueError(f"Missing required clauses: {', '.join(missing)}")
    return clauses


def summarize_policy(clauses: dict) -> str:
    summary_lines = ["HR Leave Policy Summary", ""]
    for clause in REQUIRED_CLAUSES:
        text = clauses[clause]
        summary_lines.append(f"Clause {clause}: {text}")
    return "\n".join(summary_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
