"""
UC-0B — Policy Summary Generator
"""
import argparse
import os
import re

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    sections = {}
    current_clause = None
    current_lines = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if match:
            if current_clause and current_lines:
                sections[current_clause] = " ".join(current_lines).strip()
            current_clause = match.group(1)
            current_lines = [match.group(2)]
        elif current_clause:
            current_lines.append(line)

    if current_clause and current_lines:
        sections[current_clause] = " ".join(current_lines).strip()

    return sections


def summarize_policy(policy_sections: dict) -> str:
    missing = [clause for clause in REQUIRED_CLAUSES if clause not in policy_sections]
    if missing:
        raise ValueError(f"Missing required clauses: {', '.join(missing)}")

    lines = ["HR Leave Policy Summary"]
    for clause in REQUIRED_CLAUSES:
        lines.append(f"{clause}: {policy_sections[clause]}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()

    policy_sections = retrieve_policy(args.input)
    summary = summarize_policy(policy_sections)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
