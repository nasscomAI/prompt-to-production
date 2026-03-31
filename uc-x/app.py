"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import re
from pathlib import Path


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "can",
    "for",
    "from",
    "home",
    "i",
    "in",
    "is",
    "my",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "who",
    "with",
    "work",
}


def _tokenize(text: str) -> set:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and token not in STOPWORDS
    }


def _read_document(path: Path) -> list:
    lines = path.read_text(encoding="utf-8").splitlines()
    clauses = []
    current = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or set(line) == {"═"}:
            continue

        match = CLAUSE_RE.match(line)
        if match:
            if current is not None:
                clauses.append(current)
            current = {"section": match.group(1), "text": match.group(2).strip()}
        elif current is not None:
            current["text"] = f"{current['text']} {line}".strip()

    if current is not None:
        clauses.append(current)

    return clauses


def retrieve_documents(base_dir: Path) -> dict:
    """
    Load all policy documents and index them by filename with parsed clauses.
    """
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]
    doc_index = {}
    for filename in files:
        path = base_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing required policy file: {filename}")
        doc_index[filename] = _read_document(path)

    return doc_index


def _score_clause(question_tokens: set, clause_text: str) -> int:
    clause_tokens = _tokenize(clause_text)
    overlap = question_tokens & clause_tokens
    score = len(overlap)

    lowered = clause_text.lower()
    if "cannot" in lowered or "must not" in lowered or "not permitted" in lowered:
        if {"can", "allowed", "permit", "use", "claim"} & question_tokens:
            score += 1

    return score


def answer_question(documents: dict, question: str) -> str:
    """
    Return a single-source, cited answer or the exact refusal template.
    """
    question = (question or "").strip()
    if not question:
        return REFUSAL_TEMPLATE

    q_tokens = _tokenize(question)
    if not q_tokens:
        return REFUSAL_TEMPLATE

    ranked_by_doc = {}
    for doc_name, clauses in documents.items():
        ranked = []
        for clause in clauses:
            score = _score_clause(q_tokens, clause["text"])
            if score > 0:
                ranked.append((score, clause))
        ranked.sort(key=lambda item: item[0], reverse=True)
        ranked_by_doc[doc_name] = ranked

    doc_scores = []
    for doc_name, ranked in ranked_by_doc.items():
        best = ranked[0][0] if ranked else 0
        doc_scores.append((best, doc_name))
    doc_scores.sort(reverse=True)

    best_score, best_doc = doc_scores[0]
    second_score, _ = doc_scores[1]

    if best_score == 0:
        return REFUSAL_TEMPLATE

    # Refuse when top relevance is effectively split across documents.
    if second_score > 0 and best_score - second_score <= 1:
        return REFUSAL_TEMPLATE

    top_clauses = ranked_by_doc[best_doc][:2]
    lines = []
    for _, clause in top_clauses:
        lines.append(f"{best_doc} section {clause['section']}: {clause['text']}")
    return "\n".join(lines)

def main():
    base_dir = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    documents = retrieve_documents(base_dir)

    print("UC-X Policy Q&A CLI")
    print("Ask a question, or type 'exit' to quit.")

    while True:
        question = input("\nQ> ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        print(answer_question(documents, question))

if __name__ == "__main__":
    main()
