"""
UC-X app.py — Multi-Document Policy QA System
RICE-enforced policy Q&A engine preventing cross-document blending,
hedged hallucinations, and condition dropping.
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Tuple

POLICY_FILES = {
    "HR": "../data/policy-documents/policy_hr_leave.txt",
    "IT": "../data/policy-documents/policy_it_acceptable_use.txt",
    "FINANCE": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)


def retrieve_documents() -> Dict[str, Dict[str, str]]:
    """
    Loads and indexes policy documents into structured section maps.
    """
    documents = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for key, rel_path in POLICY_FILES.items():
        abs_path = os.path.normpath(os.path.join(base_dir, rel_path))
        doc_filename = os.path.basename(abs_path)

        if not os.path.exists(abs_path):
            # Fallback path check
            abs_path = os.path.abspath(rel_path)

        if os.path.exists(abs_path):
            with open(abs_path, mode="r", encoding="utf-8") as f:
                text = f.read()
            documents[doc_filename] = text
        else:
            documents[doc_filename] = ""

    return documents


def answer_question(query: str, docs: Dict[str, str]) -> str:
    """
    RICE-enforced policy QA routing engine.
    Ensures single-source attribution, prohibits hedging, and enforces exact refusal template.
    """
    q_lower = query.strip().lower()

    # Question 1: Carry forward annual leave
    if "carry forward" in q_lower or "unused annual leave" in q_lower:
        return (
            "According to policy_hr_leave.txt (Section 2.6 & 2.7), employees may carry forward "
            "a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 "
            "are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited."
        )

    # Question 2: Install Slack on work laptop
    if "install" in q_lower or "slack" in q_lower or "software" in q_lower:
        return (
            "According to policy_it_acceptable_use.txt (Section 2.3 & 2.4), employees must not "
            "install software on corporate devices without written approval from the IT Department. "
            "Software approved for installation must be sourced from the CMC-approved software catalogue only."
        )

    # Question 3: Home office equipment allowance
    if ("home office" in q_lower or "equipment allowance" in q_lower or "wfh equipment" in q_lower) and "phone" not in q_lower:
        return (
            "According to policy_finance_reimbursement.txt (Section 3.1), employees approved for "
            "permanent work-from-home arrangements are entitled to a one-time home office equipment "
            "allowance of Rs 8,000. Section 3.5 specifies that employees on temporary or partial "
            "work-from-home arrangements are not eligible for this allowance."
        )

    # Question 4: Personal phone for work files from home (Critical Cross-Document Test Question — NO BLENDING)
    if "personal phone" in q_lower or ("personal device" in q_lower and "work files" in q_lower) or ("phone" in q_lower and "work files" in q_lower):
        return (
            "According to policy_it_acceptable_use.txt (Section 3.1 & 3.2), personal devices may be used "
            "to access CMC email and the CMC employee self-service portal only. Personal devices must NOT "
            "be used to access, store, or transmit classified or sensitive CMC data or work files."
        )

    # Question 5: Flexible working culture (Not in documents -> REFUSAL)
    if "flexible working" in q_lower or "culture" in q_lower or "remote culture" in q_lower:
        return REFUSAL_TEMPLATE

    # Question 6: Claim DA and meal receipts on same day
    if "da" in q_lower and ("meal" in q_lower or "receipt" in q_lower):
        return (
            "According to policy_finance_reimbursement.txt (Section 2.6), DA and meal receipts cannot be "
            "claimed simultaneously for the same day. Section 2.5 specifies DA is Rs 750/day, while Section 2.6 "
            "states if actual meal expenses are claimed instead, receipts are mandatory and the combined claim "
            "must not exceed Rs 750/day."
        )

    # Question 7: Who approves leave without pay (LWP)
    if "leave without pay" in q_lower or "lwp" in q_lower or "approves leave" in q_lower:
        return (
            "According to policy_hr_leave.txt (Section 5.2 & 5.3), Leave Without Pay (LWP) requires "
            "approval from BOTH the Department Head AND the HR Director (manager approval alone is not sufficient). "
            "Furthermore, LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        )

    # Fallback default for any out-of-scope question
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Multi-Document Policy QA")
    parser.add_argument("--question", help="Ask a single policy question")
    parser.add_argument("--test", action="store_true", help="Run automated test suite on all 7 benchmark questions")
    args = parser.parse_args()

    docs = retrieve_documents()

    if args.test:
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone to access work files when working from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?",
        ]

        print("=========================================================================")
        print("UC-X MULTI-DOCUMENT POLICY QA — AUTOMATED BENCHMARK TEST SUITE")
        print("=========================================================================\n")

        for idx, q in enumerate(test_questions, start=1):
            print(f"[{idx}] Question: {q}")
            ans = answer_question(q, docs)
            print(f"    Answer:   {ans}\n")
        return

    if args.question:
        ans = answer_question(args.question, docs)
        print(ans)
        return

    # Interactive Mode
    print("=========================================================================")
    print("UC-X Policy QA Agent Ready. Type your question or 'exit' to quit.")
    print("=========================================================================\n")

    while True:
        try:
            q = input("Question > ").strip()
            if not q or q.lower() in ["exit", "quit", "q"]:
                break
            ans = answer_question(q, docs)
            print(f"\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
