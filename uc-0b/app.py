"""
UC-0B app.py — Clause-preserving policy summary implementation.
"""
import argparse
import re


def retrieve_policy(input_path: str) -> str:
    """Read the policy file from disk."""
    with open(input_path, "r", encoding="utf-8") as infile:
        return infile.read()


def summarize_policy(policy_text: str) -> str:
    """Return a clause-preserving summary by extracting every numbered clause verbatim."""
    clauses = []
    current_clause = None
    current_lines = []

    for line in policy_text.splitlines():
        clause_match = re.match(r"^\s*(\d+\.\d+)\s+(.*)$", line)
        section_heading = re.match(r"^\s*\d+\.\s+[A-Z].*$", line)
        decorative_line = re.fullmatch(r"[\s═─━]+", line)

        if clause_match:
            if current_clause is not None:
                clauses.append((current_clause, " ".join(current_lines).strip()))
            current_clause = clause_match.group(1)
            current_lines = [clause_match.group(2).strip()]
        elif current_clause is not None and not decorative_line and not section_heading:
            if line.strip():
                current_lines.append(line.strip())

    if current_clause is not None:
        clauses.append((current_clause, " ".join(current_lines).strip()))

    return "\n".join(f"{number}: {text}" for number, text in clauses)


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
