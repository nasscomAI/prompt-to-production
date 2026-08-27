"""UC-X Policy Question Answering CLI.

Loads three policy documents and answers questions based on keyword rules,
citing the exact document and section.

Usage:
  python app.py
  Enter questions, type 'exit' to quit.
"""

import os
import re


# Keyword rules: list of (keywords_list, doc_name, section)
KEYWORD_RULES = [
    (["slack", "install software", "install app", "install program"], "policy_it_acceptable_use.txt", "2.3"),
    (["personal phone", "personal device", "byod", "own phone"], "policy_it_acceptable_use.txt", "3.1"),
    (["carry forward leave", "unused annual leave"], "policy_hr_leave.txt", "2.6"),
    (["leave without pay", "lwp approval"], "policy_hr_leave.txt", "5.2"),
    (["home office equipment", "wfh allowance"], "policy_finance_reimbursement.txt", "3.1"),
    (["da and meal receipts", "claim da and meal"], "policy_finance_reimbursement.txt", "2.6"),
]

DOC_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)


def extract_sections(text: str) -> dict[str, str]:
    """Extract numbered sections from a policy text.

    Returns a dict mapping section number (e.g. "2.3") to the full section text.
    """
    sections: dict[str, str] = {}

    current_number = None
    current_lines: list[str] = []

    for line in text.splitlines():
        line = line.rstrip("\n")
        m = re.match(r"^(\d+\.\d+)\s+(.*)$", line.strip())
        if m:
            # Finish previous section
            if current_number is not None:
                sections[current_number] = " ".join(l.strip() for l in current_lines).strip()
            current_number = m.group(1)
            section_body = m.group(2).strip()
            current_lines = [section_body] if section_body else []
        else:
            # Continue current section if we are within one
            if current_number is not None:
                stripped = line.strip()
                # Ignore section separators and headers (e.g. "═══" or "3. SICK LEAVE").
                # Skip lines with no alphanumeric characters.
                if not stripped or not any(c.isalnum() for c in stripped):
                    continue
                if re.match(r"^\d+\.\s+", stripped):
                    # A numbered section header (like "3. SICK LEAVE") indicates the
                    # current section has ended, but isn't itself a section we need.
                    if current_number is not None:
                        sections[current_number] = " ".join(l.strip() for l in current_lines).strip()
                    current_number = None
                    current_lines = []
                    continue
                current_lines.append(stripped)

    # Final section
    if current_number is not None:
        sections[current_number] = " ".join(l.strip() for l in current_lines).strip()

    return sections


def load_documents() -> dict[str, dict[str, str]]:
    """Load and index the three policy documents."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data", "policy-documents")
    
    index: dict[str, dict[str, str]] = {}
    for doc_name in DOC_NAMES:
        doc_path = os.path.join(data_dir, doc_name)
        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                text = f.read()
            sections = extract_sections(text)
            index[doc_name] = sections
        except Exception as e:
            raise SystemExit(f"Error loading {doc_path}: {e}")
    return index


def answer_question(question: str, index: dict[str, dict[str, str]]) -> str:
    """Answer a question using keyword rules."""
    question_lower = question.lower()
    for keywords, doc, section in KEYWORD_RULES:
        for kw in keywords:
            if kw in question_lower:
                if doc in index and section in index[doc]:
                    text = index[doc][section]
                    return f"Source: {doc}, Section {section}\n{text}"
                else:
                    # If section not found, treat as not covered
                    break
    return REFUSAL_TEMPLATE


def main():
    print("Policy Question Answering System")
    print("Available documents: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("Type 'exit' to quit.\n")

    index = load_documents()

    while True:
        try:
            question = input("Enter your question: ").strip()
            if question.lower() == "exit":
                print("Goodbye!")
                break
            if not question:
                continue
            answer = answer_question(question, index)
            print(answer)
            print()  # Blank line for readability
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
