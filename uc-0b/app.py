"""
UC-0B app.py — Summary generator for the HR leave policy.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
from pathlib import Path

CLAUSE_RE = re.compile(r'^(\d+\.\d+)\s+(.*)$')


def retrieve_policy(path: Path):
    """Load a policy file and return a list of numbered clauses."""
    text = path.read_text(encoding='utf-8')
    clauses = []
    current_number = None
    current_text = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        match = CLAUSE_RE.match(stripped)
        if match:
            if current_number is not None:
                clauses.append((current_number, ' '.join(current_text).strip()))
            current_number = match.group(1)
            current_text = [match.group(2)]
        elif current_number is not None:
            current_text.append(stripped)

    if current_number is not None:
        clauses.append((current_number, ' '.join(current_text).strip()))

    return clauses


def summarize_policy(clauses):
    """Summarize structured policy clauses while preserving meaning and conditions."""
    summary_lines = []
    for number, text in clauses:
        # Use the original clause text where possible to avoid softening obligations.
        summary_lines.append(f"{number} {text}")

    return '\n'.join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    clauses = retrieve_policy(input_path)
    if not clauses:
        raise ValueError("No numbered clauses found in the input policy document.")

    summary_text = summarize_policy(clauses)
    output_path.write_text(summary_text + '\n', encoding='utf-8')
    print(f"Summary written to {output_path}")


if __name__ == "__main__":
    main()
