"""
UC-0B app.py — Summary That Changes Meaning
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

REQUIRED_CLAUSES = [
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

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)")


def retrieve_policy(path):
    sections = {}
    current_clause = None

    with open(path, encoding="utf-8") as infile:
        for raw_line in infile:
            line = raw_line.strip()
            if not line:
                continue

            if all(ch in "═- " for ch in line):
                continue
            if re.match(r"^\d+\.\s+", line):
                continue

            match = CLAUSE_PATTERN.match(line)
            if match:
                current_clause = match.group(1)
                sections[current_clause] = match.group(2).strip()
            elif current_clause:
                sections[current_clause] += " " + line

    return sections


def summarize_policy(sections, clause_numbers):
    summary_lines = ["HR Leave Policy Summary:\n"]
    for clause in clause_numbers:
        clause_text = sections.get(clause)
        if clause_text:
            summary_lines.append(f"Clause {clause}: {clause_text}")
        else:
            summary_lines.append(
                f"Clause {clause}: [Clause text unavailable in source document]"
            )
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections, REQUIRED_CLAUSES)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(summary + "\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
