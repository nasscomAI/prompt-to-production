"""Create a source-grounded summary of a numbered policy document."""
import argparse
import re
from pathlib import Path


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_PATTERN = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")


def extract_clauses(policy_text):
    """Return every numbered clause, preserving its source wording."""
    clauses = []
    current = None

    for raw_line in policy_text.splitlines():
        line = raw_line.strip()
        match = CLAUSE_PATTERN.match(line)
        if match:
            if current:
                clauses.append(current)
            current = [match.group(1), match.group(2)]
        elif current and line:
            current[1] += " " + line

    if current:
        clauses.append(current)

    if not clauses:
        raise ValueError("The input does not contain numbered policy clauses.")

    return clauses


def build_summary(policy_text):
    sections = []
    current_section = None

    for raw_line in policy_text.splitlines():
        match = SECTION_PATTERN.match(raw_line)
        if match:
            current_section = match.group(1) + ". " + match.group(2)
            sections.append([current_section, []])

    clauses = extract_clauses(policy_text)
    for clause_number, wording in clauses:
        section_number = clause_number.split(".", 1)[0]
        matching_section = next(
            (section for section in sections if section[0].startswith(section_number + ".")),
            None,
        )
        if matching_section is None:
            matching_section = [section_number + ".", []]
            sections.append(matching_section)
        matching_section[1].append((clause_number, wording))

    output = ["# Policy Summary", "", "Source-grounded summary; wording is preserved from the source.", ""]
    for section_name, section_clauses in sections:
        if not section_clauses:
            continue
        output.extend(["## " + section_name, ""])
        for clause_number, wording in section_clauses:
            output.append(f"- **{clause_number}:** {wording}")
        output.append("")

    return "\n".join(output).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Summarize a numbered policy document.")
    parser.add_argument("--input", required=True, type=Path, help="Path to the policy text file")
    parser.add_argument("--output", required=True, type=Path, help="Path for the summary file")
    args = parser.parse_args()

    policy_text = args.input.read_text(encoding="utf-8")
    summary = build_summary(policy_text)
    args.output.write_text(summary, encoding="utf-8")

if __name__ == "__main__":
    main()
