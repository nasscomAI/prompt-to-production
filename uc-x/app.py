"""UC-X — Ask My Documents."""

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
POLICY_DIR = BASE / "data" / "policy-documents"

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    index = {}

    for filename in DOCUMENTS:
        path = POLICY_DIR / filename
        text = path.read_text(encoding="utf-8-sig")

        sections = {}
        current = None

        for line in text.splitlines():
            match = re.match(r"^\s*(\d+(?:\.\d+)?)\s+(.+?)\s*$", line)

            if match:
                current = match.group(1)
                sections[current] = line.strip()
            elif current and line.strip():
                sections[current] += " " + line.strip()

        index[filename] = sections

    return index


def answer_question(question, index):
    q = question.lower().strip()

    rules = [
        (("carry forward",), "policy_hr_leave.txt", "2.6"),
        (("carry-forward",), "policy_hr_leave.txt", "2.6"),
        (("install slack",), "policy_it_acceptable_use.txt", "2.3"),
        (("equipment allowance",), "policy_finance_reimbursement.txt", "3.1"),
        (("personal phone",), "policy_it_acceptable_use.txt", "3.1"),
        (("da", "meal"), "policy_finance_reimbursement.txt", "2.6"),
        (("leave without pay",), "policy_hr_leave.txt", "5.2"),
    ]

    matches = []

    for keywords, document, section in rules:
        if all(keyword in q for keyword in keywords):
            matches.append((document, section))

    matches = list(dict.fromkeys(matches))

    if not matches:
        return REFUSAL

    documents = {document for document, _ in matches}

    if len(documents) > 1:
        return REFUSAL

    document, section = matches[0]
    section_text = index.get(document, {}).get(section)

    if not section_text:
        return REFUSAL

    return f"{section_text} [{document}, section {section}]"


def main():
    index = retrieve_documents()

    print("UC-X Ask My Documents")
    print("Type a question, or 'exit' to quit.")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break

        if question.lower() in {"exit", "quit"}:
            break

        if question:
            print(answer_question(question, index))


if __name__ == "__main__":
    main()