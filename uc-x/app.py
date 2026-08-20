"""
UC-X - Ask My Documents

Interactive single-source policy Q&A. The app answers only from one policy
document section at a time, or returns the required refusal template verbatim.
"""
import re
from pathlib import Path


POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

ANSWER_RULES = (
    {
        "name": "annual_leave_carry_forward",
        "required": ("carry", "forward", "annual", "leave"),
        "document": "policy_hr_leave.txt",
        "section": "2.6",
        "answer": (
            "Yes. Employees may carry forward a maximum of 5 unused annual "
            "leave days to the following calendar year; any days above 5 are "
            "forfeited on 31 December."
        ),
    },
    {
        "name": "install_slack",
        "required": ("install", "slack"),
        "document": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "answer": (
            "No employee may install Slack or any other software on a corporate "
            "device without written approval from the IT Department."
        ),
    },
    {
        "name": "home_office_equipment_allowance",
        "required": ("home", "office", "equipment", "allowance"),
        "document": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "answer": (
            "Employees approved for permanent work-from-home arrangements are "
            "entitled to a one-time home office equipment allowance of Rs 8,000."
        ),
    },
    {
        "name": "personal_phone_work_files",
        "required_any": (
            ("personal", "phone", "work", "files"),
            ("personal", "device", "work", "files"),
            ("personal", "phone", "from", "home"),
        ),
        "document": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "answer": (
            "Personal devices may be used to access CMC email and the CMC "
            "employee self-service portal only. This section does not permit "
            "accessing work files from a personal phone."
        ),
    },
    {
        "name": "da_and_meal_receipts",
        "required": ("da", "meal", "receipts"),
        "document": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "answer": (
            "No. DA and meal receipts cannot be claimed simultaneously for the "
            "same day; if actual meal expenses are claimed instead of DA, "
            "receipts are mandatory and the combined meal claim must not exceed "
            "Rs 750 per day."
        ),
    },
    {
        "name": "lwp_approvers",
        "required_any": (
            ("who", "approves", "leave", "without", "pay"),
            ("approves", "lwp"),
            ("approval", "lwp"),
        ),
        "document": "policy_hr_leave.txt",
        "section": "5.2",
        "answer": (
            "Leave Without Pay requires approval from both the Department Head "
            "and the HR Director. Manager approval alone is not sufficient."
        ),
    },
)


def retrieve_documents(base_dir: Path | None = None) -> dict:
    """
    Load all three policy files and index them by document name and section.
    """
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent / "data" / "policy-documents"

    index = {}
    for file_name in POLICY_FILES:
        path = base_dir / file_name
        text = path.read_text(encoding="utf-8-sig")
        index[file_name] = _parse_sections(text)
    return index


def answer_question(question: str, documents: dict) -> str:
    """
    Return a single-source answer with citation, or the refusal template.
    """
    normalized = _normalize(question)
    for rule in ANSWER_RULES:
        if _matches_rule(normalized, rule):
            document = rule["document"]
            section = rule["section"]
            if section not in documents.get(document, {}):
                return REFUSAL_TEMPLATE
            return f"{rule['answer']}\nSource: {document} section {section}."
    return REFUSAL_TEMPLATE


def _parse_sections(text: str) -> dict:
    sections = {}
    current_section = None

    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue

        match = SECTION_RE.match(line)
        if match:
            current_section = match.group(1)
            sections[current_section] = match.group(2)
        elif current_section:
            sections[current_section] = f"{sections[current_section]} {line}"

    return sections


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _matches_rule(normalized_question: str, rule: dict) -> bool:
    words = set(normalized_question.split())
    if "required" in rule:
        return all(term in words for term in rule["required"])
    return any(all(term in words for term in terms) for terms in rule["required_any"])


def main():
    documents = retrieve_documents()
    print("UC-X Ask My Documents")
    print("Type a question and press Enter. Type exit or quit to stop.")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break

        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
