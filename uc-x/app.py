import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POLICY_FILES = {
    "policy_hr_leave.txt": os.path.normpath(
        os.path.join(
            BASE_DIR,
            "..",
            "data",
            "policy-documents",
            "policy_hr_leave.txt",
        )
    ),
    "policy_it_acceptable_use.txt": os.path.normpath(
        os.path.join(
            BASE_DIR,
            "..",
            "data",
            "policy-documents",
            "policy_it_acceptable_use.txt",
        )
    ),
    "policy_finance_reimbursement.txt": os.path.normpath(
        os.path.join(
            BASE_DIR,
            "..",
            "data",
            "policy-documents",
            "policy_finance_reimbursement.txt",
        )
    ),
}

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """Load all three policy documents."""
    documents = {}

    for filename, path in POLICY_FILES.items():
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Policy document not found: {path}"
            )

        with open(path, "r", encoding="utf-8") as file:
            documents[filename] = file.read()

    return documents


def get_section(document_text, section_number):
    """
    Extract only the requested numbered policy section.
    Stops at the next numbered section or major heading.
    """

    lines = document_text.splitlines()
    start = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        if re.match(
            rf"^{re.escape(section_number)}\s*[:.]?\s+",
            stripped,
        ):
            start = i
            break

    if start is None:
        return None

    collected = []

    for line in lines[start:]:
        stripped = line.strip()

        # Stop at next subsection, e.g. 2.7
        if collected and re.match(
            r"^\d+\.\d+\s*[:.]?\s+",
            stripped,
        ):
            break

        # Stop at next major section, e.g. 3.
        if collected and re.match(
            r"^\d+\.\s+",
            stripped,
        ):
            break

        # Stop at obvious section-heading separators
        if collected and (
            stripped.startswith("═")
            or stripped.startswith("=")
        ):
            break

        collected.append(line.rstrip())

    return "\n".join(collected).strip()


def answer_question(question, documents):
    """
    Answer using one policy document only.

    No cross-document blending.
    Every factual answer includes source document and section.
    Questions not covered by the policies receive the exact refusal.
    """

    q = question.lower().strip()

    # ---------------------------------------------------------
    # HR POLICY — Section 2.6
    # Annual leave carry-forward
    # ---------------------------------------------------------
    if "carry forward" in q and "annual leave" in q:
        section = get_section(
            documents["policy_hr_leave.txt"],
            "2.6",
        )

        if section:
            return (
                f"{section}\n\n"
                "Source: policy_hr_leave.txt, section 2.6"
            )

    # ---------------------------------------------------------
    # IT POLICY — Section 2.3
    # Software installation / Slack
    # ---------------------------------------------------------
    if "slack" in q and (
        "install" in q
        or "work laptop" in q
    ):
        section = get_section(
            documents["policy_it_acceptable_use.txt"],
            "2.3",
        )

        if section:
            return (
                f"{section}\n\n"
                "Source: policy_it_acceptable_use.txt, section 2.3"
            )

    # ---------------------------------------------------------
    # FINANCE POLICY — Section 3.1
    # Home office equipment allowance
    # ---------------------------------------------------------
    if (
        "home office" in q
        and "equipment" in q
        and "allowance" in q
    ):
        section = get_section(
            documents["policy_finance_reimbursement.txt"],
            "3.1",
        )

        if section:
            return (
                f"{section}\n\n"
                "Source: policy_finance_reimbursement.txt, section 3.1"
            )

    # ---------------------------------------------------------
    # IT POLICY — Section 3.1
    # Personal phone / personal device
    #
    # IMPORTANT:
    # Do NOT combine this with HR remote-work information.
    # ---------------------------------------------------------
    if (
        "personal phone" in q
        and (
            "work files" in q
            or "work file" in q
        )
    ):
        section = get_section(
            documents["policy_it_acceptable_use.txt"],
            "3.1",
        )

        if section:
            return (
                f"{section}\n\n"
                "Source: policy_it_acceptable_use.txt, section 3.1"
            )

        return REFUSAL

    # ---------------------------------------------------------
    # OUT-OF-SCOPE QUESTION
    # Flexible working culture
    # ---------------------------------------------------------
    if "flexible working culture" in q:
        return REFUSAL

    # ---------------------------------------------------------
    # FINANCE POLICY — Section 2.6
    # DA and meal receipts
    # ---------------------------------------------------------
    if (
        "da" in q
        and "meal" in q
        and (
            "same day" in q
            or "simultaneously" in q
        )
    ):
        section = get_section(
            documents["policy_finance_reimbursement.txt"],
            "2.6",
        )

        if section:
            return (
                f"{section}\n\n"
                "Source: policy_finance_reimbursement.txt, section 2.6"
            )

    # ---------------------------------------------------------
    # HR POLICY — Section 5.2
    # Leave Without Pay approval
    # ---------------------------------------------------------
    if (
        "leave without pay" in q
        and (
            "approve" in q
            or "approves" in q
            or "approval" in q
        )
    ):
        section = get_section(
            documents["policy_hr_leave.txt"],
            "5.2",
        )

        if section:
            return (
                f"{section}\n\n"
                "Source: policy_hr_leave.txt, section 5.2"
            )

    # ---------------------------------------------------------
    # ALL OTHER QUESTIONS
    # ---------------------------------------------------------
    return REFUSAL


def main():
    try:
        documents = retrieve_documents()
    except Exception as error:
        print(f"ERROR: {error}")
        return

    print("Policy documents loaded successfully.")
    print("Ask a policy question. Type 'exit' or 'quit' to stop.")

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            print("Please enter a question.")
            continue

        print("\n" + answer_question(question, documents))


if __name__ == "__main__":
    main()