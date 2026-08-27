"""
UC-X app.py — Ask My Documents
Built per agents.md (RICE enforcement) and skills.md (retrieve_documents, answer_question).
"""
import re

SECTION_RE = re.compile(r"^(\d+)\.\s+(\S.*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")
SEPARATOR_RE = re.compile(r"^[═=]+$")

DOCUMENT_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {
    "the", "a", "an", "is", "are", "can", "i", "my", "to", "for", "of", "on",
    "in", "and", "or", "what", "who", "when", "where", "how", "does", "do",
    "this", "that", "be", "was", "were", "will", "with", "from", "at", "as",
    "me", "you", "your", "it", "if", "same",
}

# Abbreviations used in the source documents that a spelled-out question
# wouldn't otherwise match (e.g. clauses say "LWP", a question says
# "leave without pay").
ABBREVIATION_EXPANSIONS = {
    "lwp": ["leave", "without", "pay"],
    "da": ["daily", "allowance"],
}

_STEM_SUFFIXES = ("ations", "ation", "ing", "ions", "ion", "edly", "ally", "al", "ed", "es", "s")


def _stem(word: str) -> str:
    """Crude suffix-stripping so 'approves'/'approval'/'approved' collide."""
    for suffix in _STEM_SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _parse_policy_file(file_path: str) -> list:
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_section = None
    current_clause = None

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if not stripped or SEPARATOR_RE.match(stripped):
            continue

        section_match = SECTION_RE.match(stripped)
        clause_match = CLAUSE_RE.match(stripped)

        if section_match and not clause_match:
            current_section = {
                "section_number": section_match.group(1),
                "heading": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
            continue

        if clause_match and current_section is not None:
            current_clause = {
                "clause_number": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
            current_section["clauses"].append(current_clause)
            continue

        if current_clause is not None and line.startswith(" "):
            current_clause["text"] += " " + stripped

    return sections


def retrieve_documents(file_paths: list) -> dict:
    """Load and index all policy documents by document name and section/clause number."""
    index = {}
    for path in file_paths:
        doc_name = path.rsplit("/", 1)[-1]
        index[doc_name] = _parse_policy_file(path)
    return index


def _tokenize(text: str) -> set:
    words = re.findall(r"[a-z0-9]+", text.lower())
    tokens = set()
    for w in words:
        if w in STOPWORDS or len(w) <= 1:
            continue
        tokens.add(_stem(w))
        if w in ABBREVIATION_EXPANSIONS:
            tokens |= {_stem(x) for x in ABBREVIATION_EXPANSIONS[w]}
    return tokens


def _build_token_weights(index: dict) -> dict:
    """
    Inverse-document-frequency style weights: a word shared by all 3
    documents (e.g. "work") barely distinguishes anything; a word unique
    to one document (e.g. "install") is a strong signal for that document.
    """
    doc_tokens = {}
    for doc_name, sections in index.items():
        tokens = set()
        for section in sections:
            for clause in section["clauses"]:
                tokens |= _tokenize(clause["text"])
        doc_tokens[doc_name] = tokens

    all_tokens = set().union(*doc_tokens.values()) if doc_tokens else set()
    weights = {}
    for token in all_tokens:
        doc_count = sum(1 for tokens in doc_tokens.values() if token in tokens)
        weights[token] = 1.0 / doc_count
    return weights


def _score_clause(query_tokens: set, clause_text: str, token_weights: dict) -> float:
    clause_tokens = _tokenize(clause_text)
    matched = query_tokens & clause_tokens
    return sum(token_weights.get(t, 0.0) for t in matched)


def answer_question(query: str, index: dict, token_weights: dict) -> dict:
    """
    Search all indexed documents. Return a single-source answer with
    citations, or the refusal template if nothing matches or the match
    is ambiguous across documents.
    """
    query_tokens = _tokenize(query)

    doc_best_score = {}
    doc_clause_scores = {}

    for doc_name, sections in index.items():
        clause_scores = []
        for section in sections:
            for clause in section["clauses"]:
                score = _score_clause(query_tokens, clause["text"], token_weights)
                if score > 0:
                    clause_scores.append((score, clause["clause_number"], clause["text"]))
        clause_scores.sort(key=lambda c: (-c[0], c[1]))
        doc_clause_scores[doc_name] = clause_scores
        doc_best_score[doc_name] = clause_scores[0][0] if clause_scores else 0.0

    ranked_docs = sorted(doc_best_score.items(), key=lambda kv: -kv[1])
    top_doc, top_score = ranked_docs[0]
    second_score = ranked_docs[1][1] if len(ranked_docs) > 1 else 0.0

    if top_score == 0:
        return {"refusal": REFUSAL_TEMPLATE}

    if abs(second_score - top_score) < 1e-9:
        # Two+ documents are equally relevant — do not guess which one
        # answers, and do not blend them into one answer.
        return {"refusal": REFUSAL_TEMPLATE}

    top_clauses = [c for c in doc_clause_scores[top_doc] if abs(c[0] - top_score) < 1e-9][:3]
    citations = [{"document": top_doc, "section": num} for _, num, _ in top_clauses]
    answer_text = " ".join(text for _, _, text in top_clauses)

    return {"answer": answer_text, "citations": citations}


def format_response(result: dict) -> str:
    if "refusal" in result:
        return result["refusal"]
    citation_str = "; ".join(f"{c['document']} section {c['section']}" for c in result["citations"])
    return f"{result['answer']}\n[Source: {citation_str}]"


def main():
    index = retrieve_documents(DOCUMENT_PATHS)
    token_weights = _build_token_weights(index)
    print("UC-X Ask My Documents — type a question (or 'exit' to quit).")
    while True:
        try:
            query = input("\n> ").strip()
        except EOFError:
            break
        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            break
        result = answer_question(query, index, token_weights)
        print(format_response(result))


if __name__ == "__main__":
    main()
