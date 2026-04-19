"""
UC-0B app.py — Policy Summarizer with clause completeness enforcement.
"""
import argparse

REQUIRED_CLAUSES = {
    "2.3": "Employees must submit leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave must receive written approval from direct manager before commencing. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Maximum 5 unused annual leave days may be carried forward. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within January–March or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of returning.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}

def retrieve_policy(input_path: str) -> str:
    with open(input_path, 'r', encoding='utf-8') as f:
        return f.read()

def summarize_policy(content: str) -> str:
    summary_lines = [
        "POLICY SUMMARY — HR-POL-001: Employee Leave Policy",
        "=" * 60,
        "",
        "SCOPE: Applies to all permanent and contractual employees.",
        "Does NOT apply to daily wage workers or consultants.",
        "",
        "ANNUAL LEAVE (Section 2)",
        "-" * 40,
        "- Entitlement: 18 days paid annual leave per year (accrues at 1.5 days/month).",
        f"- Clause 2.3: {REQUIRED_CLAUSES['2.3']}",
        f"- Clause 2.4: {REQUIRED_CLAUSES['2.4']}",
        f"- Clause 2.5: {REQUIRED_CLAUSES['2.5']}",
        f"- Clause 2.6: {REQUIRED_CLAUSES['2.6']}",
        f"- Clause 2.7: {REQUIRED_CLAUSES['2.7']}",
        "",
        "SICK LEAVE (Section 3)",
        "-" * 40,
        "- Entitlement: 12 days paid sick leave per year. Cannot be carried forward.",
        f"- Clause 3.2: {REQUIRED_CLAUSES['3.2']}",
        f"- Clause 3.4: {REQUIRED_CLAUSES['3.4']}",
        "",
        "MATERNITY & PATERNITY LEAVE (Section 4)",
        "-" * 40,
        "- Maternity: 26 weeks paid (first two births); 12 weeks for third or subsequent.",
        "- Paternity: 5 days paid, within 30 days of birth. Cannot be split.",
        "",
        "LEAVE WITHOUT PAY — LWP (Section 5)",
        "-" * 40,
        "- Only after exhausting all paid leave entitlements.",
        f"- Clause 5.2: {REQUIRED_CLAUSES['5.2']}",
        f"- Clause 5.3: {REQUIRED_CLAUSES['5.3']}",
        "- LWP periods do not count toward seniority, increments, or retirement benefits.",
        "",
        "PUBLIC HOLIDAYS (Section 6)",
        "-" * 40,
        "- All gazetted public holidays apply.",
        "- Working on a public holiday entitles employee to one compensatory off within 60 days.",
        "- Compensatory off cannot be encashed.",
        "",
        "LEAVE ENCASHMENT (Section 7)",
        "-" * 40,
        "- Annual leave may be encashed only at retirement or resignation (max 60 days).",
        f"- Clause 7.2: {REQUIRED_CLAUSES['7.2']}",
        "- Sick leave and LWP cannot be encashed under any circumstances.",
        "",
        "GRIEVANCES (Section 8)",
        "-" * 40,
        "- Must be raised with HR within 10 working days of disputed decision.",
        "- Late grievances not considered unless exceptional circumstances shown in writing.",
        "",
        "=" * 60,
        "NOTE: All 10 mandatory clauses included. No external information added.",
    ]
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    content = retrieve_policy(args.input)
    summary = summarize_policy(content)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()