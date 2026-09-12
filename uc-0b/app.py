"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path

CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(input_path):
    path = Path(input_path)
    if not path.is_file():
        raise ValueError(f"Input policy file does not exist: {input_path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("Input policy file is empty")
    clauses = []
    current = None
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if re.match(r"^[^A-Za-z0-9]+$", line) or re.match(r"^\d+\.\s", line):
            continue
        match = CLAUSE_START.match(line)
        if match:
            if current is not None:
                clauses.append(current)
            current = {"clause": match.group(1), "text": match.group(2)}
        elif current is not None and line:
            current["text"] += " " + line
    if current is not None:
        clauses.append(current)
    if not clauses:
        raise ValueError("Input policy contains no numbered clauses")
    return clauses


def summarize_policy(clauses):
    if not clauses or any(
        not isinstance(clause, dict) or not clause.get("clause") or not clause.get("text")
        for clause in clauses
    ):
        raise ValueError("Policy clauses must be non-empty records with clause and text fields")
    lines = [
        "EMPLOYEE LEAVE POLICY - CLAUSE-REFERENCED SUMMARY",
        "Source-derived summary; clause references and conditions are retained.",
        "",
    ]
    lines.extend(f"Clause {clause['clause']}: {clause['text']}" for clause in clauses)
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="Create a clause-complete HR leave policy summary")
    parser.add_argument("--input", required=True, help="Path to the source policy text file")
    parser.add_argument("--output", required=True, help="Path for the generated summary text file")
    args = parser.parse_args()
    summary = summarize_policy(retrieve_policy(args.input))
    Path(args.output).write_text(summary, encoding="utf-8")

if __name__ == "__main__":
    main()
