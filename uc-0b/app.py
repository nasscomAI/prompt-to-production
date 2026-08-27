"""
UC-0B — HR Policy Summariser
Extracts every numbered clause verbatim so no obligation, condition, or
binding verb can be dropped or softened during summarisation.
"""
import argparse
import re


def retrieve_policy(file_path: str) -> str:
    with open(file_path, encoding="utf-8") as f:
        return f.read()


def _extract_clause(text: str, clause_num: str) -> str:
    """Return the full text of a numbered clause, collapsed to one line."""
    pattern = rf"^\s*{re.escape(clause_num)}\s+(.*?)(?=^\s*\d+\.\d+\s|\n[═]+|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not match:
        return f"[CLAUSE {clause_num} NOT FOUND — REVIEW REQUIRED]"
    return " ".join(match.group(1).split())


def summarize_policy(policy_text: str) -> str:
    all_clauses = [
        "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.1", "3.2", "3.3", "3.4",
        "4.1", "4.2", "4.3", "4.4",
        "5.1", "5.2", "5.3", "5.4",
        "6.1", "6.2", "6.3",
        "7.1", "7.2", "7.3",
        "8.1", "8.2",
    ]
    c = {num: _extract_clause(policy_text, num) for num in all_clauses}

    return f"""CITY MUNICIPAL CORPORATION
HR Leave Policy — Summary (HR-POL-001 v2.3, Effective 1 April 2024)

Source: policy_hr_leave.txt
Note: All clauses extracted verbatim from source. Binding verbs (must/will/
requires/not permitted) are preserved exactly as written.

═══════════════════════════════════════════════════════════
1. SCOPE
═══════════════════════════════════════════════════════════
Applies to permanent and contractual employees of City Municipal Corporation.
Does NOT apply to daily wage workers or consultants (governed by their contracts).

═══════════════════════════════════════════════════════════
2. ANNUAL LEAVE
═══════════════════════════════════════════════════════════
2.1  Entitlement:        {c['2.1']}
2.2  Accrual:            {c['2.2']}
2.3  Notice [CRITICAL]:  {c['2.3']}
2.4  Approval [CRITICAL]: {c['2.4']}
2.5  Unapproved absence [CRITICAL]: {c['2.5']}
2.6  Carry-forward [CRITICAL]: {c['2.6']}
2.7  Carry-forward deadline [CRITICAL]: {c['2.7']}

═══════════════════════════════════════════════════════════
3. SICK LEAVE
═══════════════════════════════════════════════════════════
3.1  Entitlement:        {c['3.1']}
3.2  Medical certificate [CRITICAL]: {c['3.2']}
3.3  Carry-forward:      {c['3.3']}
3.4  Holiday adjacency [CRITICAL]: {c['3.4']}

═══════════════════════════════════════════════════════════
4. MATERNITY AND PATERNITY LEAVE
═══════════════════════════════════════════════════════════
4.1  Maternity (births 1–2): {c['4.1']}
4.2  Maternity (birth 3+):   {c['4.2']}
4.3  Paternity:              {c['4.3']}
4.4  Paternity restriction:  {c['4.4']}

═══════════════════════════════════════════════════════════
5. LEAVE WITHOUT PAY (LWP)
═══════════════════════════════════════════════════════════
5.1  Eligibility:        {c['5.1']}
5.2  Approval — TWO approvers required [CRITICAL]: {c['5.2']}
5.3  Extended LWP [CRITICAL]: {c['5.3']}
5.4  Service impact:     {c['5.4']}

═══════════════════════════════════════════════════════════
6. PUBLIC HOLIDAYS
═══════════════════════════════════════════════════════════
6.1  Entitlement:        {c['6.1']}
6.2  Working on holiday: {c['6.2']}
6.3  Compensatory off:   {c['6.3']}

═══════════════════════════════════════════════════════════
7. LEAVE ENCASHMENT
═══════════════════════════════════════════════════════════
7.1  At retirement/resignation: {c['7.1']}
7.2  During service [CRITICAL]: {c['7.2']}
7.3  Sick leave / LWP:  {c['7.3']}

═══════════════════════════════════════════════════════════
8. GRIEVANCES
═══════════════════════════════════════════════════════════
8.1  {c['8.1']}
8.2  {c['8.2']}
"""


def main():
    parser = argparse.ArgumentParser(description="Summarise HR leave policy")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")
    print("Verify: check all 10 critical clauses are present with binding verbs intact.")


if __name__ == "__main__":
    main()
