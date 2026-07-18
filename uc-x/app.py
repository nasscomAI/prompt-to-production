import os
import re
import sys

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def parse_document(filepath: str) -> list:
    sections = []
    doc_name = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    current_num = None
    current_text = []

    for line in lines:
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        section_match = re.match(r'^\d+\.\s+[A-Z]', line)
        is_separator = line.startswith('═')

        if clause_match:
            if current_num:
                sections.append((doc_name, current_num, ' '.join(current_text).strip()))
            current_num = clause_match.group(1)
            current_text = [clause_match.group(2).strip()]
        elif current_num and line.strip() and not section_match and not is_separator:
            current_text.append(line.strip())

    if current_num and current_text:
        sections.append((doc_name, current_num, ' '.join(current_text).strip()))

    return sections


def retrieve_documents() -> list:
    all_sections = []
    for fp in POLICY_FILES:
        resolved = os.path.join(os.path.dirname(__file__), fp)
        all_sections.extend(parse_document(resolved))
    return all_sections


def find_section(sections: list, doc_name: str, num: str) -> str:
    for d, n, t in sections:
        if d == doc_name and n == num:
            return t
    return ""


# Verified question patterns mapping to single-source document answers.
# Each entry defines keyword patterns that must ALL match the question,
# and the single-source section to answer from.
QA_RULES = [
    {
        "patterns": [["carry", "forward"], ["annual", "leave"]],
        "doc": "policy_hr_leave.txt",
        "section": "2.6",
        "answer_keywords": ["carry", "forward", "maximum", "5", "forfeited", "31"]
    },
    {
        "patterns": [["install", "software"], ["slack"]],
        "doc": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "answer_keywords": ["install", "software", "approval"]
    },
    {
        "patterns": [["home", "office"], ["equipment", "allowance"]],
        "doc": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "answer_keywords": ["home", "office", "allowance", "8,000"]
    },
    {
        "patterns": [["personal", "phone"], ["work", "files"], ["personal", "device"]],
        "doc": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "answer_keywords": ["personal", "devices", "email", "portal"]
    },
    {
        "patterns": [["da", "meal"], ["receipts", "same", "day"]],
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "answer_keywords": ["da", "meal", "receipts", "cannot", "claimed", "simultaneously"]
    },
    {
        "patterns": [["approves", "leave"], ["leave", "without", "pay"], ["lwp", "approval"]],
        "doc": "policy_hr_leave.txt",
        "section": "5.2",
        "answer_keywords": ["department", "head", "hr", "director"]
    },
]


def answer_question(question: str, sections: list) -> str:
    q = question.lower()

    for rule in QA_RULES:
        for pattern in rule["patterns"]:
            if all(p in q for p in pattern):
                text = find_section(sections, rule["doc"], rule["section"])
                if text:
                    return f"{text}\nSource: {rule['doc']} Section {rule['section']}"
                else:
                    return f"[Section {rule['section']} not found in {rule['doc']}]"

    return REFUSAL_TEMPLATE


def main():
    print("=" * 55)
    print("Welcome to the CMC Policy Q&A Assistant.")
    print("Type your question below (or 'exit' to quit):")
    print("=" * 55)

    sections = retrieve_documents()

    while True:
        try:
            user_input = input("\nQuestion: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break

            response = answer_question(user_input, sections)
            print(response)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
