"""
UC-0B app.py
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

FLAGGED_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}


def normalize_clause_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_non_clause_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if re.match(r"^\d+\.\s+", stripped):
        return True
    if re.fullmatch(r"[^A-Za-z0-9]+", stripped):
        return True
    return False


def retrieve_policy(input_path: str) -> list[dict[str, str]]:
    policy_text = Path(input_path).read_text(encoding="utf-8-sig")
    clauses: list[dict[str, str]] = []
    current_number = None
    current_lines: list[str] = []

    for raw_line in policy_text.splitlines():
        line = raw_line.rstrip()
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line.strip())
        if match:
            if current_number is not None:
                clauses.append(
                    {
                        "clause": current_number,
                        "text": normalize_clause_text(" ".join(current_lines)),
                    }
                )
            current_number = match.group(1)
            current_lines = [match.group(2).strip()]
        elif current_number is not None and not is_non_clause_line(line):
            current_lines.append(line.strip())

    if current_number is not None:
        clauses.append(
            {
                "clause": current_number,
                "text": normalize_clause_text(" ".join(current_lines)),
            }
        )

    if not clauses:
        raise ValueError("No numbered clauses were found in the policy file.")
    return clauses


def summarize_policy(clauses: list[dict[str, str]]) -> str:
    lines = ["Clause-preserving HR leave summary", ""]
    for clause in clauses:
        prefix = "[VERBATIM - meaning-loss risk] " if clause["clause"] in FLAGGED_CLAUSES else ""
        lines.append(f'{clause["clause"]}: {prefix}{clause["text"]}')
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to summary output file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    Path(args.output).write_text(summary, encoding="utf-8")
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
