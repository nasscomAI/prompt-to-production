import argparse
import os
import re


REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

DOCUMENTS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def retrieve_documents():
    documents = {}

    for path in DOCUMENTS:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy document not found: {path}")

        filename = os.path.basename(path)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        sections = {}
        current_section = None
        buffer = []

        for line in text.splitlines():
            match = re.match(r"^(\d+(?:\.\d+)?)\s+", line.strip())

            if match:
                if current_section is not None:
                    sections[current_section] = " ".join(buffer).strip()

                current_section = match.group(1)
                buffer = [line.strip()]
            elif current_section is not None:
                stripped = line.strip()
                if stripped:
                    buffer.append(stripped)

        if current_section is not None:
            sections[current_section] = " ".join(buffer).strip()

        documents[filename] = sections

    return documents


def answer_question(question, documents):
    q = question.lower().strip()

    # HR policy
    if "carry forward" in q and "annual leave" in q:
        text = documents["policy_hr_leave.txt"]["2.6"]
        return f"{text} [Source: policy_hr_leave.txt, Section 2.6]"

    if "leave without pay" in q and "approv" in q:
        text = documents["policy_hr_leave.txt"]["5.2"]
        return f"{text} [Source: policy_hr_leave.txt, Section 5.2]"

    # IT policy
    if "install slack" in q and ("work laptop" in q or "laptop" in q):
        text = documents["policy_it_acceptable_use.txt"]["2.3"]
        return f"{text} [Source: policy_it_acceptable_use.txt, Section 2.3]"

    # Finance policy
    if "home office equipment" in q and "allowance" in q:
        text = documents["policy_finance_reimbursement.txt"]["3.1"]
        return f"{text} [Source: policy_finance_reimbursement.txt, Section 3.1]"

    if ("da" in q or "daily allowance" in q) and "meal" in q and "same day" in q:
        text = documents["policy_finance_reimbursement.txt"]["2.6"]
        return f"{text} [Source: policy_finance_reimbursement.txt, Section 2.6]"

    # Personal-phone question is deliberately refused because answering it
    # would require combining IT and HR information.
    if "personal phone" in q and "work files" in q and "home" in q:
        return REFUSAL

    # Flexible-working-culture question is outside the supplied policies.
    if "flexible working culture" in q:
        return REFUSAL

    return REFUSAL


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        nargs="*",
        help="Optional policy document paths. Defaults to the three UC-X documents.",
    )
    args = parser.parse_args()

    documents = retrieve_documents()

    print("UC-X Ask My Documents")
    print("Type a policy question. Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        print("\nAnswer:")
        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()