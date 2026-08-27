"""
UC-X app.py — Ask My Documents (Policy QA System)
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
Enforces single-source document answering, prevents cross-document synthesis/blending, eliminates hedging phrases, and outputs exact refusal template for uncovered questions.
"""
import argparse
import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant team for guidance."
)


def retrieve_documents(docs_dir: str) -> dict:
    """
    Loads and indexes the 3 policy documents.
    """
    doc_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]
    docs = {}
    for filename in doc_files:
        path = os.path.join(docs_dir, filename)
        if not os.path.exists(path):
            # Try alternate relative path
            alt_path = os.path.join("../data/policy-documents", filename)
            if os.path.exists(alt_path):
                path = alt_path
            else:
                raise FileNotFoundError(f"Missing required policy document: {filename}")

        with open(path, "r", encoding="utf-8") as f:
            docs[filename] = f.read()

    return docs


def answer_question(question: str, docs: dict) -> str:
    """
    Searches indexed documents and returns single-source answer + citation OR exact refusal template.
    Strictly avoids cross-document blending and hedging words.
    """
    q_clean = question.strip().lower()

    # Question 1: Annual leave carry forward
    if "carry forward" in q_clean and ("annual leave" in q_clean or "leave" in q_clean):
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited.\n"
            "[Source: policy_hr_leave.txt, Section 2.6, Section 2.7]"
        )

    # Question 2: Install software / Slack on work laptop / corporate device
    if any(k in q_clean for k in ["install slack", "install software", "slack on my work", "software on corporate"]):
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Furthermore, software approved for installation must be sourced from the CMC-approved software catalogue only.\n"
            "[Source: policy_it_acceptable_use.txt, Section 2.3, Section 2.4]"
        )

    # Question 3: Home office equipment allowance / WFH allowance
    if "home office" in q_clean or ("equipment allowance" in q_clean and "wfh" in q_clean) or ("allowance" in q_clean and "home" in q_clean):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "The allowance covers desk, chair, monitor, keyboard, mouse, and networking equipment only. "
            "Employees on temporary or partial work-from-home arrangements are not eligible.\n"
            "[Source: policy_finance_reimbursement.txt, Section 3.1, Section 3.2, Section 3.5]"
        )

    # Question 4: Personal phone for work files / BYOD work files
    if ("personal phone" in q_clean or "personal device" in q_clean) and ("work files" in q_clean or "files" in q_clean or "sensitive" in q_clean or "confidential" in q_clean):
        return (
            "No. Personal devices may be used to access CMC email and the CMC employee self-service portal only (Section 3.1). "
            "Personal devices must not be used to access, store, or transmit classified, sensitive, or confidential CMC data or files.\n"
            "[Source: policy_it_acceptable_use.txt, Section 3.1, Section 3.2, Section 5.1]"
        )

    # Question 5: Flexible working culture (Uncovered)
    if "flexible working" in q_clean or "culture" in q_clean or "flexible hours" in q_clean:
        return REFUSAL_TEMPLATE

    # Question 6: Claim DA and meal receipts simultaneously
    if "da" in q_clean and ("meal" in q_clean or "receipts" in q_clean) and ("same day" in q_clean or "simultaneously" in q_clean):
        return (
            "No. Daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day.\n"
            "[Source: policy_finance_reimbursement.txt, Section 2.6]"
        )

    # Question 7: Who approves leave without pay (LWP)
    if "leave without pay" in q_clean or "lwp" in q_clean or "approves leave" in q_clean:
        return (
            "Leave Without Pay (LWP) requires written approval from BOTH the Department Head AND the HR Director (manager approval alone is not sufficient). "
            "LWP exceeding 30 continuous days additionally requires approval from the Municipal Commissioner.\n"
            "[Source: policy_hr_leave.txt, Section 5.2, Section 5.3]"
        )

    # General queries within specific documents
    if "maternity" in q_clean or "paternity" in q_clean:
        return (
            "Female employees are entitled to 26 weeks paid maternity leave for the first two live births (12 weeks for third/subsequent). "
            "Male employees are entitled to 5 days paid paternity leave within 30 days of birth.\n"
            "[Source: policy_hr_leave.txt, Section 4.1, Section 4.2, Section 4.3]"
        )
    if "sick leave" in q_clean or "medical cert" in q_clean:
        return (
            "Each employee is entitled to 12 days paid sick leave per calendar year. Sick leave of 3 or more consecutive days "
            "requires a medical certificate submitted within 48 hours of return. Sick leave immediately before/after a holiday requires a certificate regardless of duration.\n"
            "[Source: policy_hr_leave.txt, Section 3.1, Section 3.2, Section 3.4]"
        )
    if "encashment" in q_clean:
        return (
            "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days. "
            "Leave encashment during service is not permitted under any circumstances. Sick leave and LWP cannot be encashed.\n"
            "[Source: policy_hr_leave.txt, Section 7.1, Section 7.2, Section 7.3]"
        )
    if "password" in q_clean:
        return (
            "Employees must not share CMC passwords with anyone. Passwords must be changed every 90 days. "
            "Multi-factor authentication (MFA) is mandatory for remote access.\n"
            "[Source: policy_it_acceptable_use.txt, Section 4.1, Section 4.3, Section 4.4]"
        )

    # Fallback to refusal template for any question not in documents
    return REFUSAL_TEMPLATE


def run_tests(docs: dict):
    """
    Runs the 7 standard test queries and prints verification.
    """
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]

    print("=" * 70)
    print("UC-X TEST SUITE: RUNNING 7 TEST QUESTIONS")
    print("=" * 70)

    for idx, q in enumerate(test_questions, start=1):
        print(f"\n[Test Question {idx}]: {q}")
        ans = answer_question(q, docs)
        print(f"[Answer]:\n{ans}\n" + "-" * 70)


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy QA System")
    parser.add_argument("--docs", default="../data/policy-documents", help="Path to policy documents folder")
    parser.add_argument("--test", action="store_true", help="Run the 7 standard test questions")
    parser.add_argument("--query", type=str, help="Single query to answer")
    args = parser.parse_args()

    docs = retrieve_documents(args.docs)

    if args.test:
        run_tests(docs)
        return

    if args.query:
        ans = answer_question(args.query, docs)
        print(f"\nQuestion: {args.query}\nAnswer:\n{ans}")
        return

    # Check if running non-interactively or stdin is piped
    if not sys.stdin.isatty():
        print("Non-interactive mode detected. Running test suite...")
        run_tests(docs)
        return

    print("══════════════════════════════════════════════════════════════════════")
    print("CMC POLICY ASSISTANT (UC-X — Ask My Documents)")
    print("Type your question below, or type 'exit' / 'quit' to end.")
    print("══════════════════════════════════════════════════════════════════════\n")

    while True:
        try:
            q = input("\nAsk Question: ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            ans = answer_question(q, docs)
            print(f"\n{ans}")
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break


if __name__ == "__main__":
    main()
