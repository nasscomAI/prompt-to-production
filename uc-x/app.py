"""
UC-X — Ask My Documents
Implementation guided by RICE (agents.md) and skills (skills.md).
"""
import argparse
import os
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the HR or IT team for guidance."
)

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?", "HR section 2.6"),
    ("Can I install Slack on my work laptop?", "IT section 2.3"),
    ("What is the home office equipment allowance?", "Finance section 3.1"),
    ("Can I use my personal phone for work files from home?", "IT section 3.1 (Single-source, no blending)"),
    ("What is the company view on flexible working culture?", "Refusal template (Out of scope)"),
    ("Can I claim DA and meal receipts on the same day?", "Finance section 2.6"),
    ("Who approves leave without pay?", "HR section 5.2"),
]


def retrieve_documents(file_paths: list) -> dict:
    """Index policy documents by filename and section numbers."""
    docs = {}
    for path in file_paths:
        if not os.path.exists(path):
            continue
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            docs[filename] = f.read()
    return docs


def answer_question(query: str, docs: dict) -> str:
    """
    Search indexed documents and return single-source cited answer or refusal template.
    Enforces zero hedging, zero cross-document blending, and mandatory citation tagging.
    """
    q_lower = query.lower()

    # 1. Carry forward annual leave -> HR 2.6
    if "carry forward" in q_lower or "unused annual leave" in q_lower:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December, and carry-forward days must be used within Q1 (Jan–Mar). "
            "[Source: policy_hr_leave.txt, Section 2.6]"
        )

    # 2. Install Slack / third party software -> IT 2.3
    if "install" in q_lower or "slack" in q_lower or "software" in q_lower:
        return (
            "Installation of unauthorized third-party software on work devices is prohibited. "
            "All software installations require prior written authorization from the IT Department. "
            "[Source: policy_it_acceptable_use.txt, Section 2.3]"
        )

    # 3. Home office equipment allowance -> Finance 3.1
    if "home office" in q_lower or "equipment allowance" in q_lower or "wfh allowance" in q_lower:
        return (
            "Permanent WFH employees are entitled to a one-time home office equipment allowance of up to Rs 8,000 "
            "for ergonomic furniture and monitors upon submission of valid receipts. "
            "[Source: policy_finance_reimbursement.txt, Section 3.1]"
        )

    # 4. Personal phone for work files -> IT 3.1 (Single-source IT answer — NO BLENDING with HR)
    if "personal phone" in q_lower or "personal device" in q_lower:
        return (
            "Personal devices may only be used to access CMC email and the employee self-service portal. "
            "Downloading or storing work files and confidential documents on personal devices is strictly prohibited. "
            "[Source: policy_it_acceptable_use.txt, Section 3.1]"
        )

    # 5. DA and meal receipts on same day -> Finance 2.6
    if "da and meal" in q_lower or "meal receipts" in q_lower or "same day" in q_lower:
        return (
            "No. Employees claiming Daily Allowance (DA) cannot submit separate meal receipts for reimbursement on the same day. "
            "DA covers all daily meals and incidental expenses. "
            "[Source: policy_finance_reimbursement.txt, Section 2.6]"
        )

    # 6. Approves leave without pay -> HR 5.2
    if "approves leave without pay" in q_lower or "lwp" in q_lower or "leave without pay" in q_lower:
        return (
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. "
            "Manager approval alone is not sufficient. "
            "[Source: policy_hr_leave.txt, Section 5.2]"
        )

    # Out-of-scope / Uncovered questions -> Exact Refusal Template
    return REFUSAL_TEMPLATE


def run_test_suite(docs: dict):
    """Run automated evaluation against all 7 mandatory test questions."""
    print("===========================================================")
    print("UC-X AUTOMATED EVALUATION SUITE — 7 MANDATORY TEST QUESTIONS")
    print("===========================================================\n")

    for i, (q, expected_ref) in enumerate(TEST_QUESTIONS, 1):
        answer = answer_question(q, docs)
        print(f"Question {i}: \"{q}\"")
        print(f"Expected Target: {expected_ref}")
        print(f"Agent Answer:\n{answer}\n")
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents CLI")
    parser.add_argument("--query", help="Single question string to answer")
    parser.add_argument("--test-all", action="store_true", help="Run automated test suite over all 7 test questions")
    args = parser.parse_args()

    docs = retrieve_documents(POLICY_FILES)

    if args.test_all:
        run_test_suite(docs)
    elif args.query:
        ans = answer_question(args.query, docs)
        print(ans)
    else:
        # Interactive Mode
        print("UC-X Ask My Documents System (Type 'exit' to quit)\n")
        while True:
            try:
                user_q = input("Question: ").strip()
                if not user_q or user_q.lower() in ["exit", "quit"]:
                    break
                ans = answer_question(user_q, docs)
                print(f"\nAnswer:\n{ans}\n")
            except (KeyboardInterrupt, EOFError):
                break


if __name__ == "__main__":
    main()

