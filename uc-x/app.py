"""
UC-X: Ask My Documents.

Answers policy questions using only the three supplied policy documents.
Answers are deliberately restricted to a single source document.
"""

from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_DIR = BASE_DIR / "data" / "policy-documents"

DOCUMENTS = {
    "policy_hr_leave.txt": POLICY_DIR / "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": POLICY_DIR / "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": POLICY_DIR / "policy_finance_reimbursement.txt",
}

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)


def retrieve_documents():
    documents = {}

    for name, path in DOCUMENTS.items():
        if not path.is_file():
            raise FileNotFoundError(f"Policy document not found: {path}")

        text = path.read_text(encoding="utf-8-sig")

        if not text.strip():
            raise ValueError(f"Policy document is empty: {name}")

        documents[name] = text

    return documents


def index_sections(documents):
    indexed = {}

    pattern = re.compile(
        r"(?ms)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)"
    )

    for filename, text in documents.items():
        sections = {}

        for match in pattern.finditer(text):
            section = match.group(1)
            content = " ".join(match.group(2).split())
            sections[section] = content

        indexed[filename] = sections

    return indexed


def find_section(indexed, filename, section):
    return indexed.get(filename, {}).get(section)


def answer_question(question, indexed):
    q = question.lower().strip()

    if not q:
        return REFUSAL

    # HR: annual leave carry-forward
    if (
        ("carry forward" in q or "carry-forward" in q or "carryforward" in q)
        and ("annual leave" in q or "leave" in q)
    ):
        text = find_section(indexed, "policy_hr_leave.txt", "2.6")
        return f"{text} [policy_hr_leave.txt §2.6]"

    # IT: installing Slack/software
    if (
        ("install" in q or "installation" in q)
        and ("slack" in q or "software" in q)
        and ("work laptop" in q or "corporate" in q or "device" in q)
    ):
        text = find_section(indexed, "policy_it_acceptable_use.txt", "2.3")
        return f"{text} [policy_it_acceptable_use.txt §2.3]"

    # Finance: home office allowance
    if (
        ("home office" in q or "home-office" in q)
        and ("allowance" in q or "equipment" in q)
    ):
        text = find_section(indexed, "policy_finance_reimbursement.txt", "3.1")
        return f"{text} [policy_finance_reimbursement.txt §3.1]"

    # Personal device / phone for work files
    # Answer ONLY from IT §3.1. Do not blend HR remote-work information.
    if (
        ("personal phone" in q or "personal device" in q)
        and ("work files" in q or "files" in q)
        and ("home" in q or "from home" in q)
    ):
        text = find_section(indexed, "policy_it_acceptable_use.txt", "3.1")
        return f"{text} [policy_it_acceptable_use.txt §3.1]"

    # Finance: DA and meal receipts
    if (
        ("da" in q or "daily allowance" in q)
        and ("meal" in q or "receipt" in q)
    ):
        text = find_section(indexed, "policy_finance_reimbursement.txt", "2.6")
        return f"{text} [policy_finance_reimbursement.txt §2.6]"

    # HR: leave without pay approval
    if (
        ("leave without pay" in q or "lwp" in q)
        and ("approve" in q or "approval" in q or "who" in q)
    ):
        text = find_section(indexed, "policy_hr_leave.txt", "5.2")
        return f"{text} [policy_hr_leave.txt §5.2]"

    # Flexible working culture is intentionally not treated as a policy fact.
    return REFUSAL


def main():
    documents = retrieve_documents()
    indexed = index_sections(documents)

    print("UC-X Policy Assistant")
    print("Type 'exit' or 'quit' to stop.")
    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"exit", "quit"}:
            break

        answer = answer_question(question, indexed)
        print(f"Answer: {answer}")
        print()


if __name__ == "__main__":
    main()
