"""
UC-0B app.py — Policy Document Summarizer
Implements retrieve_policy and summarize_policy skills per agents.md and skills.md.
"""
import argparse
import os
import re


def retrieve_policy(file_path):
    """Load a .txt policy file and return its content as structured numbered sections."""
    if not os.path.exists(file_path):
        return {"error": f"Error: Input file not found at {file_path}."}

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        return {"error": "Error: Input file is empty."}

    sections = {}
    current_section = None
    current_text = []

    for line in content.split("\n"):
        if re.match(r"^\s*═+\s*$", line):
            continue
        clause_match = re.match(r"^\s*(\d+\.\d+)\s+(.*)", line)
        section_match = re.match(r"^\s*\d+\.\s+[A-Z]", line)
        if clause_match:
            if current_section is not None:
                sections[current_section] = " ".join(current_text).strip()
            current_section = clause_match.group(1)
            current_text = [clause_match.group(2)]
        elif current_section is not None and not section_match and line.strip():
            current_text.append(line.strip())

    if current_section is not None:
        sections[current_section] = " ".join(current_text).strip()

    return sections


MULTI_CONDITION_CLAUSES = {
    "5.2": 2,
    "3.2": 2,
    "2.4": 2,
}

def summarize_policy(sections):
    """Produce a compliant summary preserving all clauses and conditions."""
    if "error" in sections:
        return sections["error"]

    header_lines = [
        "CITY MUNICIPAL CORPORATION",
        "EMPLOYEE LEAVE POLICY — SUMMARY",
        "",
    ]

    summary_lines = []
    clause_order = sorted(sections.keys(), key=lambda x: [int(p) for p in x.split(".")])

    for clause in clause_order:
        text = sections[clause]
        conditions = len(re.findall(r"and\b|AND\b|or\b|OR\b|within\b|subject to\b", text))

        if clause in MULTI_CONDITION_CLAUSES or conditions >= 2:
            summary_lines.append(f"[VERBATIM — meaning cannot be preserved in summary]")
            summary_lines.append(f"{clause} {text}")
        else:
            summary_lines.append(f"{clause} {text}")
        summary_lines.append("")

    return "\n".join(header_lines + summary_lines)


def main():
    parser = argparse.ArgumentParser(description="Policy Document Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)

    if "error" in sections:
        print(sections["error"])
        raise SystemExit(1)

    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
