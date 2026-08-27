"""
UC-X — Ask My Documents
Interactive CLI that answers questions from 3 policy documents.
"""
import argparse
import logging
import os
import sys

DOCUMENT_PATHS = {
    "policy_hr_leave.txt": None,
    "policy_it_acceptable_use.txt": None,
    "policy_finance_reimbursement.txt": None,
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

SECTION_PATTERNS = {
    "leave carry forward": ("policy_hr_leave.txt", "2.6",
        "Employees may carry forward a maximum of 5 unused annual leave days "
        "to the following calendar year. Any days above 5 are forfeited on 31 December."),
    "annual leave carry": ("policy_hr_leave.txt", "2.6",
        "Employees may carry forward a maximum of 5 unused annual leave days "
        "to the following calendar year. Any days above 5 are forfeited on 31 December."),
    "carry forward": ("policy_hr_leave.txt", "2.6",
        "Employees may carry forward a maximum of 5 unused annual leave days "
        "to the following calendar year. Any days above 5 are forfeited on 31 December."),
    "install slack": ("policy_it_acceptable_use.txt", "2.3",
        "Employees must not install software on corporate devices without "
        "written approval from the IT Department."),
    "home office": ("policy_finance_reimbursement.txt", "3.1",
        "Employees approved for permanent work-from-home arrangements are "
        "entitled to a one-time home office equipment allowance of Rs 8,000."),
    "work from home equipment": ("policy_finance_reimbursement.txt", "3.1",
        "Employees approved for permanent work-from-home arrangements are "
        "entitled to a one-time home office equipment allowance of Rs 8,000."),
    "equipment allowance": ("policy_finance_reimbursement.txt", "3.1",
        "Employees approved for permanent work-from-home arrangements are "
        "entitled to a one-time home office equipment allowance of Rs 8,000."),
    "personal phone": ("policy_it_acceptable_use.txt", "3.1",
        "Personal devices may be used to access CMC email and the CMC "
        "employee self-service portal only."),
    "personal device": ("policy_it_acceptable_use.txt", "3.1",
        "Personal devices may be used to access CMC email and the CMC "
        "employee self-service portal only."),
    "flexible working": ("_refuse_", "", ""),
    "flexible work": ("_refuse_", "", ""),
    "da and meal": ("policy_finance_reimbursement.txt", "2.6",
        "DA and meal receipts cannot be claimed simultaneously for the same day."),
    "meal receipt": ("policy_finance_reimbursement.txt", "2.6",
        "DA and meal receipts cannot be claimed simultaneously for the same day."),
    "leave without pay": ("policy_hr_leave.txt", "5.2",
        "LWP requires approval from the Department Head and the HR Director. "
        "Manager approval alone is not sufficient."),
    "lwp": ("policy_hr_leave.txt", "5.2",
        "LWP requires approval from the Department Head and the HR Director. "
        "Manager approval alone is not sufficient."),
    "unpaid leave": ("policy_hr_leave.txt", "5.2",
        "LWP requires approval from the Department Head and the HR Director. "
        "Manager approval alone is not sufficient."),
}

logger = logging.getLogger(__name__)


def retrieve_documents(base_dir: str) -> dict[str, str]:
    documents = {}
    for name in DOCUMENT_PATHS:
        path = os.path.join(base_dir, name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Document not found: {path}")
        with open(path, encoding="utf-8") as f:
            documents[name] = f.read()
    return documents


def answer_question(question: str, documents: dict[str, str]) -> str:
    q = question.lower().strip()

    for pattern, (doc, section, text) in SECTION_PATTERNS.items():
        if pattern in q:
            if doc == "_refuse_":
                return REFUSAL_TEMPLATE
            return f"{doc}, Section {section}: {text}"

    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Q&A")
    parser.add_argument("--docs-dir", default="../data/policy-documents",
                        help="Directory containing policy .txt files")
    parser.add_argument("--output", help="Path to write Q&A log")
    args = parser.parse_args()

    documents = retrieve_documents(args.docs_dir)
    print("UC-X Policy Q&A — type your questions below (type 'exit' to quit)\n")

    log_lines = []
    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            break
        answer = answer_question(q, documents)
        print(answer + "\n")
        if args.output:
            log_lines.append(f"Q: {q}\nA: {answer}\n")

    if args.output and log_lines:
        with open(args.output, "w", encoding="utf-8") as f:
            f.writelines(log_lines)
        print(f"Q&A log written to {args.output}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
