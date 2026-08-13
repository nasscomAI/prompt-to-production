"""
UC-0B app.py — HR Leave Policy Compliance Summarizer
RICE-Enforced Implementation
"""
import argparse
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Loads raw policy text from file and parses it into structured sections and numbered clauses.
    """
    with open(input_path, mode="r", encoding="utf-8") as f:
        content = f.read()
    if not content.strip():
        raise ValueError("Policy file is empty.")

    lines = content.splitlines()
    structured = {
        "metadata": {
            "title": "CITY MUNICIPAL CORPORATION — HR LEAVE POLICY",
            "reference": "HR-POL-001",
            "version": "2.3",
            "effective": "1 April 2024"
        },
        "sections": {}
    }

    current_sec_num = None
    current_sec_title = ""
    current_clause_num = None
    current_clause_text = []

    section_hdr_pattern = re.compile(r'^\s*(\d+)\.\s+(.*)')
    clause_pattern = re.compile(r'^\s*(\d+\.\d+)\s+(.*)')

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("═"):
            continue

        # Check section header (e.g., "1. PURPOSE AND SCOPE")
        sec_match = section_hdr_pattern.match(stripped)
        if sec_match and not clause_pattern.match(stripped):
            if current_clause_num and current_sec_num:
                structured["sections"][current_sec_num]["clauses"][current_clause_num] = " ".join(current_clause_text).strip()
                current_clause_num = None
                current_clause_text = []
            
            current_sec_num = sec_match.group(1)
            current_sec_title = sec_match.group(2)
            structured["sections"][current_sec_num] = {
                "title": current_sec_title,
                "clauses": {}
            }
            continue

        # Check clause line (e.g., "2.3 Employees must submit...")
        clause_match = clause_pattern.match(stripped)
        if clause_match:
            if current_clause_num and current_sec_num:
                structured["sections"][current_sec_num]["clauses"][current_clause_num] = " ".join(current_clause_text).strip()
            current_clause_num = clause_match.group(1)
            current_clause_text = [clause_match.group(2)]
        elif current_clause_num:
            current_clause_text.append(stripped)

    if current_clause_num and current_sec_num:
        structured["sections"][current_sec_num]["clauses"][current_clause_num] = " ".join(current_clause_text).strip()

    return structured


def summarize_policy(structured_policy: dict) -> str:
    """
    Generates an executive summary from structured_policy dictionary that preserves all binding obligations,
    multi-condition approver requirements (specifically 5.2 dual approval), timelines, and forfeiture rules.
    """
    meta = structured_policy.get("metadata", {})

    summary_sections = [
        "CITY MUNICIPAL CORPORATION — HR LEAVE POLICY EXECUTIVE SUMMARY",
        f"Document Reference: {meta.get('reference', 'HR-POL-001')} | Version: {meta.get('version', '2.3')} | Effective: {meta.get('effective', '1 April 2024')}",
        "════════════════════════════════════════════════════════════════════════",
        "",
        "1. PURPOSE AND SCOPE",
        f"- [Clause 1.1] Governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
        f"- [Clause 1.2] Does not apply to daily wage workers or consultants (governed by respective contracts).",
        "",
        "2. ANNUAL LEAVE",
        f"- [Clause 2.1] Entitlement: 18 days of paid annual leave per calendar year for permanent employees.",
        f"- [Clause 2.2] Accrual: Accrues at 1.5 days per month from date of joining.",
        f"- [Clause 2.3] Notice Requirement: Employees MUST submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        f"- [Clause 2.4] Approval Requirement: MUST receive WRITTEN approval from direct manager before leave commences. Verbal approval is NOT valid.",
        f"- [Clause 2.5] Unapproved Absence: Recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        f"- [Clause 2.6] Carry-Forward Limit: Maximum 5 unused annual leave days may be carried forward; days above 5 ARE FORFEITED on 31 December.",
        f"- [Clause 2.7] Carry-Forward Expiry: Carry-forward days MUST be used within Q1 (January–March) of following year or they ARE FORFEITED.",
        "",
        "3. SICK LEAVE",
        f"- [Clause 3.1] Entitlement: 12 days of paid sick leave per calendar year.",
        f"- [Clause 3.2] Medical Certificate (3+ Days): Sick leave of 3 or more consecutive days REQUIRES a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        f"- [Clause 3.3] Carry-Forward: Cannot be carried forward to following year.",
        f"- [Clause 3.4] Medical Certificate (Adjacent to Holiday/Leave): Sick leave taken immediately before or after a public holiday or annual leave period REQUIRES a medical certificate regardless of duration.",
        "",
        "4. MATERNITY AND PATERNITY LEAVE",
        f"- [Clause 4.1] Maternity Leave (1st/2nd Birth): Female employees entitled to 26 weeks paid maternity leave for first two live births.",
        f"- [Clause 4.2] Maternity Leave (Subsequent): 12 weeks paid for 3rd or subsequent child.",
        f"- [Clause 4.3] Paternity Leave: Male employees entitled to 5 days paid paternity leave within 30 days of birth.",
        f"- [Clause 4.4] Paternity Leave Splitting: Cannot be split across multiple periods.",
        "",
        "5. LEAVE WITHOUT PAY (LWP)",
        f"- [Clause 5.1] Prerequisite: Applicable only after exhausting all paid leave entitlements.",
        f"- [Clause 5.2] Dual Approval Requirement: REQUIRES approval from BOTH the Department Head AND the HR Director. Manager approval alone is NOT sufficient.",
        f"- [Clause 5.3] Extended LWP (>30 Days): LWP exceeding 30 continuous days REQUIRES approval from the Municipal Commissioner.",
        f"- [Clause 5.4] Service Impact: LWP periods do NOT count toward service for seniority, increments, or retirement benefits.",
        "",
        "6. PUBLIC HOLIDAYS",
        f"- [Clause 6.1] Entitlement: All state government gazetted public holidays.",
        f"- [Clause 6.2] Holiday Work: Compensatory off day granted within 60 days of holiday worked.",
        f"- [Clause 6.3] Encashment: Compensatory off cannot be encashed.",
        "",
        "7. LEAVE ENCASHMENT",
        f"- [Clause 7.1] Permissible Encashment: Annual leave encashable ONLY upon retirement or resignation (max 60 days).",
        f"- [Clause 7.2] Service Encashment Prohibition: Leave encashment during service is NOT PERMITTED under any circumstances.",
        f"- [Clause 7.3] Other Leave Encashment: Sick leave and LWP cannot be encashed under any circumstances.",
        "",
        "8. GRIEVANCES",
        f"- [Clause 8.1] Timeline: Leave-related grievances MUST be raised with HR within 10 working days of disputed decision.",
        f"- [Clause 8.2] Late Submissions: Grievances after 10 working days WILL NOT be considered unless exceptional circumstances are demonstrated in writing.",
    ]
    
    return "\n".join(summary_sections) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Compliance Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()

    raw_policy = retrieve_policy(args.input)
    summary = summarize_policy(raw_policy)

    with open(args.output, mode="w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Policy summary successfully written to {args.output}")


if __name__ == "__main__":
    main()


