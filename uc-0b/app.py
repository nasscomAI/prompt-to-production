"""
UC-0B app.py — Summary That Changes Meaning
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path


def load_policy(path: str) -> dict:
    """Load policy text and return numbered clauses mapped to their full text."""
    text = Path(path).read_text(encoding="utf-8")
    clauses = {}
    current_clause = None
    for line in text.splitlines():
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if match:
            current_clause = match.group(1)
            clauses[current_clause] = match.group(2).strip()
            continue

        # Append only indented continuation lines, not section headers or formatting.
        if current_clause and line.startswith(" "):
            clauses[current_clause] += " " + line.strip()
    return clauses


def summarize_policy(clauses: dict) -> str:
    """Create a summary containing every numbered clause in order."""
    ordered_keys = sorted(
        clauses.keys(), key=lambda key: tuple(int(part) for part in key.split('.'))
    )
    summary_lines = [f"{key} {clauses[key]}" for key in ordered_keys]
    return "\n".join(summary_lines)


def write_summary(summary: str, output_path: str) -> None:
    Path(output_path).write_text(summary + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B policy summarizer that generates a clause-by-clause summary."
    )
    parser.add_argument("--input", required=True, help="Path to the policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary text file")
    args = parser.parse_args()

    clauses = load_policy(args.input)
    if not clauses:
        raise ValueError("No numbered clauses were found in the policy document.")

    summary = summarize_policy(clauses)
    write_summary(summary, args.output)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
