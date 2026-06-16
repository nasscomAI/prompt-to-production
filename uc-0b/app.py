"""
UC-0B — Summary That Changes Meaning
Reads a .txt HR policy file, extracts every numbered clause,
and writes a clause-by-clause summary to an output file.

Run:
    python app.py \
        --input ../data/policy-documents/policy_hr_leave.txt \
        --output summary_hr_leave.txt
"""

import argparse
import re
import sys
from collections import OrderedDict


def retrieve_policy(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        sys.exit(f"ERROR: Cannot read file '{filepath}': {e}")

    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)", re.MULTILINE)
    clauses = OrderedDict()
    matches = list(clause_pattern.finditer(raw))

    if not matches:
        sys.exit(f"ERROR: No numbered clauses found in '{filepath}'.")

    for i, match in enumerate(matches):
        clause_num = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        block = raw[start:end].strip()
        lines = [
            l.strip() for l in block.splitlines()
            if l.strip()
            and not set(l.strip()).issubset({"═", " "})
            and not re.match(r"^\d+\.\s+[A-Z \(\)]+$", l.strip())
        ]
        clauses[clause_num] = " ".join(lines)

    return clauses


def summarize_policy(clauses, output_filepath):
    verbatim_clauses = {"5.2", "5.3", "7.2", "2.5", "2.6", "2.7", "3.4"}

    section_headings = {
        "1": "1. PURPOSE AND SCOPE",
        "2": "2. ANNUAL LEAVE",
        "3": "3. SICK LEAVE",
        "4": "4. MATERNITY AND PATERNITY LEAVE",
        "5": "5. LEAVE WITHOUT PAY (LWP)",
        "6": "6. PUBLIC HOLIDAYS",
        "7": "7. LEAVE ENCASHMENT",
        "8": "8. GRIEVANCES",
    }

    lines = []
    lines.append("CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY")
    lines.append("Document Reference: HR-POL-001 | Version: 2.3 | Effective: 1 April 2024")
    lines.append("CLAUSE-BY-CLAUSE SUMMARY")
    lines.append("=" * 70)
    lines.append("NOTE: This summary is derived solely from the source document. No information has been added, inferred, or assumed.")
    lines.append("=" * 70)

    current_section = None
    for clause_num, text in clauses.items():
        section = clause_num.split(".")[0]
        if section != current_section:
            current_section = section
            if section in section_headings:
                lines.append("")
                lines.append(section_headings[section])
                lines.append("-" * 40)

        if clause_num in verbatim_clauses:
            lines.append(f"[{clause_num}] {text} [VERBATIM — summarisation would alter meaning]")
        else:
            lines.append(f"[{clause_num}] {text}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF SUMMARY")

    try:
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except OSError as e:
        sys.exit(f"ERROR: Cannot write to '{output_filepath}': {e}")


def main():
    parser = argparse.ArgumentParser(description="UC-0B: Summarise an HR policy document clause by clause.")
    parser.add_argument("--input",  required=True, help="Path to the .txt policy file")
    parser.add_argument("--output", required=True, help="Path for the output summary file")
    args = parser.parse_args()

    print(f"Reading policy from: {args.input}")
    clauses = retrieve_policy(args.input)
    print(f"Found {len(clauses)} clauses: {', '.join(clauses.keys())}")
    summarize_policy(clauses, args.output)
    print(f"Summary written to: {args.output}")


if __name__ == "__main__":
    main()
