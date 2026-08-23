"""UC-0B — Clause-preserving HR policy summarizer."""

import argparse
import re

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.+)$")


def retrieve_policy(policy_text: str) -> list[tuple[str, str]]:
    """Parse numbered clauses and preserve their complete text."""
    clauses = []
    current_number = None
    current_text = []
    for raw_line in policy_text.splitlines():
        line = raw_line.strip()
        match = CLAUSE_PATTERN.match(line)
        if match:
            if current_number is not None:
                clauses.append((current_number, " ".join(current_text)))
            current_number = match.group(1)
            current_text = [match.group(2)]
        elif current_number is not None and line:
            current_text.append(line)
    if current_number is not None:
        clauses.append((current_number, " ".join(current_text)))
    return clauses


def summarize_policy(policy_text: str) -> str:
    """Return every numbered clause with no dropped conditions."""
    clauses = retrieve_policy(policy_text)
    if not clauses:
        raise ValueError("No numbered policy clauses were found in the input file.")
    return "\n".join(f"Clause {number}: {text}" for number, text in clauses)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B HR policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to summary_hr_leave.txt")
    args = parser.parse_args()
    with open(args.input, encoding="utf-8") as input_file:
        summary = summarize_policy(input_file.read())
    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(summary + "\n")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
