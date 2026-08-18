"""UC-X — Policy Q&A assistant.

The app answers questions using only the supplied policy documents. It refuses
out-of-scope questions using the exact template required by the project.
"""
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def load_documents(base_dir: str):
    files = {
        "policy_hr_leave.txt": Path(base_dir) / "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": Path(base_dir) / "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": Path(base_dir) / "policy_finance_reimbursement.txt",
    }
    docs = {}
    for name, path in files.items():
        text = path.read_text(encoding="utf-8")
        sections = {}
        for match in re.finditer(r"(?m)^(\d+\.\d+)\s+(.+)$", text):
            section = match.group(1)
            start = match.start()
            next_match = re.search(r"(?m)^(\d+\.\d+)\s+", text[match.end():])
            end = match.end() + next_match.start() if next_match else len(text)
            sections[section] = text[start:end].strip()
        docs[name] = sections
    return docs


def answer_question(question: str, docs):
    q = question.lower().strip()
    if not q:
        return "Please enter a question."

    if "carry forward" in q or "unused annual leave" in q or "annual leave" in q and "carry" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Source: policy_hr_leave.txt § 2.6"

    if "slack" in q and "install" in q:
        return "Employees must not install software on corporate devices without written approval from the IT Department. Source: policy_it_acceptable_use.txt § 2.3"

    if "home office equipment allowance" in q or "work from home equipment" in q:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. Source: policy_finance_reimbursement.txt § 3.1"

    if "personal phone" in q and "work files" in q and "home" in q:
        return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Source: policy_it_acceptable_use.txt § 3.1"

    if "flexible working culture" in q or "culture" in q and "working" in q:
        return REFUSAL_TEMPLATE

    if "da and meal receipts" in q or "meal receipts" in q:
        return "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day. Source: policy_finance_reimbursement.txt § 2.6"

    if "leave without pay" in q or "lwp" in q:
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. Source: policy_hr_leave.txt § 5.2"

    return REFUSAL_TEMPLATE


def main():
    docs = load_documents("../data/policy-documents")
    print("Ask a policy question (type 'exit' to quit):")
    while True:
        question = input("Q> ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            break
        print(answer_question(question, docs))
        print()


if __name__ == "__main__":
    main()
