import argparse
import re
from typing import Optional


CLAUSE_START = re.compile(r"^(?P<number>\d+\.\d+)\s+(?P<text>.+?)\s*$")


def retrieve_policy(input_path: str) -> list[tuple[str, str]]:
    """Load numbered clauses while preserving their source wording."""
    with open(input_path, "r", encoding="utf-8-sig") as policy_file:
        clauses: list[tuple[str, str]] = []
        current_number: Optional[str] = None
        current_lines: list[str] = []
        for raw_line in policy_file:
            line = raw_line.strip()
            match = CLAUSE_START.match(line)
            if match:
                if current_number is not None:
                    clauses.append((current_number, " ".join(current_lines)))
                current_number = match.group("number")
                current_lines = [match.group("text")]
            elif current_number is not None and re.match(r"^\d+\.\s+", line):
                continue
            elif current_number is not None and line and not set(line) <= {"═", "-", "="}:
                current_lines.append(line)
        if current_number is not None:
            clauses.append((current_number, " ".join(current_lines)))

    if not clauses:
        raise ValueError("Policy file contains no numbered clauses")
    return clauses


def summarize_policy(clauses: list[tuple[str, str]]) -> str:
    """Create a clause-complete summary without changing source conditions."""
    lines = [
        "HR Leave Policy Summary",
        "The following summary preserves each numbered clause from the source document.",
        "",
    ]
    lines.extend(f"Clause {number}: {text}" for number, text in clauses)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B policy summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy text file")
    parser.add_argument("--output", required=True, help="Path to the summary text file")
    args = parser.parse_args()
    clauses = retrieve_policy(args.input)
    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(summarize_policy(clauses))
    print(f"Done. Summary written to {args.output} ({len(clauses)} clauses)")

if __name__ == "__main__":
    main()
