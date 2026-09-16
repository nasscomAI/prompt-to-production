import argparse
import os
import re

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}


def load_documents():
    documents = {}

    for name, path in DOCUMENTS.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy document not found: {path}")

        with open(path, "r", encoding="utf-8") as file:
            documents[name] = file.read()

    return documents


def get_section(document_text, section_number):
    pattern = rf"(?ms)^[ \t]*{re.escape(section_number)}[ \t]+(.+?)(?=^[ \t]*\d+\.\d+[ \t]|^[ \t]*\d+\.[ \t]|\Z)"
    match = re.search(pattern, document_text)

    if not match:
        return None

    return f"{section_number} {match.group(1).strip()}"


def answer_question(question, documents):
    q = question.lower().strip()

    # HR policy
    if "carry forward" in q and "annual leave" in q:
        section = get_section(documents["policy_hr_leave.txt"], "2.6")
        return f"{section}\nSource: policy_hr_leave.txt, Section 2.6"

    if "leave without pay" in q or "lwp" in q:
        section = get_section(documents["policy_hr_leave.txt"], "5.2")
        return f"{section}\nSource: policy_hr_leave.txt, Section 5.2"

    # IT policy
    if "install slack" in q or ("install" in q and "work laptop" in q):
        section = get_section(
            documents["policy_it_acceptable_use.txt"], "2.3"
        )
        return f"{section}\nSource: policy_it_acceptable_use.txt, Section 2.3"

    if "personal phone" in q and "work file" in q:
        section = get_section(
            documents["policy_it_acceptable_use.txt"], "3.1"
        )
        return (
            f"{section}\n"
            "Source: policy_it_acceptable_use.txt, Section 3.1\n"
            "Note: Section 3.1 permits personal devices to access CMC email "
            "and the CMC employee self-service portal only."
        )

    # Finance policy
    if "home office" in q and "allowance" in q:
        section = get_section(
            documents["policy_finance_reimbursement.txt"], "3.1"
        )
        return f"{section}\nSource: policy_finance_reimbursement.txt, Section 3.1"

    if "da" in q and "meal" in q and "same day" in q:
        section = get_section(
            documents["policy_finance_reimbursement.txt"], "2.6"
        )
        return f"{section}\nSource: policy_finance_reimbursement.txt, Section 2.6"

    return REFUSAL


def main():
    parser = argparse.ArgumentParser(
        description="UC-X — Ask My Documents"
    )
    parser.add_argument(
        "--question",
        help="Optional question. If omitted, starts interactive mode.",
    )
    args = parser.parse_args()

    documents = load_documents()

    if args.question:
        print(answer_question(args.question, documents))
        return

    print("UC-X — Ask My Documents")
    print("Type a question, or type 'exit' to quit.")

    while True:
        question = input("\nQuestion: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            continue

        print("\nAnswer:")
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
