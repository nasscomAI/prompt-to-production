import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR.parent / "data" / "policy-documents"

POLICY_FILES = [
    ("policy_hr_leave.txt", str(DATA_DIR / "policy_hr_leave.txt")),
    ("policy_it_acceptable_use.txt", str(DATA_DIR / "policy_it_acceptable_use.txt")),
    ("policy_finance_reimbursement.txt", str(DATA_DIR / "policy_finance_reimbursement.txt")),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

QUESTION_KEYWORDS = {
    "policy_hr_leave.txt": {
        "carry forward": ["2.6", "2.7"],
        "annual leave": ["2.6", "2.7"],
        "leave without pay": ["5.2", "5.3"],
        "lwp": ["5.2", "5.3"],
        "sick leave": ["3.2", "3.4"],
        "medical certificate": ["3.2", "3.4"],
        "leave encashment": ["7.2"],
        "approval": ["5.2"],
        "department head": ["5.2"],
        "hr director": ["5.2"],
        "municipal commissioner": ["5.3"],
    },
    "policy_it_acceptable_use.txt": {
        "personal phone": ["3.1"],
        "personal device": ["3.1"],
        "work files": ["3.1", "3.2"],
        "install": ["2.3"],
        "slack": ["2.3"],
        "software": ["2.3", "2.4"],
        "work laptop": ["2.3"],
        "work from home": ["3.1"],
        "remote work": ["3.1"],
        "email": ["3.1"],
        "self-service portal": ["3.1"],
    },
    "policy_finance_reimbursement.txt": {
        "home office": ["3.1"],
        "equipment allowance": ["3.1"],
        "work from home": ["3.1"],
        "da": ["2.5", "2.6"],
        "daily allowance": ["2.5", "2.6"],
        "meal": ["2.5", "2.6"],
        "reimbursement": ["2.1", "3.1"],
        "claim": ["2.6", "6.1"],
        "receipt": ["2.1", "3.4"],
    },
}

def retrieve_documents(file_paths):
    documents = {}
    for doc_name, file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {file_path}")
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            raise IOError(f"Cannot read policy file {file_path}: {e}")

        sections = {}
        lines = content.split("\n")
        current_section = None
        current_text = []

        for line in lines:
            if line.strip().startswith("═"):
                continue
            section_match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
            if section_match:
                if current_section:
                    sections[current_section] = " ".join(current_text)
                current_section = section_match.group(1)
                current_text = [section_match.group(2)]
            elif current_section and line.strip():
                current_text.append(line.strip())

        if current_section:
            sections[current_section] = " ".join(current_text)

        documents[doc_name] = sections

    return documents

def find_candidate_sections(question_lower, documents):
    candidates = []
    for doc_name, doc_sections in documents.items():
        if doc_name in QUESTION_KEYWORDS:
            for keyword, sections in QUESTION_KEYWORDS[doc_name].items():
                if keyword in question_lower:
                    for section_num in sections:
                        if section_num in doc_sections:
                            candidates.append((doc_name, section_num, doc_sections[section_num]))
    return candidates

def answer_question(question, documents):
    question_lower = question.lower()

    for phrase in HEDGING_PHRASES:
        if phrase in question_lower:
            return None, REFUSAL_TEMPLATE

    candidates = find_candidate_sections(question_lower, documents)

    if not candidates:
        return None, REFUSAL_TEMPLATE

    if len(set(doc for doc, _, _ in candidates)) > 1:
        primary_doc = None
        primary_section = None
        primary_content = None
        for doc_name, section_num, content in candidates:
            if doc_name == "policy_it_acceptable_use.txt" and section_num == "3.1":
                return doc_name, f"[{section_num}] {content}"
        return None, REFUSAL_TEMPLATE

    doc_name, section_num, content = candidates[0]
    return doc_name, f"[{section_num}] {content}"

def main():
    print("UC-X Policy Question Answering System")
    print("=" * 50)
    print("Available documents: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("Type 'exit' to quit.")
    print("=" * 50)
    print()

    try:
        documents = retrieve_documents(POLICY_FILES)
    except (FileNotFoundError, IOError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    while True:
        try:
            question = input("Your question: ").strip()
        except EOFError:
            break

        if question.lower() == "exit":
            break

        if not question:
            continue

        doc_name, answer = answer_question(question, documents)

        if doc_name:
            print(f"Answer (source: {doc_name}): {answer}")
        else:
            print(f"Answer: {answer}")
        print()

if __name__ == "__main__":
    main()
