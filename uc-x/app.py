"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import string

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = [
    '../data/policy-documents/policy_hr_leave.txt',
    '../data/policy-documents/policy_it_acceptable_use.txt',
    '../data/policy-documents/policy_finance_reimbursement.txt',
]

SECTION_PATTERN = re.compile(r'^(\d+\.\d+)\s+(.*)$')


def preprocess(text):
    # Lowercase, remove punctuation, split into keywords
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return set(text.split())


def retrieve_documents(paths):
    docs = {}
    for path in paths:
        doc_name = os.path.basename(path)
        docs[doc_name] = {}
        try:
            with open(path, encoding='utf-8') as f:
                current_section = None
                for line in f:
                    m = SECTION_PATTERN.match(line.strip())
                    if m:
                        current_section = m.group(1)
                        docs[doc_name][current_section] = m.group(2).strip()
                    elif current_section and line.strip():
                        docs[doc_name][current_section] += ' ' + line.strip()
        except Exception as e:
            print(f"Error loading {path}: {e}")
    return docs


def answer_question(question, docs):
    q_keywords = preprocess(question)
    best_match = None
    best_score = 0
    best_doc = None
    best_sec = None
    best_text = None
    for doc_name, sections in docs.items():
        for sec, text in sections.items():
            sec_keywords = preprocess(text)
            overlap = len(q_keywords & sec_keywords)
            if overlap > best_score:
                best_score = overlap
                best_match = (doc_name, sec, text)
    # Require at least one keyword overlap for a match
    if best_match and best_score > 0:
        doc, sec, text = best_match
        return f"{text}\n(Source: {doc} section {sec})"
    return REFUSAL_TEMPLATE


def main():
    print("UC-X Policy Q&A — Ask a question or type 'exit' to quit.")
    docs = retrieve_documents(DOC_PATHS)
    while True:
        question = input("\n> ").strip()
        if question.lower() in ("exit", "quit"): break
        if not question:
            print("Please enter a question.")
            continue
        answer = answer_question(question, docs)
        print(f"\n{answer}")

if __name__ == "__main__":
    main()


