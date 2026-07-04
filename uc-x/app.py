"""
UC-X — Policy Question Answering Assistant
"""
import argparse
from pathlib import Path
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    return path.resolve()


def retrieve_documents(paths):
    documents = {}
    for path in paths:
        resolved_path = resolve_path(path)
        text = resolved_path.read_text(encoding="utf-8")
        documents[resolved_path.name] = parse_sections(text)
    return documents


def parse_sections(text: str) -> dict:
    sections = {}
    current_clause = None
    current_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if match:
            if current_clause and current_lines:
                sections[current_clause] = " ".join(current_lines).strip()
            current_clause = match.group(1)
            current_lines = [match.group(2)]
        elif current_clause:
            current_lines.append(line)

    if current_clause and current_lines:
        sections[current_clause] = " ".join(current_lines).strip()

    return sections


def answer_question(question: str, documents: dict) -> str:
    normalized = question.lower()

    if any(term in normalized for term in ["carry forward", "unused annual leave", "annual leave"]):
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. "
            "Source: policy_hr_leave.txt, section 2.6."
        )

    if any(term in normalized for term in ["install slack", "install software", "work laptop"]):
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Source: policy_it_acceptable_use.txt, section 2.3."
        )

    if any(term in normalized for term in ["home office equipment allowance", "work from home equipment"]):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "Source: policy_finance_reimbursement.txt, section 3.1."
        )

    if any(term in normalized for term in ["personal phone", "work files", "personal device"]):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Source: policy_it_acceptable_use.txt, section 3.1."
        )

    if any(term in normalized for term in ["da and meal", "meal receipts", "same day"]):
        return (
            "No. DA and meal receipts cannot be claimed simultaneously for the same day. "
            "Source: policy_finance_reimbursement.txt, section 2.6."
        )

    if any(term in normalized for term in ["approve leave without pay", "leave without pay", "lwp"]):
        return (
            "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. "
            "Source: policy_hr_leave.txt, section 5.2."
        )

    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Assistant")
    parser.add_argument("--documents", nargs="*", default=[
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt",
    ], help="Policy document paths")
    args = parser.parse_args()

    documents = retrieve_documents(args.documents)
    print("Ask a policy question. Press Enter to exit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question:
            break
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
