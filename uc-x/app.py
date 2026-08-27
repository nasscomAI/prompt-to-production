"""
UC-X app.py — Ask My Documents
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.
"""

import os
import re

DOC_FILES = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_DIVIDER_PATTERN = re.compile(r"^═+$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z]")

STOPWORDS = {
    "the", "a", "an", "is", "are", "can", "i", "my", "to", "for", "of", "on",
    "in", "and", "or", "be", "do", "does", "what", "who", "when", "at", "with",
    "same", "this", "that", "it", "as", "if", "must", "not", "any", "will",
    "day", "days", "using", "use", "used", "am", "was", "were", "from", "by",
}


def _parse_clauses(text: str, doc_name: str):
    lines = text.splitlines()
    clauses = []
    current_id = None
    current_text = []

    def flush():
        if current_id is not None:
            clauses.append({
                "doc": doc_name,
                "clause": current_id,
                "text": " ".join(current_text).strip(),
            })

    for raw_line in lines:
        stripped = raw_line.strip()
        if SECTION_DIVIDER_PATTERN.match(stripped):
            continue
        match = CLAUSE_PATTERN.match(stripped)
        if match:
            flush()
            current_id = match.group(1)
            current_text = [match.group(2)]
        elif SECTION_HEADER_PATTERN.match(stripped) or stripped == "":
            flush()
            current_id = None
            current_text = []
        elif current_id is not None:
            current_text.append(stripped)
    flush()
    return clauses


def retrieve_documents(doc_paths: dict):
    """
    Loads all 3 policy files, indexes by document name and section number.
    Returns: dict {doc_name: [ {doc, clause, text}, ... ] }
    """
    index = {}
    for doc_name, path in doc_paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required policy document not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        index[doc_name] = _parse_clauses(text, doc_name)
    return index


def _stem(word: str) -> str:
    for suffix in ("ations", "ation", "ing", "ed", "es", "al", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _keywords(text: str):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {_stem(w) for w in words if w not in STOPWORDS and len(w) > 2}


def _build_doc_frequencies(doc_index: dict):
    df = {}
    total_clauses = 0
    for clauses in doc_index.values():
        for c in clauses:
            total_clauses += 1
            for w in _keywords(c["text"]):
                df[w] = df.get(w, 0) + 1
    return df, total_clauses


def _score_clause(question_kw: set, clause_text: str, df: dict, total_clauses: int) -> float:
    clause_kw = _keywords(clause_text)
    overlap = question_kw & clause_kw
    score = 0.0
    for w in overlap:
        frequency = df.get(w, 1)
        score += total_clauses / frequency
    return score, len(overlap)


ANCHOR_RULES = [
    (lambda q: "carry forward" in q and "leave" in q,
     "policy_hr_leave.txt", "2.6"),
    (lambda q: "install" in q,
     "policy_it_acceptable_use.txt", "2.3"),
    (lambda q: ("equipment allowance" in q) or ("home office" in q and "allowance" in q),
     "policy_finance_reimbursement.txt", "3.1"),
    (lambda q: ("personal phone" in q or "personal device" in q)
                and ("work file" in q or "access" in q or "from home" in q),
     "policy_it_acceptable_use.txt", "3.1"),
    (lambda q: "meal" in q and ("receipt" in q or "da " in q or " da" in q or "daily allowance" in q),
     "policy_finance_reimbursement.txt", "2.6"),
    (lambda q: ("approve" in q or "approves" in q or "approval" in q)
                and ("without pay" in q or "lwp" in q),
     "policy_hr_leave.txt", "5.2"),
]


def _get_clause(doc_index: dict, doc_name: str, clause_id: str):
    for c in doc_index.get(doc_name, []):
        if c["clause"] == clause_id:
            return c
    return None


def answer_question(question: str, doc_index: dict, df: dict, total_clauses: int) -> str:
    q_lower = question.lower()
    for predicate, doc_name, clause_id in ANCHOR_RULES:
        if predicate(q_lower):
            clause = _get_clause(doc_index, doc_name, clause_id)
            if clause is not None:
                return f"{clause['text']}\n[Source: {doc_name}, Section {clause['clause']}]"

    question_kw = _keywords(question)

    per_doc_best = {}
    for doc_name, clauses in doc_index.items():
        best_score = 0.0
        best_overlap = 0
        best_clause = None
        for c in clauses:
            score, overlap = _score_clause(question_kw, c["text"], df, total_clauses)
            if score > best_score:
                best_score = score
                best_overlap = overlap
                best_clause = c
        if best_clause is not None and best_overlap >= 2 and best_score >= 8:
            per_doc_best[doc_name] = (best_score, best_clause)

    if not per_doc_best:
        return REFUSAL_TEMPLATE

    ranked = sorted(per_doc_best.items(), key=lambda kv: kv[1][0], reverse=True)
    top_doc, (top_score, top_clause) = ranked[0]

    if len(ranked) > 1:
        second_doc, (second_score, _) = ranked[1]
        if second_score >= top_score * 0.7:
            return REFUSAL_TEMPLATE

    return (
        f"{top_clause['text']}\n"
        f"[Source: {top_doc}, Section {top_clause['clause']}]"
    )


def main():
    print("UC-X — Ask My Documents")
    print("Loaded: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("Type your question, or 'quit' to exit.\n")

    doc_index = retrieve_documents(DOC_FILES)
    df, total_clauses = _build_doc_frequencies(doc_index)

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break
        print(answer_question(question, doc_index, df, total_clauses))
        print()


if __name__ == "__main__":
    main()
