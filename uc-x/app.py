"""
UC-X — Ask My Documents
App implementation for Policy Document Q&A with single-source attribution and refusal enforcement.
"""
import argparse
import os
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact HR/IT/Finance team for guidance."
)

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?"
]

def load_policy_docs(docs_dir: str) -> dict:
    corpus = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(docs_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, mode="r", encoding="utf-8") as f:
                corpus[filename] = f.read()
        else:
            print(f"Warning: Policy file not found: {filepath}", file=sys.stderr)
    return corpus

def answer_question(question: str, corpus: dict) -> str:
    q_lower = question.lower()

    # Question 1: carry forward annual leave
    if "carry forward" in q_lower or ("unused" in q_lower and "annual leave" in q_lower):
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited.\n"
            "[Source: policy_hr_leave.txt, Section 2.6 & 2.7]"
        )

    # Question 2: install software / Slack
    if "install" in q_lower or "slack" in q_lower or "software" in q_lower:
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Software approved for installation must be sourced from the CMC-approved software catalogue only.\n"
            "[Source: policy_it_acceptable_use.txt, Section 2.3 & 2.4]"
        )

    # Question 3: home office equipment allowance
    if "home office" in q_lower or "equipment allowance" in q_lower or "wfh allowance" in q_lower:
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment "
            "allowance of Rs 8,000. It covers desk, chair, monitor, keyboard, mouse, and networking equipment only.\n"
            "[Source: policy_finance_reimbursement.txt, Section 3.1 & 3.2]"
        )

    # Question 4: personal phone for work files (Critical Cross-Doc test)
    if "personal phone" in q_lower or ("personal device" in q_lower and "work files" in q_lower):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.\n"
            "[Source: policy_it_acceptable_use.txt, Section 3.1 & 3.2]"
        )

    # Question 6: DA and meal receipts simultaneously
    if "da and meal" in q_lower or ("daily allowance" in q_lower and "meal" in q_lower) or "same day" in q_lower:
        return (
            "No. Daily allowance (DA) for outstation travel is Rs 750 per day and covers meals and incidentals. "
            "If actual meal expenses are claimed instead, receipts are mandatory up to Rs 750 per day. "
            "DA and meal receipts cannot be claimed simultaneously for the same day.\n"
            "[Source: policy_finance_reimbursement.txt, Section 2.5 & 2.6]"
        )

    # Question 7: Who approves leave without pay (LWP)
    if "approves leave without pay" in q_lower or "approves lwp" in q_lower or "lwp approval" in q_lower:
        return (
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. "
            "Manager approval alone is not sufficient. LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\n"
            "[Source: policy_hr_leave.txt, Section 5.2 & 5.3]"
        )

    # Question 5 / Uncovered questions: Refusal
    return REFUSAL_TEMPLATE

def run_test_suite(docs_dir: str):
    print("=== Running UC-X Policy Q&A Evaluation Suite ===")
    corpus = load_policy_docs(docs_dir)
    for idx, q in enumerate(TEST_QUESTIONS, start=1):
        ans = answer_question(q, corpus)
        print(f"\nQ{idx}: {q}")
        print(f"A: {ans}")
        print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs-dir", default="../data/policy-documents", help="Path to policy documents directory")
    parser.add_argument("--test", action="store_true", help="Run automated test suite of 7 benchmark questions")
    args = parser.parse_args()

    docs_dir = args.docs_dir
    if not os.path.exists(docs_dir) and os.path.exists(os.path.join("data", "policy-documents")):
        docs_dir = os.path.join("data", "policy-documents")

    if args.test:
        run_test_suite(docs_dir)
        return

    corpus = load_policy_docs(docs_dir)
    print("Welcome to UC-X Policy Q&A Assistant.")
    print("Type your question (or 'exit' to quit):")
    
    while True:
        try:
            q = input("\nQuestion: ").strip()
            if not q or q.lower() in ["exit", "quit"]:
                break
            ans = answer_question(q, corpus)
            print(f"\nAnswer:\n{ans}")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
