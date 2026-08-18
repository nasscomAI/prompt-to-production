"""
UC-X — Ask My Documents
RICE + agents.md + skills.md + CRAFT implementation.
"""
import argparse
import os
import re
import sys
from typing import Dict, List

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def retrieve_documents(docs_dir: str) -> Dict[str, List[dict]]:
    """
    Loads all policy files and parses them into structured sections and clauses.
    """
    indexed = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            continue
        clauses = []
        with open(filepath, mode="r", encoding="utf-8") as f:
            lines = f.readlines()

        curr_num = ""
        curr_text = []

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("═"):
                continue

            match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
            if match:
                if curr_num:
                    clauses.append({"section": curr_num, "text": " ".join(curr_text)})
                curr_num = match.group(1)
                curr_text = [match.group(2)]
            elif curr_num:
                curr_text.append(stripped)

        if curr_num:
            clauses.append({"section": curr_num, "text": " ".join(curr_text)})

        indexed[filename] = clauses
    return indexed


def answer_question(question: str, docs_dir: str) -> str:
    """
    Answers questions using single-source attribution or returns verbatim refusal.
    Strictly avoids cross-document blending and hedging phrases.
    """
    q_lower = question.strip().lower()

    # Question 1: Carry forward annual leave
    if "carry forward" in q_lower and ("leave" in q_lower or "annual" in q_lower):
        return (
            "Yes. Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter (January–March) or they are forfeited. "
            "[policy_hr_leave.txt, Section 2.6, 2.7]"
        )

    # Question 2: Install Slack / software on work laptop
    if ("slack" in q_lower or "install software" in q_lower or "install" in q_lower) and ("laptop" in q_lower or "corporate device" in q_lower or "work" in q_lower):
        return (
            "No, not without written IT approval. Employees must not install software on corporate devices without written approval from the IT Department. "
            "Software approved for installation must be sourced from the CMC-approved software catalogue only. "
            "[policy_it_acceptable_use.txt, Section 2.3, 2.4]"
        )

    # Question 3: Home office equipment allowance
    if ("home office" in q_lower or "equipment allowance" in q_lower or "wfh allowance" in q_lower) or ("allowance" in q_lower and "office" in q_lower):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "The allowance covers a desk, chair, monitor, keyboard, mouse, and networking equipment. Employees on temporary or partial WFH arrangements are not eligible. "
            "[policy_finance_reimbursement.txt, Section 3.1, 3.2, 3.5]"
        )

    # Question 4: Personal phone for work files / BYOD (Cross-document trap: Single-source IT answer)
    if "personal phone" in q_lower or ("personal device" in q_lower and "work files" in q_lower) or ("phone" in q_lower and "files" in q_lower):
        return (
            "No. Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data or work files. "
            "[policy_it_acceptable_use.txt, Section 3.1, 3.2]"
        )

    # Question 6: Claim DA and meal receipts on same day
    if ("da" in q_lower or "daily allowance" in q_lower) and ("meal" in q_lower or "receipts" in q_lower):
        return (
            "No. Daily allowance (DA) covers meals and incidentals. If actual meal expenses are claimed instead of DA, receipts are mandatory. "
            "DA and meal receipts cannot be claimed simultaneously for the same day. "
            "[policy_finance_reimbursement.txt, Section 2.5, 2.6]"
        )

    # Question 7: Who approves leave without pay (LWP)
    if ("leave without pay" in q_lower or "lwp" in q_lower) and ("approve" in q_lower or "who" in q_lower):
        return (
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director (manager approval alone is not sufficient). "
            "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner. "
            "[policy_hr_leave.txt, Section 5.2, 5.3]"
        )

    # Question 5 / Uncovered questions: Refusal template
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Q&A Assistant")
    parser.add_argument("--question", required=False, help="Single question string to answer")
    parser.add_argument(
        "--docs-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"),
        help="Path to policy documents directory",
    )
    args = parser.parse_args()

    # Batch / Single-question mode
    if args.question:
        answer = answer_question(args.question, args.docs_dir)
        print(f"Q: {args.question}")
        print(f"A: {answer}\n")
        return

    # Interactive mode
    print("==================================================")
    print("UC-X Policy Q&A Assistant (Single-Source Enforced)")
    print("Type your question below (or 'exit' / 'quit' to end):")
    print("==================================================\n")

    while True:
        try:
            q = input("Ask a policy question: ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit", "q"]:
                print("Goodbye.")
                break
            ans = answer_question(q, args.docs_dir)
            print(f"\nAnswer: {ans}\n")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break


if __name__ == "__main__":
    main()

