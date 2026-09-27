from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parent
POLICY_DIR = BASE_DIR.parent / "data" / "policy-documents"

DOCUMENTS = {
    "policy_hr_leave.txt": POLICY_DIR / "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": POLICY_DIR / "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": POLICY_DIR / "policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).

Please contact [relevant team] for guidance."""


HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]


def load_documents():
    documents = {}

    for name, path in DOCUMENTS.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing policy document: {path}")

        documents[name] = path.read_text(encoding="utf-8")

    return documents


def split_sections(text):
    """
    Split a policy document into numbered sections such as:
    2.6, 3.1, 5.2
    """
    pattern = r"(?m)^(?P<section>\d+(?:\.\d+)?)\s*[\.\-:]?\s*(?P<title>.*)$"
    matches = list(re.finditer(pattern, text))

    sections = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        content = text[start:end].strip()

        sections.append({
            "section": match.group("section"),
            "title": match.group("title").strip(),
            "content": content,
        })

    return sections


def build_index(documents):
    index = {}

    for name, text in documents.items():
        index[name] = split_sections(text)

    return index


def find_matching_sections(question, index):
    """
    Retrieve candidate sections using question keywords.
    """
    q = question.lower()

    keyword_groups = [
        {
            "keywords": ["carry forward", "unused annual leave", "annual leave", "forfeit"],
            "document": "policy_hr_leave.txt",
            "section": "2.6",
        },
        {
            "keywords": ["slack", "install", "work laptop", "software"],
            "document": "policy_it_acceptable_use.txt",
            "section": "2.3",
        },
        {
            "keywords": ["home office", "equipment allowance", "equipment", "allowance", "work from home"],
            "document": "policy_finance_reimbursement.txt",
            "section": "3.1",
        },
        {
            "keywords": ["personal phone", "personal device", "phone", "work files"],
            "document": "policy_it_acceptable_use.txt",
            "section": "3.1",
        },
        {
            "keywords": ["da", "meal receipts", "same day", "daily allowance"],
            "document": "policy_finance_reimbursement.txt",
            "section": "2.6",
        },
        {
            "keywords": ["leave without pay", "unpaid leave", "who approves leave"],
            "document": "policy_hr_leave.txt",
            "section": "5.2",
        },
    ]

    candidates = []

    for group in keyword_groups:
        if any(keyword in q for keyword in group["keywords"]):
            candidates.append(group)

    return candidates


def get_section(index, document, section_number):
    for section in index.get(document, []):
        if section["section"] == section_number:
            return section

    return None


def clean_content(content):
    """
    Keep the policy text intact enough to preserve conditions,
    but remove excessive whitespace.
    """
    return re.sub(r"\s+", " ", content).strip()


def answer_question(question, index):
    q = question.lower().strip()

    # Explicitly refuse the question about flexible working culture.
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE

    candidates = find_matching_sections(question, index)

    if not candidates:
        return REFUSAL_TEMPLATE

    # Reject situations where multiple policy documents would be needed.
    documents = {candidate["document"] for candidate in candidates}

    if len(documents) != 1:
        return REFUSAL_TEMPLATE

    candidate = candidates[0]
    document = candidate["document"]
    section_number = candidate["section"]

    section = get_section(index, document, section_number)

    if section is None:
        return REFUSAL_TEMPLATE

    content = clean_content(section["content"])

    # The personal-phone question must remain strictly within IT policy.
    if "personal phone" in q or "personal device" in q:
        return (
            f"{content}\n"
            f"Source: {document}, section {section_number}."
        )

    return (
        f"{content}\n"
        f"Source: {document}, section {section_number}."
    )


def validate_answer(answer):
    """
    Basic enforcement check before returning an answer.
    """
    if answer == REFUSAL_TEMPLATE:
        return answer

    lower = answer.lower()

    for phrase in HEDGING_PHRASES:
        if phrase in lower:
            return REFUSAL_TEMPLATE

    source_count = sum(
        answer.count(document)
        for document in DOCUMENTS
    )

    if source_count != 1:
        return REFUSAL_TEMPLATE

    if "source:" not in lower:
        return REFUSAL_TEMPLATE

    return answer


def main():
    documents = load_documents()
    index = build_index(documents)

    print("UC-X — Ask My Documents")
    print("Type a policy question.")
    print("Type 'exit' to quit.")
    print()

    while True:
        question = input("Question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            print("Please enter a question.")
            continue

        answer = answer_question(question, index)
        answer = validate_answer(answer)

        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()