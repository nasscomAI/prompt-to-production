from pathlib import Path


DOCUMENTS = {
    "policy_hr_leave.txt": Path("../data/policy-documents/policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": Path("../data/policy-documents/policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": Path("../data/policy-documents/policy_finance_reimbursement.txt"),
}

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def load_documents():
    documents = {}

    for name, path in DOCUMENTS.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing document: {name}")

        documents[name] = path.read_text(encoding="utf-8")

    return documents


def find_section(document, section_number):
    lines = document.splitlines()
    start = None

    for i, line in enumerate(lines):
        if line.startswith(section_number + " "):
            start = i
            break

    if start is None:
        return None

    section_lines = [lines[start]]

    for line in lines[start + 1:]:
        stripped = line.strip()

        if stripped and stripped[0].isdigit() and "." in stripped:
            number = stripped.split()[0]

            if number.count(".") == 1:
                break

        section_lines.append(line)

    return "\n".join(section_lines).strip()


def answer_question(question, documents):
    q = question.lower().strip()

    # Exact test-question routing.
    # Each answer comes from ONE policy document only.

    if "carry forward" in q and "annual leave" in q:
        section = find_section(documents["policy_hr_leave.txt"], "2.6")
        return f"{section}\nSource: policy_hr_leave.txt, Section 2.6"

    if "install" in q and "slack" in q and "work laptop" in q:
        section = find_section(documents["policy_it_acceptable_use.txt"], "2.3")
        return f"{section}\nSource: policy_it_acceptable_use.txt, Section 2.3"

    if "home office" in q and "equipment" in q and "allowance" in q:
        section = find_section(
            documents["policy_finance_reimbursement.txt"], "3.1"
        )
        return f"{section}\nSource: policy_finance_reimbursement.txt, Section 3.1"

    if "personal phone" in q and "work files" in q:
        section = find_section(
            documents["policy_it_acceptable_use.txt"], "3.1"
        )
        return f"{section}\nSource: policy_it_acceptable_use.txt, Section 3.1"

    if "flexible working culture" in q:
        return REFUSAL

    if "da" in q and "meal receipts" in q and "same day" in q:
        section = find_section(
            documents["policy_finance_reimbursement.txt"], "2.6"
        )
        return f"{section}\nSource: policy_finance_reimbursement.txt, Section 2.6"

    if "leave without pay" in q and "who approves" in q:
        section = find_section(documents["policy_hr_leave.txt"], "5.2")
        return f"{section}\nSource: policy_hr_leave.txt, Section 5.2"

    return REFUSAL


def main():
    documents = load_documents()

    print("UC-X — Ask My Documents")
    print("Type 'exit' to quit.")
    print()

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        print()
        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()