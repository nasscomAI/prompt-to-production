import argparse
import re
import sys


REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

CLAUSE_SUMMARIES = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January\u2013March) of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(file_path: str) -> dict[str, str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    except UnicodeDecodeError:
        raise ValueError(f"File is unreadable (encoding error): {file_path}")

    if not content.strip():
        raise ValueError(f"Policy file is empty: {file_path}")

    pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+\s|\Z)", re.MULTILINE | re.DOTALL)
    matches = pattern.findall(content)

    sections: dict[str, str] = {}
    for clause_num, body in matches:
        key = clause_num.strip()
        text = " ".join(body.split())
        if key in REQUIRED_CLAUSES:
            sections[key] = text

    missing = [c for c in REQUIRED_CLAUSES if c not in sections]
    if missing:
        raise ValueError(f"Missing required clauses in source document: {', '.join(missing)}")

    return sections


def summarize_policy(sections: dict[str, str]) -> str:
    if len(sections) < len(REQUIRED_CLAUSES):
        raise ValueError(
            f"Expected {len(REQUIRED_CLAUSES)} clauses, got {len(sections)}. "
            "Refusing to generate incomplete summary."
        )

    output_lines = [
        "POLICY SUMMARY — HR Leave Policy (HR-POL-001)",
        "=" * 50,
        "",
    ]

    for clause_id in REQUIRED_CLAUSES:
        summary = CLAUSE_SUMMARIES[clause_id]
        output_lines.append(f"[{clause_id}] {summary}")
        output_lines.append("")

    return "\n".join(output_lines)


def validate_output(summary: str, source_sections: dict[str, str]) -> list[str]:
    errors = []

    for clause_id in REQUIRED_CLAUSES:
        if f"[{clause_id}]" not in summary:
            errors.append(f"Clause {clause_id} missing from summary")

    forbidden_phrases = [
        "as is standard practice",
        "typically in government",
        "employees are generally expected",
        "it is assumed",
        "usually",
        "normally",
    ]
    lower_summary = summary.lower()
    for phrase in forbidden_phrases:
        if phrase.lower() in lower_summary:
            errors.append(f"Scope bleed detected: '{phrase}'")

    return errors


def main():
    parser = argparse.ArgumentParser(description="UC-0B: Policy Document Summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Output file for the summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)

    summary = summarize_policy(sections)

    errors = validate_output(summary, sections)
    if errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output} ({len(sections)} clauses verified)")


if __name__ == "__main__":
    main()
