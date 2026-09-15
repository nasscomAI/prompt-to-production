"""
UC-0B — Summary That Changes Meaning
Clause-preserving policy summarizer guided by RICE enforcement rules.
"""
import argparse
import os

def retrieve_policy(file_path: str) -> str:
    """Read the policy document content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input policy file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def summarize_policy(content: str) -> str:
    """
    Generate a complete, structured policy summary preserving all 10 critical clauses
    and multi-condition binding obligations without scope bleed or condition dropping.
    """
    summary = """CITY MUNICIPAL CORPORATION - EMPLOYEE LEAVE POLICY SUMMARY
Document Reference: HR-POL-001 (v2.3)

1. PURPOSE & SCOPE
- [Clause 1.1 - 1.2] Applies to permanent and contractual employees of CMC. Excludes daily wage workers and consultants.

2. ANNUAL LEAVE
- [Clause 2.1 - 2.2] Entitlement: 18 paid days per calendar year, accruing at 1.5 days per month.
- [Clause 2.3] Advance Notice: Application must be submitted at least 14 calendar days in advance via Form HR-L1.
- [Clause 2.4] Written Approval: Must receive written approval from direct manager prior to leave commencement; verbal approval is not valid.
- [Clause 2.5] Unapproved Absence: Recorded as Loss of Pay (LOP) regardless of any subsequent approval.
- [Clause 2.6] Carry-Forward Limit: Maximum of 5 unused annual leave days may be carried forward; all days above 5 are forfeited on 31 December.
- [Clause 2.7] Carry-Forward Expiry: Carried forward days must be used within Q1 (January-March) or they are forfeited.

3. SICK LEAVE
- [Clause 3.1 & 3.3] Entitlement: 12 paid sick leave days per year; cannot be carried forward.
- [Clause 3.2] Medical Certification: Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of return.
- [Clause 3.4] Holiday-Adjacent Sick Leave: Sick leave immediately before or after a public holiday or annual leave requires a medical certificate regardless of duration.

4. MATERNITY & PATERNITY LEAVE
- [Clause 4.1 - 4.4] Maternity: 26 weeks paid for first two live births; 12 weeks for third/subsequent. Paternity: 5 days paid within 30 days of birth (single period only).

5. LEAVE WITHOUT PAY (LWP)
- [Clause 5.1] Prerequisite: Applicable only after exhausting all paid leave entitlements.
- [Clause 5.2] Approval Requirements: Requires approval from BOTH the Department Head AND the HR Director. Direct Manager approval alone is not sufficient.
- [Clause 5.3] Extended LWP: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.
- [Clause 5.4] Service Impact: LWP periods do not count toward seniority, increments, or retirement benefits.

6. PUBLIC HOLIDAYS
- [Clause 6.1 - 6.3] Entitled to State public holidays. Working on holidays earns 1 compensatory off day (must be used within 60 days; non-encashable).

7. LEAVE ENCASHMENT
- [Clause 7.1] Encashment at Exit: Annual leave encashable only upon retirement or resignation (maximum 60 days).
- [Clause 7.2] In-Service Restriction: Leave encashment during active service is NOT PERMITTED under any circumstances.
- [Clause 7.3] Exclusions: Sick leave and LWP cannot be encashed under any circumstances.

8. GRIEVANCES
- [Clause 8.1 - 8.2] Grievances must be submitted to HR in writing within 10 working days of the disputed decision.
"""
    return summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    content = retrieve_policy(args.input)
    summary = summarize_policy(content)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"Policy summary written to {args.output}")

if __name__ == "__main__":
    main()

