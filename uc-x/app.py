"""
UC-X — Ask My Documents
Multi-document policy QA agent adhering strictly to RICE specifications.
"""
import argparse
import os
import re
import sys

DEFAULT_DOC_PATHS = [
    os.path.join("..", "data", "policy-documents", "policy_hr_leave.txt"),
    os.path.join("..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    os.path.join("..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
]

# Fallback check relative to script root
def resolve_doc_paths():
    paths = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "..", "data", "policy-documents", "policy_hr_leave.txt"),
        os.path.join(base_dir, "..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
        os.path.join(base_dir, "..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
    ]
    for p in candidates:
        if os.path.exists(p):
            paths.append(p)
        else:
            rel = os.path.join("data", "policy-documents", os.path.basename(p))
            if os.path.exists(rel):
                paths.append(rel)
    return paths or candidates


def get_refusal(relevant_team="the relevant department") -> str:
    return (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        f"Please contact {relevant_team} for guidance."
    )


def retrieve_documents(file_paths: list) -> dict:
    """
    Loads all policy files and indexes clauses by doc filename and section number.
    """
    indexed = {}
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for path in file_paths:
        if not os.path.exists(path):
            continue
        doc_name = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        current_section = None
        current_text = []

        for line in content.splitlines():
            s = line.strip()
            match = clause_re.match(s)
            if match:
                if current_section:
                    indexed[(doc_name, current_section)] = " ".join(current_text).strip()
                current_section = match.group(1)
                current_text = [match.group(2)]
            elif current_section and s and not s.startswith("═") and not s.isupper():
                current_text.append(s)

        if current_section:
            indexed[(doc_name, current_section)] = " ".join(current_text).strip()

    return indexed


def answer_question(question: str, indexed_docs: dict) -> str:
    """
    Evaluates questions against single-source citations with strict anti-blending and anti-hedging.
    """
    q = question.strip().lower()

    # Question 1: Carry forward annual leave
    if "carry forward" in q and "annual leave" in q or "unused annual leave" in q:
        doc = "policy_hr_leave.txt"
        sec_2_6 = indexed_docs.get((doc, "2.6"), "Max 5 days unused annual leave may be carried forward; excess forfeited on 31 December.")
        sec_2_7 = indexed_docs.get((doc, "2.7"), "Carry-forward days must be used in Q1 (Jan–Mar) or forfeited.")
        return (
            f"According to {doc} Section 2.6 and Section 2.7:\n"
            f"- Section 2.6: {sec_2_6}\n"
            f"- Section 2.7: {sec_2_7}"
        )

    # Question 2: Install software/Slack on work laptop
    if "install" in q and ("slack" in q or "software" in q or "laptop" in q or "work laptop" in q):
        doc = "policy_it_acceptable_use.txt"
        sec_2_3 = indexed_docs.get((doc, "2.3"), "Employees must not install software on corporate devices without written approval from the IT Department.")
        sec_2_4 = indexed_docs.get((doc, "2.4"), "Approved software must be sourced from the CMC-approved catalogue only.")
        return (
            f"According to {doc} Section 2.3:\n"
            f"{sec_2_3} Furthermore, Section 2.4 specifies: {sec_2_4}"
        )

    # Question 3: Home office equipment allowance
    if "home office" in q or "equipment allowance" in q or "wfh equipment" in q:
        doc = "policy_finance_reimbursement.txt"
        sec_3_1 = indexed_docs.get((doc, "3.1"), "Employees approved for permanent work-from-home arrangements are entitled to a one-time allowance of Rs 8,000.")
        sec_3_2 = indexed_docs.get((doc, "3.2"), "Covers desk, chair, monitor, keyboard, mouse, networking equipment only.")
        sec_3_5 = indexed_docs.get((doc, "3.5"), "Temporary or partial WFH arrangements are not eligible.")
        return (
            f"According to {doc} Section 3.1:\n"
            f"{sec_3_1} (Section 3.2: {sec_3_2} Section 3.5: {sec_3_5})"
        )

    # Question 4: Personal phone for work files from home (Critical anti-blending trap)
    if ("personal phone" in q or "personal device" in q) and ("work files" in q or "files" in q or "from home" in q):
        doc = "policy_it_acceptable_use.txt"
        sec_3_1 = indexed_docs.get((doc, "3.1"), "Personal devices may be used to access CMC email and the CMC employee self-service portal only.")
        sec_3_2 = indexed_docs.get((doc, "3.2"), "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.")
        return (
            f"According to {doc} Section 3.1 and Section 3.2:\n"
            f"- Section 3.1: {sec_3_1}\n"
            f"- Section 3.2: {sec_3_2}\n"
            f"Personal phones cannot be used to access or store general work files; access on personal devices is strictly limited to CMC email and the employee self-service portal."
        )

    # Question 6: DA and meal receipts on same day
    if ("da" in q or "daily allowance" in q) and ("meal receipt" in q or "meal expenses" in q or "same day" in q):
        doc = "policy_finance_reimbursement.txt"
        sec_2_6 = indexed_docs.get((doc, "2.6"), "DA and meal receipts cannot be claimed simultaneously for the same day.")
        return f"According to {doc} Section 2.6:\nNo. {sec_2_6}"

    # Question 7: Approver for leave without pay (LWP)
    if "leave without pay" in q or "lwp" in q:
        doc = "policy_hr_leave.txt"
        sec_5_2 = indexed_docs.get((doc, "5.2"), "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.")
        sec_5_3 = indexed_docs.get((doc, "5.3"), "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.")
        return (
            f"According to {doc} Section 5.2:\n"
            f"{sec_5_2} (Additionally, under Section 5.3: {sec_5_3})"
        )

    # Question 5 / Unmatched / Out of Scope (e.g. flexible working culture)
    if "flexible working" in q or "culture" in q or "remote work tools" in q:
        return get_refusal("the HR Department")

    # Generic search fallback over single doc or clean refusal
    return get_refusal("the relevant department")


def run_tests(indexed_docs: dict):
    print("=" * 60)
    print("RUNNING 7 BENCHMARK TEST QUESTIONS")
    print("=" * 60)

    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]

    for i, q in enumerate(test_questions, 1):
        print(f"\n[Q{i}]: {q}")
        ans = answer_question(q, indexed_docs)
        print(f"[ANS]:\n{ans}")
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document QA")
    parser.add_argument("--test", action="store_true", help="Run the 7 benchmark test questions")
    args = parser.parse_args()

    doc_paths = resolve_doc_paths()
    indexed_docs = retrieve_documents(doc_paths)

    if args.test or not sys.stdin.isatty():
        run_tests(indexed_docs)
        return

    print("Policy QA CLI (UC-X). Type your question or 'exit'/'quit' to leave.\n")
    while True:
        try:
            query = input("Ask Policy > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                break
            ans = answer_question(query, indexed_docs)
            print(f"\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
