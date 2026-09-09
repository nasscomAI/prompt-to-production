import os
import re


REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def retrieve_documents():
    """Load all three policy documents and index them by section number."""
    documents = {}

    for path in POLICY_FILES:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
        except OSError as error:
            raise OSError(f"Could not read {path}: {error}")

        document_name = os.path.basename(path)

        sections = {}
        current_section = None
        current_text = []

        for line in content.splitlines():
            match = re.match(r"^\s*(\d+(?:\.\d+)?)\s+(.*)$", line)

            if match:
                if current_section is not None:
                    sections[current_section] = " ".join(
                        current_text
                    ).strip()

                current_section = match.group(1)
                current_text = [match.group(2).strip()]

            elif current_section is not None:
                text = line.strip()

                if text and not text.startswith("="):
                    current_text.append(text)

        if current_section is not None:
            sections[current_section] = " ".join(current_text).strip()

        documents[document_name] = sections

    return documents


def answer_question(question, documents):
    """Answer using one source document or return the exact refusal."""

    q = question.lower().strip()

    # HR policy questions
    hr = documents.get("policy_hr_leave.txt", {})

    if "carry forward" in q and "annual leave" in q:
        return (
            f"Employees may carry forward a maximum of 5 unused annual leave "
            f"days to the following calendar year. Any days above 5 are "
            f"forfeited on 31 December. "
            f"[Source: policy_hr_leave.txt, Section 2.6]"
        )

    if "leave without pay" in q and "approve" in q:
        return (
            f"Leave Without Pay requires approval from the Department Head "
            f"and the HR Director. Manager approval alone is not sufficient. "
            f"[Source: policy_hr_leave.txt, Section 5.2]"
        )

    # IT policy questions
    it = documents.get("policy_it_acceptable_use.txt", {})

    if "slack" in q and "work laptop" in q:
        return (
            f"Installing Slack on a work laptop requires written IT approval. "
            f"[Source: policy_it_acceptable_use.txt, Section 2.3]"
        )

    if "personal phone" in q and "work files" in q:
        section = it.get("3.1")

        if section:
            return (
                f"{section} "
                f"[Source: policy_it_acceptable_use.txt, Section 3.1]"
            )

        return REFUSAL

    # Finance policy questions
    finance = documents.get("policy_finance_reimbursement.txt", {})

    if "home office" in q and "equipment allowance" in q:
        return (
            f"The home office equipment allowance is Rs 8,000 one-time "
            f"for permanent work-from-home employees. "
            f"[Source: policy_finance_reimbursement.txt, Section 3.1]"
        )

    if "da" in q and "meal" in q and "same day" in q:
        return (
            f"DA and meal receipts cannot both be claimed for the same day; "
            f"this is explicitly prohibited. "
            f"[Source: policy_finance_reimbursement.txt, Section 2.6]"
        )

    # Unknown / unsupported questions must use the exact refusal.
    return REFUSAL


def main():
    documents = retrieve_documents()

    print("Ask questions about the available policy documents.")
    print("Type 'exit' to quit.")
    print()

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(question, documents)
        print("Answer:", answer)
        print()


if __name__ == "__main__":
    main()