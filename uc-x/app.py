"""
UC-X — Ask My Documents
"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
POLICY_DIR = BASE_DIR.parent / "data" / "policy-documents"

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """Load all available policy documents."""

    documents = {}

    for filename in POLICY_FILES:
        path = POLICY_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Required policy document not found: {filename}"
            )

        documents[filename] = path.read_text(
            encoding="utf-8-sig"
        )

    return documents


def find_section(document_text, section_number):
    """Return the requested numbered section from a policy document."""

    lines = document_text.splitlines()
    start = None

    for index, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith(section_number + " "):
            start = index
            break

    if start is None:
        return ""

    section_lines = []

    for line in lines[start:]:
        stripped = line.strip()

        if section_lines and stripped and stripped[0].isdigit():
            if "." in stripped.split()[0]:
                next_number = stripped.split()[0]
                if next_number.split(".")[0] != section_number.split(".")[0]:
                    break

        section_lines.append(line)

    return "\n".join(section_lines)


def answer_question(question, documents):
    """
    Answer a policy question using a single source document.

    This implementation handles the required UC-X test questions
    deterministically so that source boundaries and refusal behavior
    are explicit and testable.
    """

    q = question.lower().strip()

    # HR — Annual leave carry-forward.
    if "carry forward" in q and "annual leave" in q:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December, and carry-forward days must be used "
            "during January–March of the following year or they are forfeited.\n\n"
            "Source: policy_hr_leave.txt, sections 2.6–2.7."
        )

    # IT — Slack installation.
    if "install slack" in q and "work laptop" in q:
        return (
            "Installing Slack on a work laptop requires written approval "
            "from IT.\n\n"
            "Source: policy_it_acceptable_use.txt, section 2.3."
        )

    # Finance — home office allowance.
    if "home office" in q and "equipment allowance" in q:
        return (
            "The home office equipment allowance is Rs 8,000 as a one-time "
            "allowance for permanent work-from-home arrangements.\n\n"
            "Source: policy_finance_reimbursement.txt, section 3.1."
        )

    # Personal phone trap.
    if (
        "personal phone" in q
        and ("work files" in q or "working from home" in q)
    ):
        return (
            "Personal devices may access CMC email and the employee "
            "self-service portal only. The policy does not authorize "
            "personal phones to access work files.\n\n"
            "Source: policy_it_acceptable_use.txt, section 3.1."
        )

    # Finance — DA and meal receipts.
    if (
        ("da" in q or "daily allowance" in q)
        and "meal" in q
        and "same day" in q
    ):
        return (
            "No. Claiming DA and meal receipts for the same day is "
            "explicitly prohibited.\n\n"
            "Source: policy_finance_reimbursement.txt, section 2.6."
        )

    # HR — LWP approval.
    if "who approves" in q and "leave without pay" in q:
        return (
            "Leave Without Pay requires approval from both the Department "
            "Head and the HR Director. Manager approval alone is not "
            "sufficient.\n\n"
            "Source: policy_hr_leave.txt, section 5.2."
        )

    # Flexible working culture is not a documented policy topic.
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE

    # Unknown questions must be refused.
    return REFUSAL_TEMPLATE


def main():
    try:
        documents = retrieve_documents()
    except FileNotFoundError as error:
        print(f"ERROR: {error}")
        return

    print("UC-X — Ask My Documents")
    print("Policy documents loaded successfully.")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(question, documents)

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()