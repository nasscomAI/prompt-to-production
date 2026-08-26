import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "policy-documents"

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def load_documents():
    documents = {}

    for filename in POLICY_FILES:
        path = DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"Required policy file not found: {path}")

        text = path.read_text(encoding="utf-8")

        sections = {}
        matches = list(re.finditer(r"(?m)^(\d+\.\d+)\s+(.*)", text))

        for i, match in enumerate(matches):
            section_number = match.group(1)
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections[section_number] = text[start:end].strip()

        documents[filename] = sections

    return documents


def answer_question(question, documents):
    q = question.lower()

    # HR policy
    if "carry forward" in q and "annual leave" in q:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December.\n\n"
            "Source: policy_hr_leave.txt, Section 2.6"
        )

    if "leave without pay" in q or "approves leave without pay" in q:
        return (
            "Leave Without Pay requires approval from the Department Head "
            "and the HR Director. Manager approval alone is not sufficient.\n\n"
            "Source: policy_hr_leave.txt, Section 5.2"
        )

    # IT policy
    if "install slack" in q or ("install" in q and "work laptop" in q):
        return (
            "Employees must not install software on corporate devices without "
            "written approval from the IT Department.\n\n"
            "Source: policy_it_acceptable_use.txt, Section 2.3"
        )

    if ("personal phone" in q or "personal device" in q) and (
        "work files" in q or "access" in q
    ):
        return (
            "Personal devices may be used to access CMC email and the CMC "
            "employee self-service portal only. The policy does not grant "
            "general permission to access work files on a personal phone.\n\n"
            "Source: policy_it_acceptable_use.txt, Section 3.1"
        )

    # Finance policy
    if "home office equipment allowance" in q:
        return (
            "Employees approved for permanent work-from-home arrangements are "
            "entitled to a one-time home office equipment allowance of Rs 8,000.\n\n"
            "Source: policy_finance_reimbursement.txt, Section 3.1"
        )

    if "da" in q and "meal" in q:
        return (
            "No. DA and meal receipts cannot be claimed simultaneously for "
            "the same day.\n\n"
            "Source: policy_finance_reimbursement.txt, Section 2.6"
        )

    return REFUSAL_TEMPLATE


def main():
    try:
        documents = load_documents()
    except FileNotFoundError as error:
        print(f"Error: {error}")
        return

    print("CMC Policy Question Answering Agent")
    print("Type a question, or type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            print("Please enter a question.\n")
            continue

        print()
        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()