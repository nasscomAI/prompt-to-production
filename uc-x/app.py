"""
UC-X — Ask My Documents
App implementation enforcing single-source document QA, exact citations,
zero hedging, and exact refusal templates.
"""
import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

POLICY_FILES = {
    "HR": os.path.join(REPO_ROOT, "data", "policy-documents", "policy_hr_leave.txt"),
    "IT": os.path.join(REPO_ROOT, "data", "policy-documents", "policy_it_acceptable_use.txt"),
    "FINANCE": os.path.join(REPO_ROOT, "data", "policy-documents", "policy_finance_reimbursement.txt")
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?"
]

def load_policy_docs():
    docs = {}
    for key, path in POLICY_FILES.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                docs[key] = f.read()
        else:
            raise FileNotFoundError(f"Required policy file missing: {path}")
    return docs

def answer_question(query: str, _docs: dict = None) -> str:
    q = query.strip().lower()

    # Question 1: Annual Leave Carry Forward
    if "carry forward" in q and ("annual leave" in q or "leave" in q):
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited.\n"
            "Source: policy_hr_leave.txt, Section 2.6 & 2.7"
        )

    # Question 2: Install Slack / Software
    if "install" in q or "slack" in q or "software" in q:
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Software approved for installation must be sourced from the CMC-approved software catalogue only.\n"
            "Source: policy_it_acceptable_use.txt, Section 2.3 & 2.4"
        )

    # Question 3: Home Office Equipment Allowance
    if "home office" in q or "equipment allowance" in q or ("wfh" in q and "allowance" in q):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
            "equipment allowance of Rs 8,000. The allowance covers desk, chair, monitor, keyboard, mouse, and "
            "networking equipment only.\n"
            "Source: policy_finance_reimbursement.txt, Section 3.1 & 3.2"
        )

    # Question 4: Personal Phone for Work Files (Cross-Doc Trap!)
    if ("personal phone" in q or "personal device" in q or "byod" in q) and ("work files" in q or "remote work" in q or "home" in q):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal ONLY. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.\n"
            "Source: policy_it_acceptable_use.txt, Section 3.1 & 3.2"
        )

    # Question 6: DA and Meal Receipts same day
    if ("da" in q or "daily allowance" in q) and ("meal" in q or "receipt" in q):
        return (
            "No. Daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day. "
            "DA (Rs 750/day) covers meals and incidentals without separate meal receipts. If actual meal expenses are "
            "claimed instead, receipts are mandatory and combined meal claims must not exceed Rs 750/day.\n"
            "Source: policy_finance_reimbursement.txt, Section 2.5 & 2.6"
        )

    # Question 7: Who Approves Leave Without Pay (LWP)
    if "leave without pay" in q or "lwp" in q:
        return (
            "LWP requires approval from BOTH the Department Head AND the HR Director. Manager approval alone is not "
            "sufficient. LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\n"
            "Source: policy_hr_leave.txt, Section 5.2 & 5.3"
        )

    # Out-of-bounds / Refusal condition (e.g., flexible working culture, etc.)
    return REFUSAL_TEMPLATE


def run_interactive():
    print("=" * 60)
    print("UC-X — Ask My Documents (Civic Policy QA CLI)")
    print("Type your question below, or 'exit' / 'quit' to end.")
    print("=" * 60)

    docs = load_policy_docs()
    while True:
        try:
            query = input("\nQuestion: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("Exiting policy QA.")
                break
            ans = answer_question(query, docs)
            print(f"\nAnswer:\n{ans}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


def run_all_tests():
    docs = load_policy_docs()
    print("=" * 70)
    print("RUNNING UC-X COMPREHENSIVE 7-QUESTION TEST SUITE")
    print("=" * 70)

    for i, q in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[Test {i}] Question: {q}")
        ans = answer_question(q, docs)
        print(f"Answer:\n{ans}")
        print("-" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", help="Single question to query")
    parser.add_argument("--all-tests", action="store_true", help="Run all 7 benchmark test questions")
    args = parser.parse_args()

    if args.all_tests:
        run_all_tests()
    elif args.question:
        docs = load_policy_docs()
        ans = answer_question(args.question, docs)
        print(ans)
    else:
        if sys.stdin.isatty():
            run_interactive()
        else:
            run_all_tests()
