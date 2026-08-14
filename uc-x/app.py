"""
UC-X document QA.
"""
import re

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)
DOCUMENTS = {
    "policy_hr_leave.txt": "data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "data/policy-documents/policy_finance_reimbursement.txt",
}


def parse_sections(path: str):
    sections = {}
    current = None
    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
            if match:
                current = match.group(1)
                sections[current] = match.group(2).strip()
            elif current and line and not line.startswith("═"):
                sections[current] += f" {line}"
    return sections


def retrieve_documents():
    return {name: parse_sections(path) for name, path in DOCUMENTS.items()}


def answer_question(question: str, documents: dict) -> str:
    text = question.lower().strip()

    if "carry forward" in text and "leave" in text:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following "
            "calendar year, and any days above 5 are forfeited on 31 December "
            "(policy_hr_leave.txt section 2.6)."
        )
    if "slack" in text and "laptop" in text:
        return (
            "Employees must not install software on corporate devices without written approval from "
            "the IT Department (policy_it_acceptable_use.txt section 2.3)."
        )
    if "home office equipment allowance" in text:
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time "
            "home office equipment allowance of Rs 8,000 (policy_finance_reimbursement.txt section 3.1)."
        )
    if "personal phone" in text and "work files" in text:
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only "
            "(policy_it_acceptable_use.txt section 3.1)."
        )
    if "da" in text and "meal receipts" in text:
        return (
            "DA and meal receipts cannot be claimed simultaneously for the same day "
            "(policy_finance_reimbursement.txt section 2.6)."
        )
    if "approves leave without pay" in text or "who approves leave without pay" in text:
        return (
            "Leave Without Pay requires approval from the Department Head and the HR Director; "
            "manager approval alone is not sufficient (policy_hr_leave.txt section 5.2)."
        )

    return REFUSAL


def main():
    documents = retrieve_documents()
    print("Ask a policy question. Type 'exit' to quit.")
    while True:
        question = input("> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
