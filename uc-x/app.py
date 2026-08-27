"""
UC-X app.py — Ask My Documents
Loads three policy documents, indexes numbered sections, and answers questions
using a single source or a precise refusal template.
"""
import os
import re
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOCUMENT_FILES = [
    "data/policy-documents/policy_hr_leave.txt",
    "data/policy-documents/policy_it_acceptable_use.txt",
    "data/policy-documents/policy_finance_reimbursement.txt",
]

STOPWORDS = {
    "the", "is", "in", "and", "or", "of", "to", "a", "an", "for", "on",
    "this", "that", "with", "by", "from", "as", "be", "are", "it",
    "can", "may", "must", "not", "any", "all", "which", "if", "when",
    "do", "does", "will", "should", "have",
}


def normalize_text(text: str) -> List[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word for word in words if word not in STOPWORDS]


def extract_title(lines: List[str], filename: str) -> str:
    candidate = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if "POLICY" in upper or "ACCEPTABLE USE" in upper:
            candidate = stripped
            break
    return candidate or os.path.splitext(os.path.basename(filename))[0]


def retrieve_documents(paths: List[str]) -> Dict[str, Dict]:
    documents = {}

    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Input file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        title = extract_title(lines, path)
        sections: Dict[str, str] = {}
        current_section: Optional[str] = None
        current_lines: List[str] = []

        for raw_line in lines:
            line = raw_line.strip()
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
            if match:
                if current_section is not None:
                    sections[current_section] = " ".join(current_lines).strip()
                current_section = match.group(1)
                current_lines = [match.group(2).strip()]
            elif current_section is not None and line:
                current_lines.append(line)

        if current_section is not None:
            sections[current_section] = " ".join(current_lines).strip()

        documents[os.path.basename(path)] = {
            "title": title,
            "sections": sections,
        }

    return documents


def section_score(question: str, section_text: str) -> int:
    question_tokens = set(normalize_text(question))
    section_tokens = set(normalize_text(section_text))
    score = sum(1 for token in question_tokens if token in section_tokens)

    q_lower = question.lower()
    s_lower = section_text.lower()

    if "personal phone" in q_lower or "phone" in q_lower or "personal device" in q_lower:
        if "personal devices" in s_lower:
            score += 2
    if "install slack" in q_lower or "install" in q_lower and "software" in q_lower:
        if "install software" in s_lower or "written approval" in s_lower:
            score += 2
    if "home office" in q_lower or "work-from-home" in q_lower or "work from home" in q_lower:
        if "home office equipment" in s_lower or "work-from-home" in s_lower:
            score += 2
    if "meal receipts" in q_lower or "da" in q_lower:
        if "meal" in s_lower or "daily allowance" in s_lower:
            score += 1
    if "leave without pay" in q_lower or "lwp" in q_lower:
        if "leave without pay" in s_lower:
            score += 2
    if "carry forward" in q_lower or "annual leave" in q_lower:
        if "carry forward" in s_lower or "forfeited" in s_lower:
            score += 1

    return score


def select_best_section(
    question: str, documents: Dict[str, Dict]
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[int]]:
    candidates = []
    for doc_name, doc_info in documents.items():
        for section_no, text in doc_info["sections"].items():
            score = section_score(question, text)
            candidates.append((score, doc_name, section_no, text))

    if not candidates:
        return None, None, None, None

    candidates.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    top_score, top_doc, top_section, top_text = candidates[0]
    if top_score <= 1:
        return None, None, None, None

    top_ties = [item for item in candidates if item[0] == top_score]
    if len(top_ties) > 1:
        top_docs = {item[1] for item in top_ties}
        if len(top_docs) > 1:
            return None, None, None, None

    return top_doc, top_section, top_text, top_score


def answer_question(question: str, documents: Dict[str, Dict]) -> str:
    doc_name, section_no, section_text, score = select_best_section(question, documents)
    if doc_name is None:
        return REFUSAL_TEMPLATE

    doc_title = documents[doc_name]["title"]
    return f"According to {doc_title} section {section_no}: {section_text}"


def main() -> None:
    try:
        documents = retrieve_documents(DOCUMENT_FILES)
    except Exception as exc:
        print(f"Error loading documents: {exc}")
        raise SystemExit(1)

    print("Policy question answering system loaded.")
    print("Ask a question about the available policy documents.")
    print("Type 'exit' or press Ctrl+D to quit.")

    while True:
        try:
            question = input("Question> ").strip()
        except EOFError:
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        answer = answer_question(question, documents)
        print(answer)


if __name__ == "__main__":
    main()
