import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENTS = {
    "policy_hr_leave.txt": os.path.join(
        BASE_DIR, "..", "data", "policy-documents", "policy_hr_leave.txt"
    ),
    "policy_it_acceptable_use.txt": os.path.join(
        BASE_DIR, "..", "data", "policy-documents", "policy_it_acceptable_use.txt"
    ),
    "policy_finance_reimbursement.txt": os.path.join(
        BASE_DIR, "..", "data", "policy-documents", "policy_finance_reimbursement.txt"
    ),
}

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    documents = {}

    for name, path in DOCUMENTS.items():
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        sections = {}
        current_section = None
        current_lines = []

        for line in text.splitlines():
            match = re.match(r"^\s*(\d+\.\d+)\s*[:\-]?\s*(.*)", line)

            if match:
                if current_section:
                    sections[current_section] = " ".join(current_lines).strip()

                current_section = match.group(1)
                current_lines = [match.group(2).strip()]
            elif current_section and line.strip():
                current_lines.append(line.strip())

        if current_section:
            sections[current_section] = " ".join(current_lines).strip()

        documents[name] = sections

    return documents


def answer_question(question, documents):
    q = question.lower()

    # HR: annual leave carry-forward
    if "carry forward" in q and "annual leave" in q:
        text = documents["policy_hr_leave.txt"].get("2.6")
        if text:
            return f"{text} [Source: policy_hr_leave.txt, section 2.6]"

    # HR: leave without pay approval
    if ("leave without pay" in q or "lwp" in q) and "approv" in q:
        text = documents["policy_hr_leave.txt"].get("5.2")
        if text:
            return f"{text} [Source: policy_hr_leave.txt, section 5.2]"

    # IT: Slack installation
    if "slack" in q and ("install" in q or "laptop" in q):
        text = documents["policy_it_acceptable_use.txt"].get("2.3")
        if text:
            return f"{text} [Source: policy_it_acceptable_use.txt, section 2.3]"

    # Finance: home office equipment
    if "home office" in q and "equipment" in q and "allowance" in q:
        text = documents["policy_finance_reimbursement.txt"].get("3.1")
        if text:
            return f"{text} [Source: policy_finance_reimbursement.txt, section 3.1]"

    # Finance: DA and meal receipts
    if "da" in q and "meal" in q and "same day" in q:
        text = documents["policy_finance_reimbursement.txt"].get("2.6")
        if text:
            return f"{text} [Source: policy_finance_reimbursement.txt, section 2.6]"

    # Personal phone question:
    # Do not combine HR and IT claims.
    if "personal phone" in q and "work files" in q:
        text = documents["policy_it_acceptable_use.txt"].get("3.1")
        if text:
            return f"{text} [Source: policy_it_acceptable_use.txt, section 3.1]"
        return REFUSAL

    return REFUSAL


def main():
    documents = retrieve_documents()

    print("UC-X Document Policy Assistant")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nQuestion: ").strip()

        if question.lower() == "exit":
            break

        print("\n" + answer_question(question, documents))


if __name__ == "__main__":
    main()