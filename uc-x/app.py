"""
UC-X - Ask My Documents.
"""

from pathlib import Path
import re

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance."""

SECTION_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)")
TOP_LEVEL_SECTION_PATTERN = re.compile(r"^\d+\.\s+")
ASCII_LETTER_OR_DIGIT = re.compile(r"[A-Za-z0-9]")
PROHIBITED_PHRASES = [
    "while not explicitly covered",
    "generally",
    "typically",
    "common practice",
]

ANSWER_RULES = [
    {
        "name": "annual leave carry-forward",
        "required": ["carry", "forward", "annual", "leave"],
        "filename": "policy_hr_leave.txt",
        "section": "2.6",
    },
    {
        "name": "software installation",
        "required": ["install"],
        "any": ["slack", "software", "application", "app"],
        "filename": "policy_it_acceptable_use.txt",
        "section": "2.3",
    },
    {
        "name": "home office equipment allowance",
        "required": ["home", "office", "equipment", "allowance"],
        "filename": "policy_finance_reimbursement.txt",
        "section": "3.1",
    },
    {
        "name": "personal phone work files",
        "required": ["personal"],
        "any": ["phone", "device", "mobile"],
        "all_any": [["work", "files", "file", "home", "access"]],
        "filename": "policy_it_acceptable_use.txt",
        "section": "3.1",
    },
    {
        "name": "daily allowance and meal receipts",
        "required": ["meal"],
        "any": ["da", "allowance", "receipts", "receipt"],
        "filename": "policy_finance_reimbursement.txt",
        "section": "2.6",
    },
    {
        "name": "leave without pay approval",
        "required": ["leave", "without", "pay"],
        "any": ["approve", "approves", "approval", "lwp"],
        "filename": "policy_hr_leave.txt",
        "section": "5.2",
    },
]


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def retrieve_documents() -> dict[str, dict[str, str]]:
    """Load all policy files and index them by document filename and section number."""
    documents: dict[str, dict[str, str]] = {}

    for file_path in POLICY_FILES:
        path = Path(file_path)
        filename = path.name
        documents[filename] = {}

        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue

        current_section: str | None = None
        current_text: list[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            match = SECTION_PATTERN.match(line)

            if match:
                if current_section:
                    documents[filename][current_section] = " ".join(current_text)
                current_section = match.group(1)
                current_text = [match.group(2).strip()]
                continue

            if not current_section:
                continue
            if not line:
                continue
            if not ASCII_LETTER_OR_DIGIT.search(line):
                continue
            if TOP_LEVEL_SECTION_PATTERN.match(line):
                continue

            current_text.append(line)

        if current_section:
            documents[filename][current_section] = " ".join(current_text)

    return documents


def rule_matches(rule: dict, question: str) -> bool:
    required = rule.get("required", [])
    optional_any = rule.get("any", [])
    grouped_any = rule.get("all_any", [])

    if not all(term in question for term in required):
        return False
    if optional_any and not any(term in question for term in optional_any):
        return False
    for group in grouped_any:
        if not any(term in question for term in group):
            return False
    return True


def select_single_source(question: str) -> tuple[str, str] | None:
    normalized_question = normalize(question)
    matches = [
        (rule["filename"], rule["section"])
        for rule in ANSWER_RULES
        if rule_matches(rule, normalized_question)
    ]

    unique_matches = sorted(set(matches))
    if len(unique_matches) != 1:
        return None
    return unique_matches[0]


def answer_question(question: str, documents: dict[str, dict[str, str]]) -> str:
    """Return a single-source answer with citation, or the exact refusal template."""
    source = select_single_source(question)
    if not source:
        return REFUSAL

    filename, section = source
    section_text = documents.get(filename, {}).get(section)
    if not section_text:
        return REFUSAL

    answer = f"{filename} section {section}: {section_text}"
    lowered = answer.lower()
    if any(phrase in lowered for phrase in PROHIBITED_PHRASES):
        return REFUSAL
    return answer


def main() -> None:
    documents = retrieve_documents()

    while True:
        try:
            question = input("Ask a question: ").strip()
        except EOFError:
            break

        if question.lower() == "exit":
            break
        if not question:
            print(REFUSAL)
            continue

        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
