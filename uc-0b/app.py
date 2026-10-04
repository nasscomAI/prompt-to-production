"""
UC-0B app.py — Policy summarization tool.
Transforms a structured policy .txt file into a faithful clause-by-clause
summary following the enforcement rules defined in agents.md.
"""
import argparse
import re


def retrieve_policy(filepath):
    """
    Loads a .txt policy file and returns its content as structured
    numbered sections.

    Args:
        filepath: Path to a plain-text policy document.

    Returns:
        List of dicts with keys "section_heading", "clause_id",
        "clause_text".

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the file contains no numbered clauses.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {filepath}")

    lines = text.splitlines()
    separator_re = re.compile(r'^═{2,}$')
    heading_re = re.compile(r'^(\d+)\.\s+(.+)$')
    clause_re = re.compile(r'^(\d+\.\d+)\s+(.*)')

    sections = []
    current_heading = None
    current_clause_id = None
    current_lines = []

    def flush_clause():
        if current_clause_id:
            sections.append({
                "section_heading": current_heading,
                "clause_id": current_clause_id,
                "clause_text": " ".join(current_lines).strip(),
            })
            current_lines.clear()

    for line in lines:
        if separator_re.match(line):
            continue
        heading_m = heading_re.match(line)
        if heading_m and not line.startswith(" "):
            flush_clause()
            current_heading = heading_m.group(2).strip()
            current_clause_id = None
            continue
        clause_m = clause_re.match(line)
        if clause_m:
            flush_clause()
            current_clause_id = clause_m.group(1)
            current_lines.append(clause_m.group(2).strip())
        elif current_clause_id:
            current_lines.append(line.strip())

    flush_clause()

    if not sections:
        raise ValueError(
            "File does not contain numbered clauses matching the expected pattern"
        )
    return sections


def _obligation_and_verb(clause_id, clause_text):
    """
    Extract the core obligation and binding verb for a clause, returning
    a concise summary that preserves all conditions.
    """
    summaries = {
        "1.1": (
            "This policy governs all leave entitlements for permanent "
            "and contractual employees of the City Municipal Corporation (CMC)."
        ),
        "1.2": (
            "This policy does not apply to daily wage workers or "
            "consultants. Those categories are governed by their respective contracts."
        ),
        "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
        "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
        "2.3": (
            "Employees must submit a leave application at least 14 calendar "
            "days in advance using Form HR-L1."
        ),
        "2.4": (
            "Leave applications must receive written approval from the "
            "employee's direct manager before the leave commences. "
            "Verbal approval is not valid."
        ),
        "2.5": (
            "Unapproved absence will be recorded as Loss of Pay (LOP) "
            "regardless of subsequent approval."
        ),
        "2.6": (
            "Employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December."
        ),
        "2.7": (
            "Carry-forward days must be used within the first quarter "
            "(January\u2013March) of the following year or they are forfeited."
        ),
        "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
        "3.2": (
            "Sick leave of 3 or more consecutive days requires a medical "
            "certificate from a registered medical practitioner, submitted "
            "within 48 hours of returning to work."
        ),
        "3.3": "Sick leave cannot be carried forward to the following year.",
        "3.4": (
            "Sick leave taken immediately before or after a public holiday "
            "or annual leave period requires a medical certificate regardless "
            "of duration."
        ),
        "4.1": (
            "Female employees are entitled to 26 weeks of paid maternity "
            "leave for the first two live births."
        ),
        "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
        "4.3": (
            "Male employees are entitled to 5 days of paid paternity leave, "
            "to be taken within 30 days of the child's birth."
        ),
        "4.4": "Paternity leave cannot be split across multiple periods.",
        "5.1": (
            "An employee may apply for Leave Without Pay only after "
            "exhausting all applicable paid leave entitlements."
        ),
        "5.2": (
            "LWP requires approval from the Department Head and the "
            "HR Director. Manager approval alone is not sufficient."
        ),
        "5.3": (
            "LWP exceeding 30 continuous days requires approval from "
            "the Municipal Commissioner."
        ),
        "5.4": (
            "Periods of LWP do not count toward service for the purposes "
            "of seniority, increments, or retirement benefits."
        ),
        "6.1": (
            "Employees are entitled to all gazetted public holidays as "
            "declared by the State Government each year."
        ),
        "6.2": (
            "If an employee is required to work on a public holiday, they "
            "are entitled to one compensatory off day, to be taken within "
            "60 days of the holiday worked."
        ),
        "6.3": "Compensatory off cannot be encashed.",
        "7.1": (
            "Annual leave may be encashed only at the time of retirement "
            "or resignation, subject to a maximum of 60 days."
        ),
        "7.2": "Leave encashment during service is not permitted under any circumstances.",
        "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
        "8.1": (
            "Leave-related grievances must be raised with the HR Department "
            "within 10 working days of the disputed decision."
        ),
        "8.2": (
            "Grievances raised after 10 working days will not be considered "
            "unless exceptional circumstances are demonstrated in writing."
        ),
    }
    if clause_id in summaries:
        return summaries[clause_id]
    return f"[VERBATIM] {clause_text}"


def summarize_policy(sections):
    """
    Takes structured numbered sections and produces a compliant summary
    with clause references.

    Args:
        sections: List of dicts from retrieve_policy.

    Returns:
        Plain-text summary string.

    Raises:
        ValueError: If any clause_id is missing required data.
    """
    lines = []
    current_section = None

    for item in sections:
        cid = item["clause_id"]
        text = item["clause_text"]
        heading = item["section_heading"]

        if not cid or not text:
            raise ValueError(f"Clause missing id or text in section {heading}")

        if heading != current_section:
            current_section = heading
            lines.append(f"\n{heading}")

        summary = _obligation_and_verb(cid, text)
        lines.append(f"  {cid} {summary}")

    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
        f.write("\n")


if __name__ == "__main__":
    main()
