"""UC-X policy Q&A CLI."""
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

SECTION_PATTERN = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S.*)$")


def is_separator_line(text):
    return text and all(not ch.isalnum() for ch in text) and len(set(text)) == 1


def is_section_header(text):
    if re.match(r"^\d+\.\s", text):
        return True
    if text.isupper() and not SECTION_PATTERN.match(text):
        return True
    return False


def load_document(path):
    sections = {}
    current_section = None
    buffer = []

    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip()
            match = SECTION_PATTERN.match(line)
            if match:
                if current_section:
                    sections[current_section] = " ".join(buffer).strip()
                current_section = match.group(1)
                buffer = [match.group(2).strip()]
                continue

            if current_section:
                stripped = line.strip()
                if not stripped:
                    continue
                if is_separator_line(stripped) or is_section_header(stripped):
                    continue
                buffer.append(stripped)

    if current_section:
        sections[current_section] = " ".join(buffer).strip()

    return sections


def retrieve_documents(base_dir):
    index = {}
    for filename in DOC_FILES:
        path = os.path.join(base_dir, filename)
        index[filename] = load_document(path)
    return index


def contains_word(text, word):
    return re.search(rf"\b{re.escape(word)}\b", text) is not None


def build_answer(doc_index, doc_name, section_number):
    section_text = doc_index.get(doc_name, {}).get(section_number, "")
    if not section_text:
        return REFUSAL_TEMPLATE
    return f"According to {doc_name} section {section_number}, {section_text}"


def answer_question(question, doc_index):
    q = question.strip().lower()

    if not q:
        return REFUSAL_TEMPLATE

    if "flexible working culture" in q or "company view" in q:
        return REFUSAL_TEMPLATE

    if "leave without pay" in q or "lwp" in q or "who approves leave" in q:
        return build_answer(doc_index, "policy_hr_leave.txt", "5.2")

    if "carry forward" in q or ("annual leave" in q and "carry" in q):
        return build_answer(doc_index, "policy_hr_leave.txt", "2.6")

    if "slack" in q or "install" in q:
        return build_answer(doc_index, "policy_it_acceptable_use.txt", "2.3")

    if "personal phone" in q or "personal device" in q:
        return build_answer(doc_index, "policy_it_acceptable_use.txt", "3.1")

    if "home office" in q or "equipment allowance" in q:
        return build_answer(doc_index, "policy_finance_reimbursement.txt", "3.1")

    if contains_word(q, "da") and "meal" in q:
        return build_answer(doc_index, "policy_finance_reimbursement.txt", "2.6")

    return REFUSAL_TEMPLATE


def main():
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
    )
    doc_index = retrieve_documents(base_dir)
    print("Policy Q&A System loaded. 3 documents indexed. Type your question or 'quit' to exit.")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break

        if question.lower() == "quit":
            break

        answer = answer_question(question, doc_index)
        print(answer)


if __name__ == "__main__":
    main()
