"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*\S)\s*$")
DECORATION_RE = re.compile(r"^[^\w]+$")


def retrieve_policy(input_path: str) -> list[tuple[str, str]]:
    text = Path(input_path).read_text(encoding="utf-8")
    clauses: list[tuple[str, str]] = []
    current_id = ""
    current_text: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        clause_match = CLAUSE_RE.match(line)
        if clause_match:
            if current_id:
                clauses.append((current_id, " ".join(current_text)))
            current_id = clause_match.group(1)
            current_text = [clause_match.group(2)]
            continue

        if not current_id:
            continue
        if not line or DECORATION_RE.match(line):
            continue
        if re.match(r"^\d+\.\s+[A-Z]", line):
            continue
        current_text.append(line)

    if current_id:
        clauses.append((current_id, " ".join(current_text)))
    return clauses


def summarize_policy(clauses: list[tuple[str, str]]) -> str:
    if not clauses:
        raise ValueError("No numbered clauses found in the policy document.")
    return "\n".join(f"{clause_id} {clause_text}" for clause_id, clause_text in clauses) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B clause-preserving policy summarizer")
    parser.add_argument("--input", required=True, help="Path to the source policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary text file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    Path(args.output).write_text(summary, encoding="utf-8")
    print(f"Wrote {len(clauses)} clauses to {args.output}")

if __name__ == "__main__":
    main()
