
"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
from pathlib import Path


def retrieve_policy(path: Path) -> dict:
    """
    Skill: retrieve_policy

    Loads a .txt policy file and returns a structured representation
    keyed by clause number. This function must preserve original text
    and numbering without inference or paraphrasing.
    """
    clauses = {}
    current_clause = None
    buffer = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # crude but safe: detect clause numbers like "2.3", "5.2", etc.
            if stripped and stripped[0].isdigit() and "." in stripped.split()[0]:
                if current_clause is not None:
                    clauses[current_clause] = " ".join(buffer).strip()
                    buffer = []
                current_clause = stripped.split()[0]
                buffer.append(stripped)
            else:
                buffer.append(stripped)

        if current_clause is not None:
            clauses[current_clause] = " ".join(buffer).strip()

    return clauses


def summarize_policy(structured_clauses: dict) -> str:
    """
    Skill: summarize_policy

    Produces a summary that preserves all obligations, conditions,
    and binding verbs. This starter implementation is intentionally
    conservative: it emits each clause verbatim with a clause label.
    """
    summary_lines = []
    for clause, text in structured_clauses.items():
        summary_lines.append(f"Clause {clause}: {text}")

    return "\n\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary file")

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    structured_policy = retrieve_policy(input_path)
    summary = summarize_policy(structured_policy)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    main()
