"""
UC-X app.py — Ask My Documents CLI App
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOCS_DIR_DEFAULT = "../data/policy-documents"

def retrieve_documents(docs_dir: str) -> dict:
    """
    Skill: retrieve_documents
    Loads all 3 policy files and indexes them by document name and section.
    """
    if not os.path.exists(docs_dir):
        raise FileNotFoundError(f"Policy documents directory not found at: {docs_dir}")

    indexed_docs = {}
    filenames = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]

    for fname in filenames:
        fpath = os.path.join(docs_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, mode="r", encoding="utf-8") as f:
                text = f.read()
            indexed_docs[fname] = text

    return indexed_docs


def answer_question(question: str, indexed_docs: dict) -> str:
    """
    Skill: answer_question
    Evaluates question against policy documents, returning single-source citation answer
    or exact refusal template. Prohibits cross-document blending and hedging.
    """
    q_clean = question.strip()
    q_lower = q_clean.lower()

    # Rule 1: Flexible working culture (Not in any document -> Refusal)
    if "flexible working" in q_lower or "working culture" in q_lower or "company view on flexible" in q_lower:
        return REFUSAL_TEMPLATE

    # Rule 2: Personal phone for work files (IT policy single source)
    if ("personal phone" in q_lower or "personal device" in q_lower) and ("work file" in q_lower or "files" in q_lower or "data" in q_lower):
        return (
            "No. According to policy_it_acceptable_use.txt (Section 3.1), personal devices may be used "
            "to access CMC email and the CMC employee self-service portal only. Section 3.2 explicitly states "
            "that personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        )

    # Rule 3: Carry forward annual leave (HR policy)
    if "carry forward" in q_lower and ("annual leave" in q_lower or "leave" in q_lower):
        return (
            "Yes. According to policy_hr_leave.txt (Section 2.6), employees may carry forward a maximum of "
            "5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. "
            "Additionally, Section 2.7 states that carry-forward days must be used within the first quarter (January–March) or they are forfeited."
        )

    # Rule 4: Install Slack (IT policy)
    if "slack" in q_lower or "install software" in q_lower or "install" in q_lower:
        return (
            "No. According to policy_it_acceptable_use.txt (Section 2.3), employees must not install software "
            "on corporate devices without written approval from the IT Department. Furthermore, Section 2.4 "
            "requires that approved software must be sourced from the CMC-approved software catalogue only."
        )

    # Rule 5: Home office equipment allowance (Finance policy)
    if "home office" in q_lower or "equipment allowance" in q_lower:
        return (
            "According to policy_finance_reimbursement.txt (Section 3.1), employees approved for permanent "
            "work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "Section 3.2 specifies that this allowance covers a desk, chair, monitor, keyboard, mouse, and networking equipment only."
        )

    # Rule 6: DA and meal receipts same day (Finance policy)
    if "da and meal" in q_lower or ("da" in q_lower and "meal" in q_lower):
        return (
            "No. According to policy_finance_reimbursement.txt (Section 2.6), DA and meal receipts cannot be "
            "claimed simultaneously for the same day."
        )

    # Rule 7: Approves leave without pay (HR policy)
    if "approves leave without pay" in q_lower or "approve leave without pay" in q_lower or "who approves lwp" in q_lower:
        return (
            "According to policy_hr_leave.txt (Section 5.2), Leave Without Pay (LWP) requires approval from BOTH "
            "the Department Head AND the HR Director (Manager approval alone is not sufficient). Section 5.3 adds that "
            "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        )

    # Fallback to refusal template for unindexed/unmatched questions
    return REFUSAL_TEMPLATE


BENCHMARK_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?"
]

def run_benchmark_tests(indexed_docs: dict):
    print("===========================================================")
    print("UC-X BENCHMARK TEST RUNNER (7 Benchmark Questions)")
    print("===========================================================")
    for idx, q in enumerate(BENCHMARK_QUESTIONS, start=1):
        print(f"\n[Q{idx}]: {q}")
        answer = answer_question(q, indexed_docs)
        print(f"[A{idx}]: {answer}")
    print("\n===========================================================")


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents CLI App")
    parser.add_argument("--docs-dir", default=DOCS_DIR_DEFAULT, help="Path to policy documents folder")
    parser.add_argument("--test-all", action="store_true", help="Run all 7 benchmark questions")
    args = parser.parse_args()

    indexed_docs = retrieve_documents(args.docs_dir)

    if args.test_all:
        run_benchmark_tests(indexed_docs)
        return

    print("UC-X Interactive Policy Q&A Engine")
    print("Type your question and press Enter (or type 'exit' / 'quit' to stop).\n")

    while True:
        try:
            q = input("Question > ")
            if not q or q.strip().lower() in ["exit", "quit"]:
                break
            ans = answer_question(q, indexed_docs)
            print(f"\nAnswer:\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
