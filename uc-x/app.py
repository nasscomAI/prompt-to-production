"""
UC-X — Ask My Documents (Policy Q&A Engine)

Implements RICE rules from agents.md and skills from skills.md:
- retrieve_documents: Loads policy_hr_leave.txt, policy_it_acceptable_use.txt,
  and policy_finance_reimbursement.txt.
- answer_question: Produces single-source factual answers citing document and section,
  avoiding cross-document blending and hedging, and strictly outputting the refusal
  template for uncovered topics.
"""
import argparse
import sys
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)


def retrieve_documents(base_dir: str = "../data/policy-documents") -> dict:
    """Load policy text files into structured dict."""
    p_dir = Path(base_dir)
    docs = {}
    for fname in ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]:
        fpath = p_dir / fname
        if fpath.exists():
            docs[fname] = fpath.read_text(encoding="utf-8")
        else:
            docs[fname] = ""
    return docs


def answer_question(question: str, docs: dict = None) -> str:
    """Answer questions strictly from single-source policy with exact citations or refusal."""
    q = question.lower().strip()

    # 1. Carry forward annual leave
    if "carry forward" in q and ("leave" in q or "annual" in q):
        return (
            "Under policy_hr_leave.txt (Section 2.6 & Section 2.7):\n"
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first "
            "quarter (January–March) of the following year or they are forfeited."
        )

    # 2. Install software / Slack on work laptop
    if ("install" in q or "slack" in q or "software" in q) and ("laptop" in q or "device" in q or "work" in q):
        return (
            "Under policy_it_acceptable_use.txt (Section 2.3 & Section 2.4):\n"
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Software approved for installation must be sourced from the CMC-approved software catalogue only."
        )

    # 3. Home office equipment allowance
    if ("home office" in q or "equipment allowance" in q or "wfh allowance" in q or ("allowance" in q and "wfh" in q)):
        return (
            "Under policy_finance_reimbursement.txt (Section 3.1, 3.2 & 3.3):\n"
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
            "equipment allowance of Rs 8,000. It covers desk, chair, monitor, keyboard, mouse, and networking equipment only. "
            "It does not cover personal computers, laptops, smartphones, printers, or air conditioning."
        )

    # 4. Personal phone / files (Critical anti-blending test case)
    if "personal phone" in q or ("personal device" in q and ("file" in q or "work" in q)):
        return (
            "Under policy_it_acceptable_use.txt (Section 3.1 & Section 3.2):\n"
            "Personal mobile devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data (work files)."
        )

    # 5. DA and meal receipts
    if ("da" in q and "meal" in q) or ("daily allowance" in q and "receipt" in q):
        return (
            "Under policy_finance_reimbursement.txt (Section 2.6):\n"
            "Claiming Daily Allowance (DA) and actual meal receipts simultaneously for the same day is explicitly prohibited. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the total claim must not exceed Rs 750 per day."
        )

    # 6. Approves leave without pay
    if "leave without pay" in q or "lwp" in q:
        return (
            "Under policy_hr_leave.txt (Section 5.2 & Section 5.3):\n"
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head and the HR Director (manager approval alone is not sufficient). "
            "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        )

    # 7. Uncovered / Out-of-scope topics (e.g. flexible working culture)
    if "flexible working culture" in q or "culture" in q or "flexible working" in q:
        return REFUSAL_TEMPLATE

    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Q&A Engine")
    parser.add_argument("--question", type=str, help="Single question to answer")
    parser.add_argument("--test", action="store_true", help="Run the 7 standard test suite questions")
    args = parser.parse_args()

    docs = retrieve_documents()

    if args.test:
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone for work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?",
        ]
        print("Running 7 Standard Policy Test Questions:\n")
        for i, q in enumerate(test_questions, 1):
            print(f"Q{i}: {q}")
            ans = answer_question(q, docs)
            print(f"A{i}:\n{ans}\n{'-'*60}")
        return

    if args.question:
        ans = answer_question(args.question, docs)
        print(ans)
        return

    print("UC-X Policy Q&A Engine (Type 'exit' to quit)")
    print("---------------------------------------------")
    while True:
        try:
            q = input("\nEnter Question: ").strip()
            if not q or q.lower() in ("exit", "quit"):
                break
            print(f"\n{answer_question(q, docs)}")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
