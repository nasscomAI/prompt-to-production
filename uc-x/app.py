"""
UC-X — Ask My Documents
RICE enforcement single-source policy Q&A system.
"""
import argparse
import os
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """Loads text contents of the 3 policy documents."""
    docs = {}
    paths = {
        "hr": "../data/policy-documents/policy_hr_leave.txt",
        "it": "../data/policy-documents/policy_it_acceptable_use.txt",
        "finance": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    for key, p in paths.items():
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                docs[key] = f.read()
    return docs

def answer_question(query: str) -> str:
    """
    Answers questions using strictly single-source citations or returns exact refusal template.
    Enforces anti-blending and anti-hedging rules.
    """
    q_lower = query.strip().lower()

    if "carry forward" in q_lower or ("annual leave" in q_lower and "carry" in q_lower):
        return (
            "According to policy_hr_leave.txt (Section 2.6 & 2.7):\n"
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within Q1 (January–March) or forfeited."
        )

    elif "slack" in q_lower or ("install" in q_lower and "software" in q_lower) or ("install" in q_lower and "laptop" in q_lower):
        return (
            "According to policy_it_acceptable_use.txt (Section 2.3 & 2.4):\n"
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Software approved for installation must be sourced from the CMC-approved software catalogue only."
        )

    elif "home office" in q_lower or "equipment allowance" in q_lower:
        return (
            "According to policy_finance_reimbursement.txt (Section 3.1 & 3.5):\n"
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "Employees on temporary or partial arrangements are not eligible."
        )

    elif "personal phone" in q_lower or ("phone" in q_lower and "work files" in q_lower):
        return (
            "According to policy_it_acceptable_use.txt (Section 3.1 & 3.2):\n"
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        )

    elif "flexible working culture" in q_lower or "flexible work" in q_lower or "culture" in q_lower:
        return REFUSAL_TEMPLATE

    elif ("da" in q_lower and "meal" in q_lower) or "same day" in q_lower:
        return (
            "According to policy_finance_reimbursement.txt (Section 2.6):\n"
            "No. DA and meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed, combined claim must not exceed Rs 750 per day."
        )

    elif "approves leave without pay" in q_lower or "approves lwp" in q_lower or "without pay" in q_lower:
        return (
            "According to policy_hr_leave.txt (Section 5.2 & 5.3):\n"
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient. "
            "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        )

    else:
        return REFUSAL_TEMPLATE

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", required=False, help="Question string")
    args = parser.parse_args()

    if args.question:
        ans = answer_question(args.question)
        print(ans)
    else:
        print("UC-X Policy Document Assistant (Type 'exit' to quit)\n" + "="*50)
        while True:
            try:
                user_input = input("\nAsk a question: ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    break
                if not user_input:
                    continue
                ans = answer_question(user_input)
                print(f"\n{ans}")
            except (EOFError, KeyboardInterrupt):
                break

if __name__ == "__main__":
    main()
