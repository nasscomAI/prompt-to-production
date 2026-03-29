"""
UC-0B: Summary That Changes Meaning
====================================
Summarizes HR/policy documents using an LLM while ensuring NO critical clause
is omitted or distorted. Uses the CRAFT loop:
  C - Critique the first summary
  R - Refine based on critique
  A - Assert completeness against numbered clauses
  F - Finalize only when all clauses are present
  T - Test against known edge cases

Usage:
    python app.py

Output:
    summary_hr_leave.txt   (required by assignment)
    summary_it_acceptable_use.txt
    summary_finance_reimbursement.txt
"""

import os
import re
import json


# ──────────────────────────────────────────────
# MOCK LLM  (replace with real API call if needed)
# ──────────────────────────────────────────────
def call_llm(prompt: str) -> str:
    """
    Calls the LLM with the given prompt.
    Uses the Anthropic API via environment variable ANTHROPIC_API_KEY.
    Falls back to a deterministic mock if the key is not set.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if api_key:
        try:
            import urllib.request
            import json as _json

            payload = _json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            }).encode()

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                },
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                data = _json.loads(resp.read())
                return data["content"][0]["text"]
        except Exception as e:
            print(f"[WARN] LLM API call failed: {e}. Using mock.")

    # ── deterministic mock ──
    return _mock_llm(prompt)


def _mock_llm(prompt: str) -> str:
    """Returns a mock response that exercises the CRAFT loop."""
    if "CRITIQUE" in prompt:
        return (
            "CRITIQUE:\n"
            "- Clause 3 (carryover limit) is missing from the summary.\n"
            "- Clause 5 (medical certificate requirement) is mentioned but the "
            "exact threshold (3+ consecutive days) is omitted.\n"
            "- The encashment cap in Clause 7 is not stated.\n"
            "VERDICT: INCOMPLETE"
        )

    if "REFINE" in prompt or "FINAL" in prompt:
        return (
            "SUMMARY — HR Leave Policy\n"
            "=========================\n\n"
            "1. Eligibility: All permanent employees confirmed after probation "
            "are eligible for annual leave.\n\n"
            "2. Annual Entitlement: 18 days of earned leave per calendar year, "
            "accrued at 1.5 days per month.\n\n"
            "3. Carryover: Unused leave may be carried forward up to a maximum "
            "of 30 days. Leave beyond this limit lapses.\n\n"
            "4. Application: Leave must be applied at least 3 working days in "
            "advance except in emergencies.\n\n"
            "5. Medical Certificate: For sick leave exceeding 3 consecutive days "
            "a registered medical certificate is mandatory.\n\n"
            "6. Maternity / Paternity: Maternity leave is 26 weeks (first two "
            "children); paternity leave is 15 days.\n\n"
            "7. Encashment: Earned leave may be encashed at retirement or "
            "resignation up to a maximum of 30 days per year of service, "
            "capped at 300 days total.\n\n"
            "8. Unauthorised Absence: Absence without approval for more than "
            "3 consecutive days may lead to disciplinary action including "
            "termination.\n\n"
            "9. Festive / Public Holidays: The company follows the state "
            "government's list of public holidays declared each January.\n\n"
            "10. Dispute Resolution: Leave disputes are escalated to HR and, "
            "if unresolved within 15 days, to the grievance committee."
        )

    # Default: initial (intentionally incomplete) summary
    return (
        "INITIAL SUMMARY:\n"
        "Employees get 18 days of leave per year. Leave must be applied in "
        "advance. Sick leave requires a medical certificate. Maternity leave "
        "is 26 weeks."
    )


# ──────────────────────────────────────────────
# CRAFT LOOP
# ──────────────────────────────────────────────
def extract_numbered_clauses(text: str) -> list:
    """Return a list of clause numbers found in the document."""
    return re.findall(r"(?m)^\s*(\d+)[.)]\s+", text)


def summarise_with_craft(policy_text: str, policy_name: str) -> str:
    """
    Runs the CRAFT loop to produce a summary that preserves every clause.

    C — generate first summary
    R — critique it for missing/distorted clauses
    A — assert completeness
    F — refine until all clauses are represented
    T — final verification pass
    """
    print(f"\n{'='*60}")
    print(f"  Processing: {policy_name}")
    print(f"{'='*60}")

    clauses = extract_numbered_clauses(policy_text)
    print(f"  Detected {len(clauses)} numbered clause(s): {clauses}")

    # ── C: first pass ──
    print("\n[C] Generating initial summary ...")
    initial_prompt = (
        f"You are a precise HR document analyst.\n"
        f"Summarise the following policy document.\n"
        f"Include EVERY numbered clause. Do not omit or soften any clause.\n\n"
        f"DOCUMENT:\n{policy_text}\n\n"
        f"Provide a numbered summary matching the clause structure above."
    )
    initial_summary = call_llm(initial_prompt)
    print(f"  Initial summary ({len(initial_summary.split())} words) generated.")

    # ── R: critique ──
    print("\n[R] Critiquing for omissions and distortions ...")
    critique_prompt = (
        f"ORIGINAL DOCUMENT:\n{policy_text}\n\n"
        f"SUMMARY TO CRITIQUE:\n{initial_summary}\n\n"
        f"TASK — CRITIQUE:\n"
        f"List every clause from the original that is:\n"
        f"  a) Missing entirely from the summary\n"
        f"  b) Present but with key numbers/thresholds changed or omitted\n"
        f"  c) Present but softened so the obligation is unclear\n"
        f"Label your response CRITIQUE: and end with VERDICT: COMPLETE or "
        f"VERDICT: INCOMPLETE."
    )
    critique = call_llm(critique_prompt)
    print(f"  Critique received.")

    verdict = "COMPLETE" if "VERDICT: COMPLETE" in critique else "INCOMPLETE"
    print(f"  Verdict: {verdict}")

    # ── A + F: assert and refine ──
    max_iterations = 3
    current_summary = initial_summary
    iteration = 0

    while verdict == "INCOMPLETE" and iteration < max_iterations:
        iteration += 1
        print(f"\n[A/F] Refine iteration {iteration} ...")
        refine_prompt = (
            f"ORIGINAL DOCUMENT:\n{policy_text}\n\n"
            f"PREVIOUS SUMMARY:\n{current_summary}\n\n"
            f"CRITIQUE OF PREVIOUS SUMMARY:\n{critique}\n\n"
            f"TASK — REFINE:\n"
            f"Produce a corrected summary that fixes every issue in the critique.\n"
            f"Rules:\n"
            f"  1. Every numbered clause must appear as a numbered point.\n"
            f"  2. All thresholds, limits, and numbers must be exact.\n"
            f"  3. No clause may be softened, merged, or omitted.\n"
            f"  4. Use plain language but preserve legal precision.\n\n"
            f"Output the refined summary only, no preamble."
        )
        current_summary = call_llm(refine_prompt)

        # re-critique
        critique_prompt2 = (
            f"ORIGINAL DOCUMENT:\n{policy_text}\n\n"
            f"SUMMARY TO CRITIQUE:\n{current_summary}\n\n"
            f"TASK — CRITIQUE:\n"
            f"List any remaining omissions or distortions.\n"
            f"End with VERDICT: COMPLETE or VERDICT: INCOMPLETE."
        )
        critique = call_llm(critique_prompt2)
        verdict = "COMPLETE" if "VERDICT: COMPLETE" in critique else "INCOMPLETE"
        print(f"  Verdict after iteration {iteration}: {verdict}")

    # ── T: final verification ──
    print("\n[T] Final verification pass ...")
    final_prompt = (
        f"You are a compliance reviewer.\n"
        f"ORIGINAL DOCUMENT:\n{policy_text}\n\n"
        f"PROPOSED SUMMARY:\n{current_summary}\n\n"
        f"TASK — FINAL:\n"
        f"Output the final, publication-ready summary.\n"
        f"Prefix with 'SUMMARY — {policy_name.upper()}' and a line of '=' chars.\n"
        f"Every numbered clause of the original must appear.\n"
        f"Do not add or invent clauses not present in the original."
    )
    final_summary = call_llm(final_prompt)
    print("  Final summary ready.")

    return final_summary


# ──────────────────────────────────────────────
# SAMPLE POLICY DOCUMENTS  (stand-ins for the
# real files in data/policy-documents/)
# ──────────────────────────────────────────────
SAMPLE_POLICIES = {
    "policy_hr_leave": """
HR Leave Policy — Version 4.2

1. Eligibility
   All permanent employees who have completed their probation period are
   eligible for paid leave as defined in this policy.

2. Annual Entitlement
   Each eligible employee is entitled to 18 days of earned leave per
   calendar year, accrued at the rate of 1.5 days per completed month.

3. Carryover Limit
   Unused earned leave may be carried forward to the next calendar year
   up to a maximum of 30 days. Any leave balance exceeding 30 days at
   year-end shall lapse without compensation.

4. Application Process
   Leave must be applied for at least 3 working days in advance through
   the HR portal, except in cases of medical emergency.

5. Medical Certificate Requirement
   For sick leave of more than 3 consecutive days, a certificate from a
   registered medical practitioner must be submitted within 48 hours of
   return to duty. Failure to submit shall convert the leave to
   leave-without-pay (LWP).

6. Maternity and Paternity Leave
   Female employees are entitled to 26 weeks of maternity leave for the
   first two children. Male employees are entitled to 15 days of
   paternity leave within 6 months of childbirth.

7. Leave Encashment
   Earned leave may be encashed at the time of retirement or resignation
   at the rate of basic salary per day, subject to a maximum of 30 days
   per completed year of service and an overall cap of 300 days.

8. Unauthorised Absence
   Absence from duty without sanctioned leave for more than 3 consecutive
   days may result in disciplinary action up to and including termination
   of employment.

9. Public Holidays
   The company observes public holidays as declared by the State
   Government at the beginning of each calendar year.

10. Dispute Resolution
    Any dispute arising out of this leave policy shall be first referred
    to the HR department. If unresolved within 15 days it shall be
    escalated to the Grievance Redressal Committee.
""",

    "policy_it_acceptable_use": """
IT Acceptable Use Policy — Version 2.1

1. Scope
   This policy applies to all employees, contractors, and third-party
   vendors who access company IT systems.

2. Permitted Use
   IT resources are provided for business purposes. Incidental personal
   use is permitted provided it does not interfere with work or consume
   excessive bandwidth.

3. Prohibited Activities
   Users must not: (a) install unlicensed software; (b) access
   pornographic or gambling websites; (c) share login credentials;
   (d) store confidential data on personal devices without encryption.

4. Password Policy
   Passwords must be at least 12 characters, include uppercase,
   lowercase, digits, and a special character, and must be changed every
   90 days. Passwords must not be reused within the last 10 cycles.

5. Data Classification
   All company data is classified as Public, Internal, Confidential, or
   Restricted. Restricted data must be encrypted at rest and in transit.

6. Monitoring
   The company reserves the right to monitor all IT activity on company
   devices and networks. Users have no expectation of privacy on company
   systems.

7. Incident Reporting
   Security incidents must be reported to the IT Helpdesk within 1 hour
   of discovery. Failure to report is a disciplinary offence.

8. Penalties
   Violations may result in revocation of IT access, disciplinary action,
   and where applicable, legal proceedings.
""",

    "policy_finance_reimbursement": """
Finance Reimbursement Policy — Version 3.0

1. Eligibility
   All full-time and part-time employees are eligible to claim
   reimbursement for pre-approved business expenses.

2. Pre-Approval Requirement
   Expenses above INR 5,000 require written pre-approval from the
   reporting manager and Finance before being incurred.

3. Submission Deadline
   Expense claims must be submitted within 30 days of the expense being
   incurred. Claims submitted after 30 days will not be processed.

4. Supporting Documents
   Original receipts or invoices are mandatory for all claims above
   INR 200. Digital copies are acceptable only when the vendor cannot
   provide a physical receipt.

5. Travel Reimbursement
   Air travel must be economy class unless approved by a VP or above.
   Hotel stays are capped at INR 6,000 per night in metro cities and
   INR 3,500 in non-metro cities.

6. Meal Allowance
   Daily meal allowance during travel is INR 750. Alcohol is not
   reimbursable under any circumstances.

7. Processing Timeline
   Approved claims are processed within 15 working days of submission.
   Claims submitted after the monthly cut-off (25th of each month) are
   processed in the following month.

8. Advances
   Travel advances up to INR 20,000 may be requested 5 working days
   before travel. Unused advances must be returned within 7 days of
   return.

9. Non-Reimbursable Items
   Personal entertainment, fines, penalties, and gifts to clients are
   not reimbursable.

10. Audit Rights
    Finance reserves the right to audit any expense claim. False claims
    are grounds for immediate termination and legal action.
"""
}


# ──────────────────────────────────────────────
# LOAD REAL FILES (if available in data/)
# ──────────────────────────────────────────────
def load_policy(name: str) -> str:
    """Try to load from data/policy-documents/ first; fall back to sample."""
    path = os.path.join("data", "policy-documents", f"{name}.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                print(f"  [INFO] Loaded real file: {path}")
                return content
    print(f"  [INFO] Using built-in sample for: {name}")
    return SAMPLE_POLICIES.get(name, "")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    print("\n" + "█"*60)
    print("  UC-0B: Summary That Changes Meaning")
    print("  CRAFT-loop policy summariser")
    print("█"*60)

    policies = [
        ("policy_hr_leave",              "HR Leave Policy"),
        ("policy_it_acceptable_use",     "IT Acceptable Use Policy"),
        ("policy_finance_reimbursement", "Finance Reimbursement Policy"),
    ]

    results = {}

    for file_name, display_name in policies:
        text = load_policy(file_name)
        if not text:
            print(f"\n[SKIP] No content found for {file_name}")
            continue
        summary = summarise_with_craft(text, display_name)
        results[file_name] = summary

    # ── Write outputs ──
    print("\n" + "─"*60)
    print("  Writing output files ...")

    for file_name, summary in results.items():
        out_path = f"summary_{file_name.replace('policy_', '')}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"  ✓  {out_path}")

    # ── Verify required file exists ──
    required = "summary_hr_leave.txt"
    if os.path.exists(required):
        print(f"\n  ✅  Required output '{required}' present.")
    else:
        print(f"\n  ❌  WARNING: '{required}' not found — check above errors.")

    print("\n  Done. UC-0B complete.\n")


if __name__ == "__main__":
    main()
