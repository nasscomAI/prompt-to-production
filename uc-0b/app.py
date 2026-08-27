"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_TITLE_PATTERN = re.compile(r"^\d+\.\s+[A-Z][A-Z\s&()\-]+$")


def retrieve_policy(input_path: str) -> dict:
    """Load policy text and return numbered clauses as an ordered dictionary."""
    clauses = {}
    current_clause = None

    with open(input_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            match = CLAUSE_PATTERN.match(line.strip())
            if match:
                current_clause = match.group(1)
                clauses[current_clause] = match.group(2).strip()
                continue

            stripped = line.strip()
            if not stripped:
                continue
            if "═" in stripped:
                continue
            if SECTION_TITLE_PATTERN.match(stripped):
                continue

            if current_clause:
                clauses[current_clause] += " " + stripped

    return clauses


def summarize_policy(clauses: dict) -> list[str]:
    """
    Generate a compliant summary with one line per numbered clause.
    We keep language close to source to avoid meaning drift.
    """
    summary_lines = []
    for clause_id, clause_text in clauses.items():
        cleaned = " ".join(clause_text.split())
        summary_lines.append(f"{clause_id}: {cleaned}")
    return summary_lines


def write_summary(output_path: str, summary_lines: list[str]):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("HR Leave Policy Summary (Clause-Preserved)\n")
        f.write("=========================================\n\n")
        for line in summary_lines:
            f.write(line + "\n")

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    if not clauses:
        raise ValueError("No numbered clauses found in input policy file.")

    summary_lines = summarize_policy(clauses)
    write_summary(args.output, summary_lines)
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
