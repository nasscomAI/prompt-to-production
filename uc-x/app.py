"""
UC-X — Ask My Documents
"""
import argparse
import re
import sys
import io
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

POLICY_FILES = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard",
    "employees are generally",
    "in most cases",
]

STOP_WORDS = {"the", "and", "for", "can", "not", "from", "are", "may", "must", "with", "has", "its", "all", "any", "each", "per", "than", "that", "this", "what", "will", "been", "after", "also", "over", "use", "using", "used", "get", "got", "make", "made", "put", "set", "does", "doing", "done", "say", "said"}

ABBREV = {
    "lwp": "leave without pay",
    "lop": "loss of pay",
    "byod": "bring your own device personal device",
    "da": "daily allowance",
    "mfa": "multi factor authentication multi-factor authentication",
    "wfh": "work from home",
    "hr": "human resources",
    "it": "information technology",
    "cmc": "city municipal corporation",
    "approval": "approves approve approved approving",
    "paid": "pay pays",
}


def retrieve_documents(doc_paths: dict) -> dict:
    documents = {}
    for name, path in doc_paths.items():
        try:
            with open(path, encoding="utf-8") as f:
                documents[name] = f.read()
        except FileNotFoundError:
            print(f"Error: File not found \u2014 {path}")
            sys.exit(1)
    return documents


def _contains_hedging(text: str) -> bool:
    lower = text.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in lower:
            return True
    return False


def _query_words(question: str) -> set:
    return {w for w in re.findall(r"[a-z]{3,}", question.lower()) if w not in STOP_WORDS}


def _build_idf(q_words: set, all_doc_texts: dict) -> dict:
    idf = {}
    for w in q_words:
        doc_count = sum(1 for t in all_doc_texts.values() if w in t.lower())
        idf[w] = 1.0 if doc_count == 0 else 1.0 / doc_count
    return idf


def _score(q_words: set, section_text: str, idf: dict) -> tuple:
    lower = section_text.lower()
    score = 0.0
    matched = 0
    for w in q_words:
        if re.search(r"\b" + re.escape(w) + r"\b", lower):
            score += idf.get(w, 1.0)
            matched += 1
    return score, matched


def _expand(text: str) -> str:
    lower = text.lower()
    for abbr, expansion in ABBREV.items():
        if re.search(r"\b" + abbr + r"\b", lower):
            text += " " + expansion
    return text


def _all_clauses(text: str) -> list:
    return re.findall(r"^\d+\.\d+\s+.*(?:\n(?!\d+\.\d+|\d+\.\s+|═).*)*", text, re.MULTILINE)


def _best_clause(text: str, q_words: set, idf: dict) -> tuple:
    clauses = _all_clauses(text)
    best = ("", 0.0, 0)
    for c in clauses:
        expanded = _expand(c)
        score, matched = _score(q_words, expanded, idf)
        if score > best[1]:
            best = (c.strip(), score, matched)
    return best


def answer_question(question: str, documents: dict) -> str:
    if _contains_hedging(question):
        return REFUSAL_TEMPLATE

    q_words = _query_words(question)
    if len(q_words) < 2:
        return REFUSAL_TEMPLATE

    idf = _build_idf(q_words, documents)

    per_doc = []
    for doc_name, doc_text in documents.items():
        clause, score, matched = _best_clause(doc_text, q_words, idf)
        per_doc.append((score, matched, doc_name, clause))

    per_doc.sort(key=lambda x: (-x[0], -x[1]))
    best_score, best_matched, best_doc, best_clause = per_doc[0]

    if best_matched < 1:
        return REFUSAL_TEMPLATE

    if best_matched == 1:
        single_word = [w for w in q_words if w in best_clause.lower()][0]
        if single_word in idf and idf[single_word] <= 0.5:
            return REFUSAL_TEMPLATE

    others = [(s, m, d) for s, m, d, _ in per_doc[1:] if d != best_doc]
    for s, m, d in others:
        if s >= best_score * 0.5 and m >= best_matched - 1:
            return REFUSAL_TEMPLATE

    clause_id = re.search(r"(\d+\.\d+)", best_clause)
    cite = clause_id.group(1) if clause_id else "section"

    return f"[Source: {best_doc} \u2014 {cite}]\n{best_clause}"


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--doc-dir", default="../data/policy-documents")
    args = parser.parse_args()

    documents = retrieve_documents(POLICY_FILES)

    print("=" * 60)
    print("UC-X \u2014 Ask My Documents")
    print("Type your question or 'quit' to exit.")
    print("=" * 60)

    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            break

        answer = answer_question(question, documents)
        print(answer)


if __name__ == "__main__":
    main()
