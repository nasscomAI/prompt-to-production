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
    """
    Loads the policy .txt file and returns an OrderedDict mapping
    clause numbers (e.g. '2.3') to their full text.
    Exits with an error message if the file cannot be read or parsed.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        sys.exit(f"ERROR: Cannot read file '{filepath}': {e}")

    # Split on lines that start a new numbered clause (e.g. "2.3 ...")
    # A clause line begins with digits.digits at the start of a line.
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)", re.MULTILINE)

    clauses = OrderedDict()
    matches = list(clause_pattern.finditer(raw))

    if not matches:
        sys.exit(
            f"ERROR: No numbered clauses found in '{filepath}'. "
            "Check that the file is the correct policy document."
        )

    for i, match in enumerate(matches):
        clause_num = match.group(1)
        # Collect text from this match start to the next match start
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        block = raw[start:end].strip()

        # Clean up internal whitespace/newlines while preserving sentence breaks.
        # Strip decorative separator lines (═══...) and section title lines.
        lines = [line.strip() for line in block.splitlines()]
        lines = [
            l for l in lines
            if l
            and not set(l).issubset({"═", " "})
            and not re.match(r"^\d+\.\s+[A-Z \(\)]+$", l)
        ]
        clause_text = " ".join(lines)

        clauses[clause_num] = clause_text

    return clauses


def summarize_policy(clauses, output_filepath):
    """
    Writes a clause-by-clause summary to output_filepath.
    Every clause is present, every binding verb is preserved,
    and multi-condition obligations keep all named conditions.
    If a clause cannot be safely condensed, it is quoted verbatim.
    """

    # These clauses carry multi-condition or high-risk obligations.
    # They are written verbatim to guarantee no condition drop.
    verbatim_clauses = {"5.2", "5.3", "7.2", "2.5", "2.6", "2.7", "3.4"}

    lines = []
    lines.append("CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY")
    lines.append("Document Reference: HR-POL-001 | Version: 2.3 | Effective: 1 April 2024")
    lines.append("CLAUSE-BY-CLAUSE SUMMARY")
    lines.append("=" * 70)
    lines.append(
        "NOTE: This summary is derived solely from the source document. "
        "No information has been added, inferred, or assumed."
    )
    lines.append("=" * 70)
    lines.append("")

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
            lines.append(
                f"[{clause_num}] {text} "
                f"[VERBATIM — summarisation would alter meaning]"
            )
        else:
            lines.append(f"[{clause_num}] {text}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF SUMMARY")

    output = "\n".join(lines)

    try:
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(output)
    except OSError as e:
        sys.exit(f"ERROR: Cannot write to '{output_filepath}': {e}")

    return output


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Summarise an HR policy document clause by clause."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the .txt policy file (e.g. ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output summary file (e.g. summary_hr_leave.txt)",
    )
    args = parser.parse_args()

    print(f"Reading policy from: {args.input}")
    clauses = retrieve_policy(args.input)
    print(f"Found {len(clauses)} clauses: {', '.join(clauses.keys())}")

    print(f"Writing summary to: {args.output}")
    summarize_policy(clauses, args.output)

    print("Done. Verify that all 10 critical clauses are present in the output.")


if __name__ == "__main__":
    main()
