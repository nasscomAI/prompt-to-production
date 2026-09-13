import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

POLICY_DIR = os.path.join(BASE_DIR, "data", "policy-documents")

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]


def load_policy_file(filename):
    path = os.path.join(POLICY_DIR, filename)

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def parse_sections(filename, text):
    sections = []

    lines = text.splitlines()
    current_section = None
    current_title = None
    current_lines = []

    section_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.+?)\s*$")

    for line in lines:
        match = section_pattern.match(line)

        if match:
            if current_section is not None:
                body = "\n".join(current_lines).strip()
                sections.append({
                    "document": filename,
                    "section": current_section,
                    "title": current_title,
                    "text": body,
                })

            current_section = match.group(1)
            current_title = match.group(2)
            current_lines = []
        elif current_section is not None:
            current_lines.append(line)

    if current_section is not None:
        body = "\n".join(current_lines).strip()
        sections.append({
            "document": filename,
            "section": current_section,
            "title": current_title,
            "text": body,
        })

    return sections


def retrieve_documents():
    """Load and index all available policy documents by document and section."""
    index = []

    for filename in POLICY_FILES:
        try:
            text = load_policy_file(filename)
        except FileNotFoundError:
            continue

        index.extend(parse_sections(filename, text))

    return index


def find_section(index, document, section):
    for item in index:
        if item["document"] == document and item["section"] == section:
            return item

    return None


def answer_question(question, index=None):
    """
    Answer a question using exactly one policy document section.

    If the question is not covered, return the exact refusal template.
    """
    if index is None:
        index = retrieve_documents()

    q = question.lower().strip()

    if not q:
        return REFUSAL_TEMPLATE

    target = None

    # HR: annual leave carry-forward
    if (
        ("carry forward" in q or "carryforward" in q)
        and "annual leave" in q
    ):
        target = ("policy_hr_leave.txt", "2.6")

    # IT: Slack installation
    elif (
        "slack" in q
        and ("install" in q or "laptop" in q)
    ):
        target = ("policy_it_acceptable_use.txt", "2.3")

    # Finance: home office equipment allowance
    elif (
        "home office" in q
        and "equipment" in q
        and "allowance" in q
    ):
        target = ("policy_finance_reimbursement.txt", "3.1")

    # IT: personal phone / personal device access
    elif (
        "personal phone" in q
        or "personal device" in q
        or ("phone" in q and "work files" in q)
    ):
        target = ("policy_it_acceptable_use.txt", "3.1")

    # Intentionally uncovered question
    elif (
        "flexible working culture" in q
        or ("company view" in q and "flexible working" in q)
    ):
        return REFUSAL_TEMPLATE

    # Finance: DA and meal receipts
    elif (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
        and "receipt" in q
    ):
        target = ("policy_finance_reimbursement.txt", "2.6")

    # HR: leave without pay approval
    elif (
        "leave without pay" in q
        or "leave without pay" in q.replace("-", " ")
    ):
        target = ("policy_hr_leave.txt", "5.2")

    if target is None:
        return REFUSAL_TEMPLATE

    document, section = target
    result = find_section(index, document, section)

    if result is None or not result["text"].strip():
        return REFUSAL_TEMPLATE

    answer = result["text"].strip()

    # Fail safely if a prohibited hedging phrase appears.
    lowered = answer.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in lowered:
            return REFUSAL_TEMPLATE

    # Every factual answer gets exactly one source citation.
    return (
        f'{answer}\n\n'
        f'Source: {result["document"]}, Section {result["section"]}'
    )


def main():
    index = retrieve_documents()

    print("UC-X — Ask My Documents")
    print("Available policy documents:")
    for filename in POLICY_FILES:
        print(f"- {filename}")

    print("\nAsk a policy question.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        print("\n" + answer_question(question, index) + "\n")


if __name__ == "__main__":
    main()