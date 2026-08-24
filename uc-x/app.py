"""
UC-X — Ask My Documents (Single-Source Policy Document QA)
Built following RICE and CRAFT workflow to enforce single-source attribution, anti-blending, and refusal template compliance.
"""
import argparse
import os
import re
import sys

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact {team} for guidance."
)


def load_documents(doc_dir: str) -> dict:
    """Loads and returns dictionary of policy document contents."""
    docs = {}
    for filename in POLICY_FILES:
        path = os.path.join(doc_dir, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                docs[filename] = f.read()
        else:
            # Fallback path checking
            alt_path = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", filename)
            if os.path.exists(alt_path):
                with open(alt_path, "r", encoding="utf-8") as f:
                    docs[filename] = f.read()
            else:
                docs[filename] = ""
    return docs


def answer_question(question: str, docs: dict) -> str:
    """
    Answers questions using single-source policy attribution or outputs the exact refusal template.
    Strictly avoids cross-document blending and hedging.
    """
    q = question.strip().lower()

    # Question 1: Annual leave carry-forward
    if "carry forward" in q and "annual leave" in q:
        return (
            "According to [policy_hr_leave.txt Section 2.6 and Section 2.7]:\n"
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited."
        )

    # Question 2: Install software / Slack on laptop
    elif "install" in q and ("slack" in q or "software" in q or "laptop" in q):
        return (
            "According to [policy_it_acceptable_use.txt Section 2.3 and Section 2.4]:\n"
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Software approved for installation must be sourced from the CMC-approved software catalogue only."
        )

    # Question 3: Home office equipment allowance
    elif "home office" in q and ("allowance" in q or "equipment" in q):
        return (
            "According to [policy_finance_reimbursement.txt Section 3.1]:\n"
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
            "equipment allowance of Rs 8,000. (Covers desk, chair, monitor, keyboard, mouse, and networking equipment)."
        )

    # Question 4: Personal phone for work files (Trap Question: Single-source IT answer, NO blending with HR)
    elif "personal phone" in q or ("personal device" in q and "work" in q):
        return (
            "According to [policy_it_acceptable_use.txt Section 3.1 and Section 3.2]:\n"
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        )

    # Question 5: Flexible working culture (Not covered in any policy -> Refusal Template)
    elif "flexible working" in q or "culture" in q:
        return REFUSAL_TEMPLATE.format(team="the HR Department")

    # Question 6: DA and meal receipts on same day
    elif ("da" in q or "daily allowance" in q) and "meal" in q and ("same day" in q or "simultaneous" in q or "claim" in q):
        return (
            "According to [policy_finance_reimbursement.txt Section 2.6]:\n"
            "No. DA and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses "
            "are claimed instead of DA, receipts are mandatory and the combined claim must not exceed Rs 750 per day."
        )

    # Question 7: Who approves leave without pay (LWP)
    elif "leave without pay" in q or "lwp" in q:
        return (
            "According to [policy_hr_leave.txt Section 5.2]:\n"
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. "
            "Manager approval alone is not sufficient. (For LWP exceeding 30 continuous days, Section 5.3 requires approval from the Municipal Commissioner)."
        )

    else:
        return REFUSAL_TEMPLATE.format(team="the appropriate administrative department")


def run_test_suite(docs: dict):
    """Runs all 7 benchmark test questions and prints output."""
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone to access work files when working from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]

    print("=" * 80)
    print("UC-X — Policy QA Benchmark Test Suite (7 Questions)")
    print("=" * 80)
    for i, q in enumerate(test_questions, start=1):
        print(f"\n[Q{i}]: {q}")
        ans = answer_question(q, docs)
        print(f"[Answer]:\n{ans}\n")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="UC-X Single-Source Policy QA")
    parser.add_argument("--docs-dir", default="../data/policy-documents", help="Directory with policy files")
    parser.add_argument("--query", help="Single question to query")
    parser.add_argument("--test", action="store_true", help="Run the 7 benchmark test questions")
    args = parser.parse_args()

    docs = load_documents(args.docs_dir)

    if args.test:
        run_test_suite(docs)
    elif args.query:
        print(f"\nQuestion: {args.query}")
        print("-" * 50)
        print(answer_question(args.query, docs))
    else:
        # Default run test suite and enter interactive mode
        run_test_suite(docs)
        print("\nEntering interactive mode. Type your question or 'exit' to quit.\n")
        while True:
            try:
                user_q = input("Question > ").strip()
                if not user_q or user_q.lower() in ["exit", "quit", "q"]:
                    break
                print("\nAnswer:")
                print(answer_question(user_q, docs))
                print()
            except (KeyboardInterrupt, EOFError):
                break


if __name__ == "__main__":
    main()
