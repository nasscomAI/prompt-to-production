"""
UC-0B app.py — Policy summarizer for HR leave policy.
"""
import argparse
import re
from pathlib import Path

CLAUSE_IDS = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def load_policy_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8")


def parse_sections(text: str) -> dict:
    sections = {}
    current_clause = None
    current_text = []
    for line in text.splitlines():
        stripped_line = line.strip()
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped_line)
        if match:
            if current_clause:
                sections[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
            continue

        if not current_clause or not stripped_line:
            continue

        if re.match(r"^[^A-Za-z0-9]+$", stripped_line):
            continue
        if re.match(r"^\d+\.\s+.+", stripped_line):
            continue

        current_text.append(stripped_line)
    if current_clause:
        sections[current_clause] = " ".join(current_text).strip()
    return sections


def summarize_policy(text: str) -> str:
    sections = parse_sections(text)
    summary_lines = [
        "HR Leave Policy Summary",
        "========================",
        "",
        "Key obligations and approvals by clause:",
        "",
    ]

    for clause in CLAUSE_IDS:
        clause_text = sections.get(clause)
        if not clause_text:
            raise ValueError(f"Required clause {clause} not found in policy document.")
        summary_lines.append(f"{clause}. {clause_text}")
        summary_lines.append("")

    return "\n".join(summary_lines).strip()


def main():
    parser = argparse.ArgumentParser(description="UC-0B policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    policy_text = load_policy_file(Path(args.input))
    summary_text = summarize_policy(policy_text)
    Path(args.output).write_text(summary_text + "\n", encoding="utf-8")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
