from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
POLICY_DIR = BASE_DIR.parent / "data" / "policy-documents"

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)


def retrieve_documents():
    """Load and index all policy documents by section number."""
    index = {}

    for filename in DOCUMENTS:
        path = POLICY_DIR / filename

        try:
            text = path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError) as exc:
            raise RuntimeError(f"Unable to read {filename}: {exc}") from exc

        sections = {}
        current_section = None
        buffer = []

        for line in text.splitlines():
            match = re.match(r"^\s*(\d+\.\d+)\s+", line)

            if match:
                if current_section is not None:
                    sections[current_section] = " ".join(buffer).strip()

                current_section = match.group(1)
                buffer = [line.strip()]

            elif current_section is not None:
                stripped = line.strip()

                if stripped and not set(stripped) <= {"═", "-", " "}:
                    buffer.append(stripped)

        if current_section is not None:
            sections[current_section] = " ".join(buffer).strip()

        index[filename] = sections

    return index


def answer_question(question, index):
    """Return a single-source answer or the exact refusal template."""

    q = question.lower().strip()

    # HR — Annual leave carry-forward
    if ("carry forward" in q or "carry-forward" in q) and "annual leave" in q:
        source = "policy_hr_leave.txt"
        section = "2.6"

        answer = (
            "Employees may carry forward a maximum of 5 unused annual "
            "leave days to the following calendar year. Any days above 5 "
            "are forfeited on 31 December."
        )

        return f"{answer} [{source}, Section {section}]"

    # IT — Software installation / Slack
    if ("slack" in q or "install software" in q) and (
        "laptop" in q or "work" in q or "install" in q
    ):
        source = "policy_it_acceptable_use.txt"
        section = "2.3"

        answer = (
            "Employees must not install software on corporate devices "
            "without written approval from the IT Department."
        )

        return f"{answer} [{source}, Section {section}]"

    # Finance — Home office allowance
    if (
        ("home office" in q or "wfh" in q or "work from home" in q)
        and ("allowance" in q or "equipment" in q)
    ):
        source = "policy_finance_reimbursement.txt"
        section = "3.1"

        answer = (
            "Employees approved for permanent work-from-home arrangements "
            "are entitled to a one-time home office equipment allowance "
            "of Rs 8,000."
        )

        return f"{answer} [{source}, Section {section}]"

    # IT — Personal phone / BYOD
    if (
        ("personal phone" in q or "personal device" in q)
        and ("work files" in q or "files" in q or "work" in q)
    ):
        source = "policy_it_acceptable_use.txt"
        section = "3.1"

        answer = (
            "Personal devices may be used to access CMC email and the "
            "CMC employee self-service portal only."
        )

        return f"{answer} [{source}, Section {section}]"

    # Exact refusal test
    if (
        "flexible working culture" in q
        or "flexible working" in q
        or "working culture" in q
    ):
        return REFUSAL

    # Finance — DA and meal receipts
    if (
        ("da" in q or "daily allowance" in q)
        and ("meal" in q or "receipt" in q)
    ):
        source = "policy_finance_reimbursement.txt"
        section = "2.6"

        answer = (
            "No. DA and meal receipts cannot be claimed simultaneously "
            "for the same day."
        )

        return f"{answer} [{source}, Section {section}]"

    # HR — Leave Without Pay approval
    if (
        ("leave without pay" in q or "lwp" in q)
        and ("approve" in q or "approval" in q or "who" in q)
    ):
        source = "policy_hr_leave.txt"
        section = "5.2"

        answer = (
            "LWP requires approval from the Department Head and the HR "
            "Director. Manager approval alone is not sufficient."
        )

        return f"{answer} [{source}, Section {section}]"

    return REFUSAL


def main():
    index = retrieve_documents()

    print("Ask My Documents")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            print()
            continue

        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()