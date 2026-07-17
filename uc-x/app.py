"""
UC-X app.py
Built using the RICE (agents.md) -> skills.md -> CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import math
import re

DIVIDER_RE = re.compile(r"^═+$")
SECTION_HEADER_PREFIX_RE = re.compile(r"^\d+\.\s")
CLAUSE_PREFIX_RE = re.compile(r"^\d+\.\d+\s")

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "be", "to", "of", "for", "on", "in",
    "and", "or", "do", "does", "did", "my", "i", "me", "can", "could", "what",
    "who", "when", "where", "how", "this", "that", "with", "from", "at", "as",
    "it", "if", "you", "your", "same", "day", "will", "must", "not", "any",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# A close-enough second-place score (relative to the top score) means the
# question genuinely straddles two documents, not that one of them just
# happens to share a stray word with the winner.
AMBIGUITY_MARGIN = 0.8
TOP_K_FOR_DOC_SCORE = 2


def _tokenize(text: str) -> list:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def _parse_clauses(doc_name: str, raw_lines: list) -> list:
    clauses = []
    state = {"section": None, "clause": None, "text": []}

    def flush():
        if state["clause"] is not None:
            clauses.append({
                "doc": doc_name,
                "section": state["section"],
                "clause": state["clause"],
                "text": " ".join(state["text"]).strip(),
            })

    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line or DIVIDER_RE.match(line):
            continue

        clause_match = CLAUSE_PREFIX_RE.match(line)
        if clause_match:
            flush()
            state["clause"] = line[:clause_match.end()].split()[0]
            state["text"] = [line[clause_match.end():].strip()]
            continue

        section_match = SECTION_HEADER_PREFIX_RE.match(line)
        if section_match:
            flush()
            state["clause"] = None
            state["text"] = []
            state["section"] = line
            continue

        if state["clause"] is not None:
            state["text"].append(line)

    flush()
    return clauses


def retrieve_documents(file_paths: list) -> list:
    """
    Load all policy .txt files and return their content as structured,
    per-clause entries tagged with their source document.
    """
    clauses = []
    for file_path in file_paths:
        with open(file_path, encoding="utf-8") as f:
            raw_lines = [line.rstrip("\n") for line in f]

        doc_name = file_path.replace("\\", "/").rsplit("/", 1)[-1]
        doc_clauses = _parse_clauses(doc_name, raw_lines)
        if not doc_clauses:
            raise ValueError(f"No numbered clauses found in {file_path}")

        clauses.extend(doc_clauses)

    return clauses


def _clause_tokens(entry: dict) -> set:
    return set(_tokenize(entry["text"])) | set(_tokenize(entry["section"] or ""))


def _build_idf(clauses: list) -> dict:
    """
    Rare, distinguishing words (e.g. "install") should count for more than
    generic words that show up throughout every policy (e.g. "work",
    "employee") — otherwise a document that just happens to use common
    vocabulary a lot can out-score the document that actually answers the
    question.
    """
    doc_freq = {}
    for entry in clauses:
        for token in _clause_tokens(entry):
            doc_freq[token] = doc_freq.get(token, 0) + 1
    n = len(clauses)
    return {token: math.log((1 + n) / (1 + df)) + 1 for token, df in doc_freq.items()}


def _score_clauses(clauses: list, question_tokens: set, idf: dict) -> list:
    scored = []
    for entry in clauses:
        overlap = question_tokens & _clause_tokens(entry)
        score = sum(idf.get(token, 0.0) for token in overlap)
        scored.append((score, entry))
    return scored


def _pick_document(scored_clauses: list):
    # Rank documents by their *best* matching clauses, not the sum across
    # every clause — otherwise a long, loosely-related section can outscore
    # the one specific clause that actually answers the question.
    doc_top_scores = {}
    for score, entry in scored_clauses:
        doc_top_scores.setdefault(entry["doc"], []).append(score)
    doc_scores = {
        doc: sum(sorted(scores, reverse=True)[:TOP_K_FOR_DOC_SCORE])
        for doc, scores in doc_top_scores.items()
    }

    ranked = sorted(doc_scores.items(), key=lambda kv: kv[1], reverse=True)
    best_doc, best_score = ranked[0]

    if best_score <= 0:
        return None

    if len(ranked) > 1:
        _, second_score = ranked[1]
        if second_score > 0 and second_score >= best_score * AMBIGUITY_MARGIN:
            return None

    return best_doc


def answer_question(clauses: list, question: str) -> dict:
    """
    Score every clause against the question, answer from exactly one
    document's highest-scoring clauses, or refuse if nothing matches or the
    match is genuinely ambiguous between two documents.
    """
    question_tokens = set(_tokenize(question))
    idf = _build_idf(clauses)
    scored_clauses = _score_clauses(clauses, question_tokens, idf)

    best_doc = _pick_document(scored_clauses)
    if best_doc is None:
        return {"answer": REFUSAL_TEMPLATE, "citations": []}

    doc_clauses = [(score, entry) for score, entry in scored_clauses if entry["doc"] == best_doc and score > 0]
    top_score = max(score for score, _ in doc_clauses)
    top_clauses = [entry for score, entry in doc_clauses if score == top_score]
    top_clauses.sort(key=lambda e: e["clause"])

    lines = []
    citations = []
    for entry in top_clauses:
        citation = f"{entry['doc']}, Clause {entry['clause']}"
        citations.append(citation)
        lines.append(f'[{citation}] "{entry["text"]}"')

    return {"answer": "\n".join(lines), "citations": citations}


DOCUMENT_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def main():
    clauses = retrieve_documents(DOCUMENT_PATHS)
    print("Loaded", len(clauses), "clauses from", len(DOCUMENT_PATHS), "documents.")
    print("Ask a question about HR leave, IT acceptable use, or finance reimbursement policy.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break

        result = answer_question(clauses, question)
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()
