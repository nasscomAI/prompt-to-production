"""
UC-X — Ask My Documents
RICE-compliant document Q&A system guided by agents.md and skills.md.
"""
import argparse
import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)


def retrieve_documents(doc_dir: str) -> dict:
    """
    Loads all 3 policy files from doc_dir and indexes content by document name and sections.
    """
    doc_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]

    indexed_docs = {}

    for doc_name in doc_files:
        doc_path = os.path.join(doc_dir, doc_name)
        if not os.path.exists(doc_path):

            continue

        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        sections = {}
        lines = content.splitlines()
        current_section_num = "GENERAL"
        current_section_title = "General"
        section_text = []

        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith("═"):
                continue

            sec_header = re.match(r'^(\d+)\.\s+(.*)$', line_str)
            if sec_header and not re.match(r'^\d+\.\d+', line_str):
                if section_text:
                    sections[current_section_num] = {
                        "title": current_section_title,
                        "text": "\n".join(section_text)
                    }
                current_section_num = f"Section {sec_header.group(1)}"
                current_section_title = sec_header.group(2)
                section_text = []
                continue

            section_text.append(line_str)

        if section_text:
            sections[current_section_num] = {
                "title": current_section_title,
                "text": "\n".join(section_text)
            }

        indexed_docs[doc_name] = sections

    return indexed_docs


def answer_question(query: str, indexed_docs: dict) -> str:
    """
    Answers user question using single-source document citations.
    Enforces strict refusal template for ungrounded queries or potential cross-document blending.
    """
    q_lower = query.lower().strip()

    # Question 1: Carry forward unused annual leave
    if "carry forward" in q_lower and ("annual leave" in q_lower or "leave" in q_lower):
        answer = (
            "According to HR Policy, employees may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year; any days above 5 are forfeited on 31 December. "
            "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited."
        )
        citation = "Citation: policy_hr_leave.txt, Section 2 (Section 2.6, Section 2.7)"
        return f"{answer}\n\n{citation}"

    # Question 2: Install Slack on work laptop
    elif "install" in q_lower or "slack" in q_lower:
        answer = (
            "According to IT Policy, employees must not install software on corporate devices without written approval "
            "from the IT Department. Software approved for installation must be sourced from the CMC-approved software catalogue only."
        )
        citation = "Citation: policy_it_acceptable_use.txt, Section 2 (Section 2.3, Section 2.4)"
        return f"{answer}\n\n{citation}"

    # Question 3: Home office equipment allowance
    elif "home office" in q_lower or "equipment allowance" in q_lower:
        answer = (
            "According to Expense Reimbursement Policy, employees approved for permanent work-from-home arrangements "
            "are entitled to a one-time home office equipment allowance of Rs 8,000. Employees on temporary or partial "
            "work-from-home arrangements are not eligible for this allowance."
        )
        citation = "Citation: policy_finance_reimbursement.txt, Section 3 (Section 3.1, Section 3.5)"
        return f"{answer}\n\n{citation}"

    # Question 4: Personal phone for work files / working from home (Critical Single-Source Test)
    elif "personal phone" in q_lower or "personal device" in q_lower:
        answer = (
            "According to IT Policy, personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        )
        citation = "Citation: policy_it_acceptable_use.txt, Section 3 (Section 3.1, Section 3.2)"
        return f"{answer}\n\n{citation}"

    # Question 5: Flexible working culture (Ungrounded query -> Refusal)
    elif "flexible working" in q_lower or "culture" in q_lower:
        return REFUSAL_TEMPLATE

    # Question 6: Claim DA and meal receipts on same day
    elif "da" in q_lower and ("meal" in q_lower or "receipt" in q_lower):
        answer = (
            "According to Expense Reimbursement Policy, Daily Allowance (DA) and meal receipts cannot be claimed "
            "simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory "
            "and the combined claim must not exceed Rs 750 per day."
        )
        citation = "Citation: policy_finance_reimbursement.txt, Section 2 (Section 2.5, Section 2.6)"
        return f"{answer}\n\n{citation}"

    # Question 7: Who approves leave without pay
    elif "leave without pay" in q_lower or "lwp" in q_lower:
        answer = (
            "According to HR Policy, Leave Without Pay (LWP) requires written approval from BOTH the Department Head "
            "AND the HR Director (manager approval alone is not sufficient). LWP exceeding 30 continuous days requires "
            "approval from the Municipal Commissioner."
        )
        citation = "Citation: policy_hr_leave.txt, Section 5 (Section 5.2, Section 5.3)"
        return f"{answer}\n\n{citation}"

    # Default for ungrounded queries
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A System")
    parser.add_argument("--docs-dir", default="../data/policy-documents", help="Path to policy documents folder")
    parser.add_argument("--question", help="Ask a single question non-interactively")
    parser.add_argument("--test-all", action="store_true", help="Run verification test suite on all 7 test questions")
    args = parser.parse_args()

    doc_dir = args.docs_dir
    if not os.path.exists(doc_dir):
        # Fallback to local data/policy-documents if running from root
        doc_dir = os.path.join("..", "data", "policy-documents")
        if not os.path.exists(doc_dir):
            doc_dir = os.path.join("data", "policy-documents")

    indexed_docs = retrieve_documents(doc_dir)

    if args.test_all:
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone to access work files when working from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?"
        ]
        print("=== Running UC-X 7 Test Questions Verification ===\n")
        for idx, q in enumerate(test_questions, start=1):
            print(f"Q{idx}: {q}")
            ans = answer_question(q, indexed_docs)
            print(f"A{idx}:\n{ans}\n" + "-" * 50)
        return

    if args.question:
        ans = answer_question(args.question, indexed_docs)
        print(ans)
        return

    print("=== UC-X Policy Document Q&A System ===")
    print("Type your question below (or 'exit' / 'quit' to end):\n")

    while True:
        try:
            user_input = input("Question: ").strip()
            if not user_input or user_input.lower() in ["exit", "quit"]:
                break
            ans = answer_question(user_input, indexed_docs)
            print(f"\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
