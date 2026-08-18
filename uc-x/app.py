import os
import re

POLICY_DIR = os.path.join("..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def retrieve_documents():
    documents = {}

    for filename in POLICY_FILES:
        path = os.path.join(POLICY_DIR, filename)

        if not os.path.exists(path):
            raise FileNotFoundError("Missing policy document: " + path)

        with open(path, "r", encoding="utf-8") as file:
            text = file.read()

        sections = {}

        # Find every numbered clause: 1.1, 2.6, 3.1, etc.
        matches = list(re.finditer(r"(?m)^(\d+\.\d+)\s+", text))

        for i, match in enumerate(matches):
            section_no = match.group(1)
            start = match.start()

            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(text)

            section_text = text[start:end]

            # Keep only the actual numbered clause.
            lines = section_text.splitlines()
            clean_lines = []

            for line in lines:
                stripped = line.strip()

                # Stop at a major section heading.
                if re.match(r"^\d+\.\s+[A-Z]", stripped):
                    break

                # Ignore separator lines.
                if stripped and not all(
                    char in "═=─- " for char in stripped
                ):
                    clean_lines.append(line.rstrip())

            section_text = "\n".join(clean_lines).strip()

            sections[section_no] = section_text

        documents[filename] = sections

    return documents


def answer_question(question, documents):
    q = question.lower()

    if "carry forward" in q:
        filename = "policy_hr_leave.txt"
        section = "2.6"

    elif "slack" in q or "install" in q:
        filename = "policy_it_acceptable_use.txt"
        section = "2.3"

    elif "home office" in q or "equipment allowance" in q:
        filename = "policy_finance_reimbursement.txt"
        section = "3.1"

    elif "meal" in q and "da" in q:
        filename = "policy_finance_reimbursement.txt"
        section = "2.6"

    elif "leave without pay" in q or "lwp" in q:
        filename = "policy_hr_leave.txt"
        section = "5.2"

    else:
        return REFUSAL

    section_text = documents[filename].get(section)

    if not section_text:
        return REFUSAL

    return (
        section_text
        + "\n\nSource: "
        + filename
        + ", Section "
        + section
    )


def main():
    documents = retrieve_documents()

    print("UC-X Policy Q&A")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            print(REFUSAL)
            continue

        print("\n" + answer_question(question, documents) + "\n")


if __name__ == "__main__":
    main()