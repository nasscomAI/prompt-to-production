import os
import re


POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def retrieve_documents():
    documents = {}

    for path in POLICY_FILES:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy document not found: {path}")

        name = os.path.basename(path)

        with open(path, "r", encoding="utf-8") as file:
            text = file.read()

        documents[name] = text

    return documents


def get_section(text, section_number):
    lines = text.splitlines()

    start = None

    for i, line in enumerate(lines):
        match = re.match(r"^\s*" + re.escape(section_number) + r"\b", line)

        if match:
            start = i
            break

    if start is None:
        return None

    result = [lines[start]]

    for line in lines[start + 1:]:
        if re.match(r"^\s*\d+\.\d+\b", line):
            break

        result.append(line)

    return "\n".join(result).strip()


def answer_question(question, documents):
    q = question.lower()

    matches = []

    # HR policy
    if "carry forward" in q or "carryforward" in q:
        matches.append(("policy_hr_leave.txt", "2.6"))

    elif "annual leave" in q:
        matches.append(("policy_hr_leave.txt", "2.6"))

    elif "sick leave" in q or "medical certificate" in q:
        matches.append(("policy_hr_leave.txt", "3.2"))

    elif "leave without pay" in q or "lwp" in q:
        matches.append(("policy_hr_leave.txt", "5.2"))

    elif "encashment" in q:
        matches.append(("policy_hr_leave.txt", "7.2"))

    # IT policy
    if "slack" in q:
        matches.append(("policy_it_acceptable_use.txt", "2.3"))

    elif "personal phone" in q or "personal device" in q:
        matches.append(("policy_it_acceptable_use.txt", "3.1"))

    # Finance policy
    if "home office" in q or "equipment allowance" in q:
        matches.append(("policy_finance_reimbursement.txt", "3.1"))

    elif "da" in q and "meal" in q:
        matches.append(("policy_finance_reimbursement.txt", "2.6"))

    # Remove duplicate matches
    matches = list(dict.fromkeys(matches))

    # No matching document
    if not matches:
        return REFUSAL

    # Never blend different documents
    document_names = {doc for doc, section in matches}

    if len(document_names) > 1:
        return REFUSAL

    document, section = matches[0]

    content = get_section(documents[document], section)

    if content is None:
        return REFUSAL

    return f"{content}\nSource: {document}, section {section}"


def main():
    documents = retrieve_documents()

    print("Policy document assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        print("\n" + answer_question(question, documents) + "\n")


if __name__ == "__main__":
    main()