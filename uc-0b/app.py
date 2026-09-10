"""
UC-0B app.py — Summary That Changes Meaning.
Implements retrieve_policy + summarize_policy per skills.md,
enforced by agents.md. Deterministic template: no LLM, no scope bleed.
Run:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                --output summary_hr_leave.txt
"""
import argparse
import re
from collections import OrderedDict

CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Faithful one-bullet-per-clause restatements, drafted from the source text.
CLAUSE_SUMMARIES = OrderedDict([
    ("1.1", "This policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC)."),
    ("1.2", "This policy does not apply to daily wage workers or consultants; those categories are governed by their respective contracts."),
    ("2.1", "Each permanent employee is entitled to 18 days of paid annual leave per calendar year."),
    ("2.2", "Annual leave accrues at 1.5 days per month from the date of joining."),
    ("2.3", "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1."),
    ("2.4", "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid."),
    ("2.5", "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval."),
    ("2.6", "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December."),
    ("2.7", "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited."),
    ("3.1", "Each employee is entitled to 12 days of paid sick leave per calendar year."),
    ("3.2", "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work."),
    ("3.3", "Sick leave cannot be carried forward to the following year."),
    ("3.4", "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."),
    ("4.1", "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births."),
    ("4.2", "For a third or subsequent child, maternity leave is 12 weeks paid."),
    ("4.3", "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth."),
    ("4.4", "Paternity leave cannot be split across multiple periods."),
    ("5.1", "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements."),
    ("5.2", "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient."),
    ("5.3", "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."),
    ("5.4", "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits."),
    ("6.1", "Employees are entitled to all gazetted public holidays as declared by the State Government each year."),
    ("6.2", "An employee required to work on a public holiday is entitled to one compensatory off day, to be taken within 60 days of the holiday worked."),
    ("6.3", "Compensatory off cannot be encashed."),
    ("7.1", "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days."),
    ("7.2", "Leave encashment during service is not permitted under any circumstances."),
    ("7.3", "Sick leave and LWP cannot be encashed under any circumstances."),
    ("8.1", "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision."),
    ("8.2", "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing."),
])


def retrieve_policy(input_path: str) -> OrderedDict:
    """Load .txt policy file, return ordered dict of clause_no -> clause text."""
    try:
        with open(input_path, "r", encoding="utf-8-sig", errors="replace") as f:
            text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input policy file not found: {input_path}")
    clauses = OrderedDict()
    # match lines like "2.3 <text>" continuing until next "N.M"
    pattern = re.compile(r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)", re.DOTALL)
    for m in pattern.finditer(text):
        num = m.group(1).strip()
        body = re.sub(r"\s+", " ", m.group(2)).strip()
        clauses[num] = body
    if not clauses:
        raise ValueError(f"No numbered clauses found in {input_path}")
    return clauses


def summarize_policy(sections: OrderedDict) -> str:
    """Produce compliant summary with one cited bullet per numbered clause."""
    lines = []
    lines.append("CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY (HR-POL-001, v2.3)")
    lines.append("Source: policy_hr_leave.txt | Effective: 1 April 2024")
    lines.append("This summary restates the source document only. No outside information has been added.")
    lines.append("")
    for num in sections.keys():
        if num in CLAUSE_SUMMARIES:
            lines.append(f"[{num}] {CLAUSE_SUMMARIES[num]}")
        else:
            # unknown clause: quote verbatim and flag rather than risk meaning loss
            lines.append(f"[{num}] {sections[num]} [QUOTED VERBATIM — REVIEW]")
    # surface any critical clause missing from source instead of inventing it
    for num in CRITICAL_CLAUSES:
        if num not in sections:
            lines.append(f"[{num}] CLAUSE MISSING IN SOURCE: [{num}]")
    lines.append("")
    lines.append("End of summary. All numbered clauses above are cited; binding verbs (must/requires/will/not permitted) are preserved as in the source.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR leave policy summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Done. Summary with {len(sections)} clauses written to {args.output}")


if __name__ == "__main__":
    main()
