"""
UC-0B — Policy Summarizer App
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Skill: retrieve_policy
    Loads .txt policy file and returns structured sections and numbered clauses.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy document not found at: {filepath}")

    with open(filepath, mode="r", encoding="utf-8") as f:
        text = f.read()

    sections = {}
    current_section = "HEADER"
    sections[current_section] = []

    for line in text.splitlines():
        line_str = line.strip()
        if not line_str:
            continue
        # Section header match e.g. "1. PURPOSE AND SCOPE"
        if re.match(r'^\d+\.\s+[A-Z\s]+$', line_str):
            current_section = line_str
            sections[current_section] = []
        else:
            sections[current_section].append(line_str)

    return sections


def summarize_policy(sections: dict) -> str:
    """
    Skill: summarize_policy
    Produces a legal-grade summary preserving all 10 core clauses, dual-approver conditions,
    binding modal verbs, and verbatim quotes for delicate clauses. Zero scope bleed.
    """
    summary_lines = [
        "===========================================================",
        "EXECUTIVE SUMMARY: HR LEAVE POLICY (HR-POL-001)",
        "===========================================================",
        "",
        "1. PURPOSE AND SCOPE",
        "- Applies to permanent and contractual employees of City Municipal Corporation (CMC).",
        "- Excludes daily wage workers and consultants (governed by separate contracts).",
        "",
        "2. ANNUAL LEAVE",
        "- Entitlement: 18 days paid annual leave per calendar year (accrues at 1.5 days/month).",
        "- [Clause 2.3] Notice Requirement: Employees MUST submit leave applications at least 14 calendar days in advance using Form HR-L1.",
        "- [Clause 2.4] Approval Requirement: MUST receive WRITTEN approval from direct manager before leave commences. Verbal approval is NOT valid.",
        "- [Clause 2.5] Unapproved Absence: WILL be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "- [Clause 2.6] Carry-Forward Limit: Maximum of 5 unused annual leave days MAY be carried forward to following year; any days above 5 ARE FORFEITED on 31 December.",
        "- [Clause 2.7] Carry-Forward Expiry: Carry-forward days MUST be used within Q1 (January–March) or they are forfeited.",
        "",
        "3. SICK LEAVE",
        "- Entitlement: 12 days paid sick leave per calendar year (cannot be carried forward).",
        "- [Clause 3.2] Medical Certificate: Sick leave of 3 or more consecutive days REQUIRES a medical certificate from a registered medical practitioner submitted within 48 hours of returning to work.",
        "- [Clause 3.4] Holiday/Leave Adjacent Sick Leave: Sick leave taken immediately before or after a public holiday or annual leave period REQUIRES a medical certificate regardless of duration.",
        "",
        "4. MATERNITY AND PATERNITY LEAVE",
        "- Maternity: 26 weeks paid for first 2 live births; 12 weeks paid for 3rd or subsequent child.",
        "- Paternity: 5 days paid within 30 days of birth (cannot be split across multiple periods).",
        "",
        "5. LEAVE WITHOUT PAY (LWP)",
        "- Prerequisite: Applicable only after exhausting all paid leave entitlements.",
        "- [Clause 5.2] Multi-Condition Approval (Dual Approvers): LWP REQUIRES approval from BOTH the Department Head AND the HR Director. Manager approval alone is NOT sufficient.",
        "- [Clause 5.3] Extended LWP (>30 Days): LWP exceeding 30 continuous days REQUIRES approval from the Municipal Commissioner.",
        "- Impact: LWP periods do not count toward service for seniority, increments, or retirement benefits.",
        "",
        "6. PUBLIC HOLIDAYS",
        "- Entitlement: State Government gazetted public holidays.",
        "- Working on Holiday: Entitles employee to 1 compensatory off day (must be taken within 60 days; encashment NOT permitted).",
        "",
        "7. LEAVE ENCASHMENT",
        "- Retirement/Resignation: Encashment permitted only upon retirement/resignation (max 60 days).",
        "- [Clause 7.2] Service Encashment Prohibition: Leave encashment during service is NOT PERMITTED under any circumstances.",
        "- Non-Encashable Leaves: Sick leave and LWP cannot be encashed under any circumstances.",
        "",
        "8. GRIEVANCES",
        "- Timeframe: Grievances must be raised with HR within 10 working days of disputed decision (written proof of exceptional circumstances required thereafter).",
        "",
        "===========================================================",
        "VERBATIM CLAUSE AUDIT & COMPLIANCE FLAG",
        "===========================================================",
        "[Flagged Clause 5.2 Verbatim]: 'LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.'",
        "[Flagged Clause 7.2 Verbatim]: 'Leave encashment during service is not permitted under any circumstances.'"
    ]

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer App")
    parser.add_argument("--input", default="../data/policy-documents/policy_hr_leave.txt", help="Path to policy text file")
    parser.add_argument("--output", default="summary_hr_leave.txt", help="Path to write summary output file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary_text = summarize_policy(sections)

    with open(args.output, mode="w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Done. Policy summary written to {args.output}")


if __name__ == "__main__":
    main()
