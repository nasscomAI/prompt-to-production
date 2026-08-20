"""
UC-0B app.py — Minimal implementation.
Loads the HR leave policy file, extracts numbered clauses, and writes a clause-preserving summary.
"""
import argparse
import re
from pathlib import Path

CLAUSE_RE = re.compile(r"^(\d+(?:\.\d+)*)\s+(.*\S.*)$")
CONTINUATION_RE = re.compile(r"^\s{4,}(.*\S.*)$")


def retrieve_policy(input_path: Path):
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")

    clauses = []
    current_clause = None

    with input_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            clause_match = CLAUSE_RE.match(line)
            if clause_match:
                if current_clause is not None:
                    clauses.append(current_clause)
                current_clause = {
                    "id": clause_match.group(1),
                    "text": clause_match.group(2).strip(),
                }
                continue

            if current_clause is None:
                continue

            continuation_match = CONTINUATION_RE.match(line)
            if continuation_match:
                current_clause["text"] += " " + continuation_match.group(1).strip()
                continue

            if line.strip() == "":
                continue

    if current_clause is not None:
        clauses.append(current_clause)

    return clauses


def summarize_policy(clauses):
    if not clauses:
        raise ValueError("No numbered clauses were found in the input policy.")

    lines = [
        "Policy summary generated from the input policy document.",
        "Each numbered clause from the source is preserved below.",
        "",
    ]

    for clause in clauses:
        text = " ".join(clause["text"].split())
        lines.append(f"{clause['id']}. {text}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate a clause-preserving policy summary.")
    parser.add_argument("--input", required=True, help="Path to the input policy text file.")
    parser.add_argument("--output", required=True, help="Path to the output summary file.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    clauses = retrieve_policy(input_path)
    summary = summarize_policy(clauses)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")

    print(f"Summary written to: {output_path}")


if __name__ == "__main__":
    main()
