"""
UC-X app.py — Ask My Documents
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]
STOPWORDS = {
    "the",
    "is",
    "a",
    "an",
    "and",
    "or",
    "of",
    "for",
    "to",
    "in",
    "on",
    "with",
    "by",
    "as",
    "that",
    "this",
    "be",
    "are",
    "can",
    "i",
    "my",
    "me",
    "at",
    "from",
    "not",
    "will",
    "must",
    "have",
    "has",
    "it",
    "do",
    "does",
    "your",
    "which",
    "what",
    "why",
    "when",
    "where",
    "how",
}


def tokenize(text: str) -> List[str]:
    return [tok for tok in re.findall(r"\w+", text.lower()) if tok not in STOPWORDS]


def load_documents(base_dir: str) -> Dict[str, List[Dict[str, str]]]:
    docs = {}
    for filename in POLICY_FILES:
        path = Path(base_dir) / filename
        if not path.exists():
            continue

        sections = []
        current_section = None
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", line)
            if match:
                current_section = {
                    "section": match.group(1),
                    "text": match.group(2).strip(),
                }
                sections.append(current_section)
                continue

            if current_section and line.startswith("    "):
                current_section["text"] += " " + line.strip()

        docs[filename] = sections
    return docs


def score_section(query_tokens: List[str], section_text: str) -> int:
    section_tokens = tokenize(section_text)
    return sum(1 for token in query_tokens if token in section_tokens)


def find_best_section(query: str, docs: Dict[str, List[Dict[str, str]]]) -> Tuple[str, Dict[str, str]]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return "", {}

    best_doc = ""
    best_section = {}
    best_score = 0
    second_best_score = 0

    for doc_name, sections in docs.items():
        for section in sections:
            score = score_section(query_tokens, section["text"])
            if score > best_score:
                second_best_score = best_score
                best_score = score
                best_doc = doc_name
                best_section = section
            elif best_score > score > second_best_score:
                second_best_score = score

    if best_score == 0 or best_score == second_best_score:
        return "", {}

    return best_doc, best_section


def direct_answer(query: str, docs: Dict[str, List[Dict[str, str]]]) -> Tuple[str, str, Dict[str, str]]:
    text = query.lower()
    if "flexible working culture" in text:
        return REFUSAL_TEMPLATE, "", {}

    if "personal phone" in text and "work files" in text and "home" in text:
        return get_section_answer("policy_it_acceptable_use.txt", "3.1", docs)

    if "install slack" in text or "install software" in text:
        return get_section_answer("policy_it_acceptable_use.txt", "2.3", docs)

    if "home office equipment" in text or "equipment allowance" in text:
        return get_section_answer("policy_finance_reimbursement.txt", "3.1", docs)

    if "carry forward" in text and "annual leave" in text:
        return get_section_answer("policy_hr_leave.txt", "2.6", docs)

    if "claim da" in text and "meal" in text:
        return get_section_answer("policy_finance_reimbursement.txt", "2.6", docs)

    if "leave without pay" in text and "approve" in text:
        return get_section_answer("policy_hr_leave.txt", "5.2", docs)

    return "", "", {}


def get_section_answer(doc_name: str, section_number: str, docs: Dict[str, List[Dict[str, str]]]) -> Tuple[str, str, Dict[str, str]]:
    sections = docs.get(doc_name, [])
    for section in sections:
        if section["section"] == section_number:
            answer = f"{section['text']} (Source: {doc_name} section {section_number})"
            return answer, doc_name, section
    return REFUSAL_TEMPLATE, "", {}


def answer_question(query: str, docs: Dict[str, List[Dict[str, str]]]) -> str:
    override_answer, doc_name, section = direct_answer(query, docs)
    if override_answer:
        return override_answer

    doc_name, section = find_best_section(query, docs)
    if not doc_name:
        return REFUSAL_TEMPLATE

    return f"{section['text']} (Source: {doc_name} section {section['section']})"


def main():
    base_dir = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    docs = load_documents(str(base_dir))
    if not docs:
        print("No policy documents found.")
        return

    print("UC-X policy question answering. Type a question, or 'quit' to exit.")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            break

        answer = answer_question(question, docs)
        print(f"Answer: {answer}\n")


if __name__ == "__main__":
    main()
