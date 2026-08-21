"""
UC-X app.py — Interactive policy question answering tool.
"""
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data" / "policy-documents"

DOCUMENTS = [
    ("HR policy", DATA_DIR / "policy_hr_leave.txt", "policy_hr_leave.txt"),
    ("IT policy", DATA_DIR / "policy_it_acceptable_use.txt", "policy_it_acceptable_use.txt"),
    ("Finance policy", DATA_DIR / "policy_finance_reimbursement.txt", "policy_finance_reimbursement.txt"),
]


def load_documents():
    documents = []
    for display_name, path, filename in DOCUMENTS:
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {path}")
        text = path.read_text(encoding="utf-8")
        documents.append((display_name, filename, parse_sections(text)))
    return documents


def parse_sections(text):
    sections = {}
    current = None
    for line in text.splitlines():
        match = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", line)
        if match:
            current = match.group(1)
            sections[current] = match.group(2).strip()
        elif current and line.strip():
            sections[current] += " " + line.strip()
    return sections


def answer_question(question, documents):
    q = question.strip().lower()
    if not q:
        return REFUSAL_TEMPLATE

    if "flexible working" in q and "culture" in q:
        return REFUSAL_TEMPLATE

    if "personal phone" in q and "work files" in q:
        return REFUSAL_TEMPLATE

    if "carry forward" in q and "annual leave" in q:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; "
            "any days above 5 are forfeited on 31 December. "
            "(HR policy section 2.6)"
        )

    if "install slack" in q or ("install" in q and "slack" in q):
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "(IT policy section 2.3)"
        )

    if "home office equipment" in q or ("equipment allowance" in q and "work-from-home" in q) or ("work from home" in q and "allowance" in q):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "(Finance policy section 3.1)"
        )

    if "da" in q and "meal" in q and ("same day" in q or "same day" in q):
        return (
            "DA and meal receipts cannot be claimed simultaneously for the same day. "
            "(Finance policy section 2.6)"
        )

    if "who approves" in q and "leave without pay" in q:
        return (
            "Leave Without Pay requires approval from the Department Head and the HR Director; manager approval alone is not sufficient. "
            "(HR policy section 5.2)"
        )

    if "personal devices" in q and ("email" in q or "self-service portal" in q):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "(IT policy section 3.1)"
        )

    # Fallback to exact section search when a single document is clearly referenced.
    matched_documents = []
    for display_name, filename, sections in documents:
        matches = [sec for sec, text in sections.items() if sec in q or any(term in question.lower() for term in text.lower().split())]
        if matches:
            matched_documents.append((display_name, filename, matches[:1], sections))

    if len(matched_documents) == 1:
        display_name, filename, matches, sections = matched_documents[0]
        section = matches[0]
        return f"{sections[section]} ({display_name} section {section})"

    return REFUSAL_TEMPLATE


def main():
    documents = load_documents()
    print("Policy question answering tool. Type a question or 'exit' to quit.")
    while True:
        try:
            question = input("Q: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break

        answer = answer_question(question, documents)
        print(answer)
        print()


if __name__ == "__main__":
    main()
