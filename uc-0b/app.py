"""
UC-0B — Policy Summary Generator
Produces a clause-preserving summary from a policy text file.
"""
import argparse
import re
from pathlib import Path
from typing import Dict


def retrieve_policy(input_path: str) -> Dict[str, str]:
    """Load policy text and return a mapping of numbered clauses to their text."""
    content = Path(input_path).read_text(encoding="utf-8")
    lines = [line.rstrip() for line in content.splitlines()]
    sections: Dict[str, str] = {}

    current_clause: str | None = None
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_clause is not None:
                current_lines.append("")
            continue

        if re.fullmatch(r"[=\-\s]+", stripped) or re.fullmatch(r"[\u2500\u2550\u2551\s]+", stripped):
            continue

        clause_match = re.match(r"^(\d+\.\d+)\b", stripped)
        if clause_match:
            if current_clause is not None:
                sections[current_clause] = " ".join(part.strip() for part in current_lines if part.strip())
            current_clause = clause_match.group(1)
            current_lines = [stripped]
            continue

        if re.match(r"^\d+\.\s", stripped):
            continue

        if current_clause is not None:
            current_lines.append(stripped)

    if current_clause is not None:
        sections[current_clause] = " ".join(part.strip() for part in current_lines if part.strip())

    return sections


def summarize_policy(policy: Dict[str, str]) -> str:
    """Create a clause-preserving summary that includes the required numbered clauses."""
    required_clauses = [
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

    lines = []
    for clause_id in required_clauses:
        if clause_id in policy:
            lines.append(f"{clause_id}: {policy[clause_id]}")
        else:
            lines.append(f"{clause_id}: [missing from source]")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    Path(args.output).write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
