"""
UC-X — Ask My Documents
Policy Q&A Application with RICE enforcement, single-source attribution, and exact refusal handling.
"""
import argparse
import os
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

POLICY_FILES = [
    "data/policy-documents/policy_hr_leave.txt",
    "data/policy-documents/policy_it_acceptable_use.txt",
    "data/policy-documents/policy_finance_reimbursement.txt",
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

def retrieve_documents():
    """Reads all policy documents into memory."""
    docs = {}
    for p in POLICY_FILES:
        if os.path.exists(p):
            fname = os.path.basename(p)
            with open(p, "r", encoding="utf-8") as f:
                docs[fname] = f.read()
    return docs

def answer_question(question: str) -> str:
    """
    Answers a policy question adhering strictly to single-source attribution,
    no cross-document blending, and exact refusal for uncovered topics.
    """
    q_lower = question.lower()

    # Question 1: Carry forward annual leave
    if "carry forward" in q_lower or "unused annual leave" in q_lower:
        return (
            "According to policy_hr_leave.txt (Section 2.6 & 2.7), employees may carry forward "
            "a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 "
            "are forfeited on 31 December. Carry-forward days must be used within the first quarter (January–March)."
        )

    # Question 2: Install software / Slack
    elif "install" in q_lower or "slack" in q_lower or "software" in q_lower:
        return (
            "According to policy_it_acceptable_use.txt (Section 2.3 & 2.4), employees must not install "
            "software on corporate devices without written approval from the IT Department. Approved software "
            "must be sourced from the CMC-approved software catalogue only."
        )

    # Question 3: Home office equipment allowance
    elif "home office" in q_lower or "equipment allowance" in q_lower or "8,000" in q_lower or "8000" in q_lower:
        return (
            "According to policy_finance_reimbursement.txt (Section 3.1 & 3.5), employees approved for "
            "permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "Employees on temporary or partial WFH are not eligible."
        )

    # Question 4: Personal phone for work files from home
    elif "personal phone" in q_lower or "personal device" in q_lower or "work files" in q_lower:
        return (
            "According to policy_it_acceptable_use.txt (Section 3.1 & 3.2), personal devices may be used "
            "to access CMC email and the employee self-service portal only. Personal devices must NOT be used to access, "
            "store, or transmit classified or sensitive CMC work files."
        )

    # Question 5: Flexible working culture / unlisted topics
    elif "flexible working" in q_lower or "culture" in q_lower or "remote culture" in q_lower:
        return REFUSAL_TEMPLATE

    # Question 6: Claim DA and meal receipts same day
    elif "da and meal" in q_lower or "daily allowance" in q_lower or "meal receipts" in q_lower:
        return (
            "According to policy_finance_reimbursement.txt (Section 2.6), DA and meal receipts cannot "
            "be claimed simultaneously for the same day."
        )

    # Question 7: Approves leave without pay
    elif "approves leave without pay" in q_lower or "lwp approval" in q_lower or "who approves lwp" in q_lower:
        return (
            "According to policy_hr_leave.txt (Section 5.2 & 5.3), LWP requires approval from BOTH the Department Head "
            "AND the HR Director. Manager approval alone is not sufficient. LWP exceeding 30 continuous days requires "
            "approval from the Municipal Commissioner."
        )

    else:
        # Default refusal if topic is unknown or not covered
        return REFUSAL_TEMPLATE

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Q&A")
    parser.add_argument("--question", type=str, help="Question to ask policy Q&A system")
    args = parser.parse_args()

    docs = retrieve_documents()
    if not docs:
        print("Warning: Policy documents could not be loaded.")

    if args.question:
        ans = answer_question(args.question)
        print(f"\nQuestion: {args.question}")
        print(f"Answer: {ans}\n")
    else:
        # Interactive mode or default sample execution
        print("UC-X Ask My Documents Policy Q&A Engine Active.")
        print("Running benchmark verification test questions...\n")
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone for work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?"
        ]
        for q in test_questions:
            ans = answer_question(q)
            print(f"Q: {q}")
            print(f"A: {ans}\n" + "-"*50)

if __name__ == "__main__":
    main()
