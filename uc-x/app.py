"""
UC-X — Ask My Documents
Interactive CLI for policy question answering strictly from 3 policy documents.
Enforces single-source answers, mandatory citations, and exact refusal template.
"""
import os
import re
import sys

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {"can", "i", "my", "the", "a", "an", "is", "are", "on", "for",
             "to", "of", "in", "do", "and", "or", "what", "who", "when", "how"}


def retrieve_documents():
    """Load all 3 policy files. Report any that are missing."""
    docs = {}
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "policy-documents")
    for fname in POLICY_FILES:
        path = os.path.join(base, fname)
        if not os.path.exists(path):
            print(f"Warning: {fname} not found at {path}", file=sys.stderr)
            docs[fname] = ""
        else:
            with open(path, "r", encoding="utf-8") as f:
                docs[fname] = f.read()
    return docs


def index_sections(doc_text):
    """Index a document by section number -> full section text."""
    sections = {}
    matches = list(re.finditer(r'(\d+\.\d+)\b', doc_text))
    for i, m in enumerate(matches):
        sec_num = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(doc_text)
        sections[sec_num] = doc_text[start:end].strip()
    return sections


def answer_question(question, docs):
    """
    Find the best single-source answer by keyword scoring.
    Never blends across documents. Returns exact refusal template if not found.
    """
    if not question.strip():
        return REFUSAL_TEMPLATE

    q_words = [w for w in re.sub(r'[^a-z0-9 ]', '', question.lower()).split()
               if w not in STOPWORDS and len(w) > 2]

    best_score = 0
    best_answer = None

    for doc_name, text in docs.items():
        if not text:
            continue
        sections = index_sections(text)
        for sec_num, sec_text in sections.items():
            sec_lower = sec_text.lower()
            score = sum(1 for w in q_words if w in sec_lower)
            if score > best_score:
                best_score = score
                best_answer = (doc_name, sec_num, sec_text)

    # Require at least 2 keyword hits to avoid spurious matches
    if best_answer and best_score >= 2:
        doc_name, sec_num, sec_text = best_answer
        return f"{sec_text}\n\n[Source: {doc_name}, Section {sec_num}]"

    return REFUSAL_TEMPLATE


def main():
    docs = retrieve_documents()
    print("UC-X Policy Q&A — type your question or 'exit' to quit.\n")
    while True:
        try:
            q = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("exit", "quit", ""):
            break
        print(answer_question(q, docs))
        print()


if __name__ == "__main__":
    main()
