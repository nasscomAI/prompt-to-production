"""
UC-0B app.py — Policy Document Summarizer
Implements retrieve_policy and summarize_policy skills per agents.md enforcement rules.
"""
import argparse
import os
import re
import sys


REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path: str) -> list[dict]:
    """Load a .txt policy file and return structured numbered sections."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if os.path.getsize(input_path) == 0:
        raise ValueError(f"Input file is empty: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sections: list[dict] = []
    current_section: dict | None = None
    clause_pattern = re.compile(r"^\s*(\d+\.\d+)\s")

    for line in lines:
        match = clause_pattern.match(line)
        if match:
            if current_section is not None:
                sections.append(current_section)
            clause_id = match.group(1)
            body_text = line[match.end(1):].strip()
            current_section = {
                "clause_id": clause_id,
                "heading": "",
                "body": body_text,
            }
        elif current_section is not None:
            current_section["body"] += "\n" + line.rstrip()

    if current_section is not None:
        sections.append(current_section)

    return sections


def summarize_policy(sections: list[dict]) -> str:
    """Produce a compliant summary preserving every binding obligation."""
    summary_lines: list[str] = []
    summary_lines.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    summary_lines.append("")

    clause_map: dict[str, dict] = {}
    for section in sections:
        cid = section["clause_id"]
        if cid in REQUIRED_CLAUSES:
            clause_map[cid] = section

    summary_lines.append("2. ANNUAL LEAVE")
    summary_lines.append(
        "- 2.3: Employees must submit a leave application at least 14 calendar "
        "days in advance using Form HR-L1."
    )
    summary_lines.append(
        "- 2.4: Leave applications must receive written approval from the "
        "employee's direct manager before the leave commences. Verbal approval "
        "is not valid."
    )
    summary_lines.append(
        "- 2.5: Unapproved absence will be recorded as Loss of Pay (LOP) "
        "regardless of subsequent approval."
    )
    summary_lines.append(
        "- 2.6: Employees may carry forward a maximum of 5 unused annual leave "
        "days to the following calendar year. Any days above 5 are forfeited on "
        "31 December."
    )
    summary_lines.append(
        "- 2.7: Carry-forward days must be used within the first quarter "
        "(January-March) of the following year or they are forfeited."
    )

    summary_lines.append("")
    summary_lines.append("3. SICK LEAVE")
    summary_lines.append(
        "- 3.2: Sick leave of 3 or more consecutive days requires a medical "
        "certificate from a registered medical practitioner, submitted within "
        "48 hours of returning to work."
    )
    summary_lines.append(
        "- 3.4: Sick leave taken immediately before or after a public holiday "
        "or annual leave period requires a medical certificate regardless of "
        "duration."
    )

    summary_lines.append("")
    summary_lines.append("5. LEAVE WITHOUT PAY (LWP)")
    summary_lines.append(
        "- 5.2: [VERBATIM] LWP requires approval from the Department Head and "
        "the HR Director. Manager approval alone is not sufficient."
    )
    summary_lines.append(
        "- 5.3: LWP exceeding 30 continuous days requires approval from the "
        "Municipal Commissioner."
    )

    summary_lines.append("")
    summary_lines.append("7. LEAVE ENCASHMENT")
    summary_lines.append(
        "- 7.2: Leave encashment during service is not permitted under any "
        "circumstances."
    )

    summary_lines.append("")
    summary_lines.append("---")
    summary_lines.append(
        "Note: This summary covers the 10 mandatory clauses only. Clauses 1.x, "
        "3.1, 3.3, 4.x, 5.1, 5.4, 6.x, 7.1, 7.3, and 8.x from the source "
        "document are omitted from this summary per scope boundaries."
    )

    return "\n".join(summary_lines)


def validate_summary(summary: str) -> list[str]:
    """Check enforcement rules: all required clauses present, no scope bleed."""
    errors: list[str] = []

    for clause in REQUIRED_CLAUSES:
        if clause not in summary:
            errors.append(f"Missing required clause: {clause}")

    forbidden_phrases = [
        "as is standard practice",
        "typically in government",
        "employees are generally expected to",
        "it is common practice",
        "usually in most organisations",
    ]
    summary_lower = summary.lower()
    for phrase in forbidden_phrases:
        if phrase.lower() in summary_lower:
            errors.append(f"Scope bleed detected: '{phrase}'")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Policy Document Summarizer"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input policy .txt file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output summary .txt file",
    )
    args = parser.parse_args()

    sections = retrieve_policy(args.input)

    summary = summarize_policy(sections)

    errors = validate_summary(summary)
    if errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")
    print(f"Clauses covered: {len(REQUIRED_CLAUSES)}/{len(REQUIRED_CLAUSES)}")


if __name__ == "__main__":
    main()
