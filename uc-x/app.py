
"""
UC-X — Ask My Documents
Interactive CLI that answers questions strictly from one of three policy
documents at a time, citing document + section, or refuses using the exact
required template when no single document answers cleanly. Implements the
two skills defined in skills.md: retrieve_documents, answer_question.
"""

import os
import re
import sys

DOCUMENT_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

SECTION_PATTERN = re.compile(r"^\s*(\d+\.\d+)\b[\.\)\s]*", re.MULTILINE)

STOPWORDS = {
    "the", "a", "an", "is", "are", "can", "i", "my", "to", "for", "of", "on",
    "in", "do", "does", "what", "who", "and", "or", "be", "use", "using",
    "from", "at", "with", "this", "that", "it", "as", "if", "not", "you",
    "your", "me", "when", "same", "day",
}


def retrieve_documents(paths):
    index = {}
    for name, path in paths.items():
        if not os.path.exists(path):
            print(f"ERROR: required document not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        matches = list(SECTION_PATTERN.finditer(text))
        sections = []
        if not matches:
            sections.append({"section_id": "0", "text": text.strip()})
        else:
            for i, m in enumerate(matches):
                section_id = m.group(1)
                start = m.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                sections.append({"section_id": section_id, "text": text[start:end].strip()})

        index[name] = sections

    return index

def _stem(word):
    for suffix in ("ing", "ed", "es", "al", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) > 3:
            word = word[: -len(suffix)]
            break
    if word.endswith("e") and len(word) > 4:
        word = word[:-1]
    return word

def _keywords(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {_stem(w) for w in words if w not in STOPWORDS and len(w) > 2}


def answer_question(question, index):
    q_keywords = _keywords(question)
    if not q_keywords:
        return {"answer": REFUSAL_TEMPLATE, "source_document": None, "section": None, "refused": True}

    # Score every section across every document by keyword overlap
    scored = []  # (score, doc_name, section_id, text)
    for doc_name, sections in index.items():
        for sec in sections:
            sec_keywords = _keywords(sec["text"])
            overlap = len(q_keywords & sec_keywords)
            if overlap > 0:
                scored.append((overlap, doc_name, sec["section_id"], sec["text"]))

    if not scored:
        return {"answer": REFUSAL_TEMPLATE, "source_document": None, "section": None, "refused": True}

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0]
    top_matches = [s for s in scored if s[0] == top_score]

    docs_involved = {m[1] for m in top_matches}

    if len(docs_involved) > 1:
        # Ambiguous across documents at the same relevance level — refuse
        # rather than blend, per the cross-document blending rule.
        return {"answer": REFUSAL_TEMPLATE, "source_document": None, "section": None, "refused": True}

    doc_name, section_id, text = top_matches[0][1], top_matches[0][2], top_matches[0][3]

    answer = f"Per {doc_name}, section {section_id}: {text}"
    return {"answer": answer, "source_document": doc_name, "section": section_id, "refused": False}


def main():
    index = retrieve_documents(DOCUMENT_PATHS)
    print("Policy Q&A — type your question, or 'quit' to exit.")
    print(f"Loaded documents: {', '.join(index.keys())}\n")

    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break

        result = answer_question(question, index)
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()