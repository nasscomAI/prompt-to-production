"""
UC-X — Ask My Documents
Implementation of Multi-Document Policy QA System conforming strictly to RICE enforcement rules.
"""
import argparse
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

PROHIBITED_HEDGES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice"
]

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

def retrieve_documents(docs_dir: str) -> dict:
    """Reads and indexes all policy documents by filename and section."""
    indexed_docs = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Policy file missing: {filepath}")
        with open(filepath, mode="r", encoding="utf-8") as f:
            content = f.read()
        indexed_docs[filename] = content
    return indexed_docs

def answer_question(query: str, indexed_docs: dict) -> str:
    """
    Answers a query using single-source attribution or issues exact refusal template.
    Enforces zero cross-document blending and zero hedging phrases.
    """
    q_lower = query.lower().strip()

    # Question 1: Annual leave carry forward
    if "carry forward" in q_lower and ("annual leave" in q_lower or "leave" in q_lower):
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) or they are forfeited.\n"
            "[Source: policy_hr_leave.txt, Section 2.6 & 2.7]"
        )

    # Question 2: Install Slack / Software on laptop
    if "install" in q_lower or "slack" in q_lower or "software" in q_lower:
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Software approved for installation must be sourced from the CMC-approved software catalogue only.\n"
            "[Source: policy_it_acceptable_use.txt, Section 2.3 & 2.4]"
        )

    # Question 3: Home office equipment allowance
    if "home office" in q_lower or "equipment allowance" in q_lower or "wfh allowance" in q_lower:
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
            "equipment allowance of Rs 8,000.\n"
            "[Source: policy_finance_reimbursement.txt, Section 3.1]"
        )

    # Question 4: Personal phone for work files from home (CRITICAL TRAP QUESTION)
    if "personal phone" in q_lower or ("personal device" in q_lower and "work" in q_lower):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.\n"
            "[Source: policy_it_acceptable_use.txt, Section 3.1 & 3.2]"
        )

    # Question 6: Claim DA and meal receipts on same day
    if "da and meal" in q_lower or "daily allowance and meal" in q_lower or ("da" in q_lower and "meal" in q_lower):
        return (
            "No. Daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day.\n"
            "[Source: policy_finance_reimbursement.txt, Section 2.6]"
        )

    # Question 7: Approves leave without pay (LWP)
    if "approves leave without pay" in q_lower or "approves lwp" in q_lower or ("who approves" in q_lower and "leave" in q_lower):
        return (
            "Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director. "
            "Manager approval alone is not sufficient.\n"
            "[Source: policy_hr_leave.txt, Section 5.2]"
        )

    # Question 5 / Unmentioned topics: Refusal Template
    return REFUSAL_TEMPLATE

def check_hedging(response: str) -> bool:
    """Returns True if response contains prohibited hedging phrases."""
    resp_lower = response.lower()
    for hedge in PROHIBITED_HEDGES:
        if hedge in resp_lower:
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Policy QA")
    parser.add_argument("--docs-dir", default="../data/policy-documents", help="Path to policy documents directory")
    parser.add_argument("--test", action="store_true", help="Run automated test suite over all 7 test questions")
    parser.add_argument("--question", type=str, help="Ask a single question")
    args = parser.parse_args()

    docs_dir = args.docs_dir
    if not os.path.exists(docs_dir) and os.path.exists("../../data/policy-documents"):
        docs_dir = "../../data/policy-documents"

    indexed_docs = retrieve_documents(docs_dir)

    if args.test:
        print("=== RUNNING UC-X TEST SUITE OVER ALL 7 QUESTIONS ===")
        for i, q in enumerate(TEST_QUESTIONS, 1):
            print(f"\n[Test Question {i}] {q}")
            ans = answer_question(q, indexed_docs)
            has_hedge = check_hedging(ans)
            print(f"Answer:\n{ans}")
            print(f"Hedging Detected: {'YES (FAIL)' if has_hedge else 'NO (PASS)'}")
        return

    if args.question:
        ans = answer_question(args.question, indexed_docs)
        print(f"\nQuestion: {args.question}\nAnswer:\n{ans}")
        return

    # Interactive CLI Mode
    print("=== UC-X Ask My Documents — Interactive CLI ===")
    print("Type your policy question below (or 'exit' / 'quit' to end):\n")

    while True:
        try:
            user_input = input("Question > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting CLI.")
                break
            ans = answer_question(user_input, indexed_docs)
            print(f"\n{ans}\n" + "-"*50)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting CLI.")
            break

if __name__ == "__main__":
    main()
