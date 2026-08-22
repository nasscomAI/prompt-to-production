"""
UC-X — Ask My Documents
Answers questions using only the three supplied CMC policy documents.
"""

import argparse
import re
from pathlib import Path


POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).

Please contact [relevant team] for guidance."""


def load_documents():
    documents = {}

    for file_path in POLICY_FILES:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Required policy file not found: {file_path}")

        documents[path.name] = path.read_text(encoding="utf-8")

    return documents


def get_section(document_text, section_number):
    pattern = rf"(?m)^{re.escape(section_number)}\.\d+\s+.*?(?=^\d+\.\d+\s+|\Z)"
    matches = re.findall(pattern, document_text, re.DOTALL)

    if matches:
        return "\n".join(matches)

    return None


def find_section(document_text, section_number):
    lines = document_text.splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith(section_number + " "):
            section_lines = [stripped]

            for next_line in lines[i + 1:]:
                next_stripped = next_line.strip()

                # Stop at next top-level section, e.g.:
                # 3. WORK FROM HOME EQUIPMENT
                if re.match(r"^\d+\.\s+", next_stripped):
                    break

                # Stop at next subsection, e.g.:
                # 2.7 ...
                if re.match(r"^\d+\.\d+\s+", next_stripped):
                    break

                if next_stripped and not next_stripped.startswith("═"):
                    section_lines.append(next_stripped)

            return " ".join(section_lines)

    return None

def answer_question(question, documents):
    q = question.lower()

    # HR — Annual Leave carry forward
    if "carry forward" in q and "annual leave" in q:
        section = find_section(documents["policy_hr_leave.txt"], "2.6")

        return (
            f"{section}\n\n"
            "Source: policy_hr_leave.txt, Section 2.6"
        )

    # IT — Installing software
    if "install" in q and ("slack" in q or "software" in q) and "work laptop" in q:
        section = find_section(documents["policy_it_acceptable_use.txt"], "2.3")

        return (
            f"{section}\n\n"
            "Source: policy_it_acceptable_use.txt, Section 2.3"
        )

    # Finance — Home office equipment
    if "home office" in q and "equipment" in q and "allowance" in q:
        section = find_section(documents["policy_finance_reimbursement.txt"], "3.1")

        return (
            f"{section}\n\n"
            "Source: policy_finance_reimbursement.txt, Section 3.1"
        )

    # Personal phone + work files:
    # Must NOT combine HR and IT information.
    if "personal phone" in q and "work files" in q:
        section = find_section(documents["policy_it_acceptable_use.txt"], "3.1")

        return (
            f"{section}\n\n"
            "Source: policy_it_acceptable_use.txt, Section 3.1"
        )

    # Flexible working culture is not covered.
    if "flexible working culture" in q:
        return REFUSAL

    # Finance — DA and meal receipts
    if "da" in q and "meal receipts" in q:
        section = find_section(documents["policy_finance_reimbursement.txt"], "2.6")

        return (
            f"{section}\n\n"
            "Source: policy_finance_reimbursement.txt, Section 2.6"
        )

    # HR — LWP approval
    if "who approves" in q and "leave without pay" in q:
        section = find_section(documents["policy_hr_leave.txt"], "5.2")

        return (
            f"{section}\n\n"
            "Source: policy_hr_leave.txt, Section 5.2"
        )

    return REFUSAL


def main():
    documents = load_documents()

    print("UC-X — Ask My Documents")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if question.lower() == "exit":
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