"""
UC-X app.py — Ask My Documents
Interactive CLI policy assistant built using RICE + agents.md + skills.md.

Agent role    : Answers policy questions strictly from the 3 CMC policy documents.
Enforcement   : Single-source only · no hedging · exact refusal template · cite doc+section.
Skills        : retrieve_documents · answer_question
"""

import os
import re

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Prefer local copy (uc-x/data/policy-documents/); fall back to shared ../data/
_local_data = os.path.join(BASE_DIR, "data", "policy-documents")
_shared_data = os.path.normpath(os.path.join(BASE_DIR, "../data/policy-documents"))
DATA_DIR = _local_data if os.path.isdir(_local_data) else _shared_data

POLICY_FILES = {
    "policy_hr_leave.txt": os.path.join(DATA_DIR, "policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": os.path.join(DATA_DIR, "policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": os.path.join(DATA_DIR, "policy_finance_reimbursement.txt"),
}

# Exact refusal template from agents.md — used verbatim, no variations.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Minimum keyword-match score to return an answer (prevents weak/off-topic matches).
MIN_SCORE_THRESHOLD = 2


# ─── SKILL: retrieve_documents ─────────────────────────────────────────────────

def retrieve_documents() -> dict:
    """
    Skill: retrieve_documents
    Loads all 3 policy files and indexes content by document name and section number.

    Input  : File paths defined in POLICY_FILES.
    Output : dict[doc_name][clause_ref] = { section, ref, text }
    Errors : Raises FileNotFoundError if any policy file is missing.
    """
    index = {}

    for doc_name, file_path in POLICY_FILES.items():
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Policy file not found: {file_path}\n"
                "Ensure the data/policy-documents/ directory is present."
            )

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        clauses = {}
        current_section = None
        current_clause = None
        current_text = []

        for line in content.split("\n"):
            stripped = line.strip()

            # Match top-level section headers e.g. "2. ANNUAL LEAVE"
            sec_match = re.match(r"^(\d+)\.\s+([A-Z][A-Z\s\(\)\/&\-]+)$", stripped)
            if sec_match:
                # Flush the current clause before switching section
                if current_clause and current_section:
                    clauses[current_clause] = {
                        "section": current_section,
                        "ref": current_clause,
                        "text": re.sub(r"\s+", " ", " ".join(current_text)).strip(),
                    }
                current_section = f"{sec_match.group(1)}. {sec_match.group(2).strip()}"
                current_clause = None
                current_text = []
                continue

            # Match numbered clauses e.g. "2.6 Employees may carry forward..."
            clause_match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
            if clause_match:
                # Flush previous clause
                if current_clause and current_section:
                    clauses[current_clause] = {
                        "section": current_section,
                        "ref": current_clause,
                        "text": re.sub(r"\s+", " ", " ".join(current_text)).strip(),
                    }
                current_clause = clause_match.group(1)
                current_text = [clause_match.group(2).strip()]
            elif current_clause and stripped and set(stripped) != {"═"}:
                # Continuation line for current clause
                current_text.append(stripped)

        # Flush the final clause
        if current_clause and current_section:
            clauses[current_clause] = {
                "section": current_section,
                "ref": current_clause,
                "text": re.sub(r"\s+", " ", " ".join(current_text)).strip(),
            }

        index[doc_name] = clauses

    return index


# ─── SKILL: answer_question ────────────────────────────────────────────────────

# Common words that carry no discriminating signal — excluded from keyword matching.
_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "i", "my", "me", "we", "our", "you", "your", "they", "their",
    "can", "do", "does", "did", "will", "would", "should", "must", "may",
    "what", "when", "how", "who", "where", "which", "that", "this",
    "to", "for", "of", "in", "on", "at", "by", "from", "with", "and",
    "or", "not", "use", "used", "using", "about", "if", "it", "as",
}


def _stem(token: str) -> str:
    """
    Minimal suffix stripping for better recall.
    Guards on length to avoid over-stemming short words (e.g. 'files' → kept).
    Examples: 'approves' → 'approv', 'claiming' → 'claim', 'laptops' → 'laptop'
    """
    if token.endswith("ing") and len(token) > 6:
        return token[:-3]
    if token.endswith("ves") and len(token) > 5:
        return token[:-3]
    if token.endswith("ied") and len(token) > 5:
        return token[:-3] + "y"
    if token.endswith("es") and len(token) > 5:
        return token[:-2]
    if token.endswith("ed") and len(token) > 5:
        return token[:-2]
    if token.endswith("s") and len(token) > 4:
        return token[:-1]
    return token


def _tokenize(text: str) -> set:
    """Lowercase, strip punctuation, remove stopwords, then stem each token."""
    raw = set(re.sub(r"[^a-z0-9\s]", "", text.lower()).split()) - _STOPWORDS
    return {_stem(t) for t in raw}


def _score_clause(query_tokens: set, clause: dict) -> float:
    """
    Score based on clause *text only* (not section title) using word-boundary
    prefix matching so that e.g. 'phone' does not match mid-word in 'smartphones',
    and 'laptop' correctly matches 'laptops'.
    """
    text = clause["text"].lower()
    return sum(
        1.0 for t in query_tokens
        if re.search(r"\b" + re.escape(t), text)
    )


def answer_question(question: str, index: dict) -> str:
    """
    Skill: answer_question
    Searches the indexed policy documents and returns a single-source answer
    with an explicit citation, or the exact refusal template.

    Input  : User question (str) + indexed documents (dict from retrieve_documents).
    Output : Answer string with citation, OR REFUSAL_TEMPLATE verbatim.

    Enforcement rules applied here:
    1. Never combine claims from two different documents — cross-doc tie → refuse.
    2. Never use hedging phrases — output is either a cited fact or the refusal.
    3. Cite document name + section number for every factual claim.
    4. If question not in documents — use REFUSAL_TEMPLATE exactly, no variations.
    """
    tokens = _tokenize(question)
    if not tokens:
        return REFUSAL_TEMPLATE

    # Score every clause in every document; keep the best-scoring clause per doc.
    best_per_doc = {}
    for doc_name, clauses in index.items():
        best_score, best_clause = 0, None
        for clause in clauses.values():
            score = _score_clause(tokens, clause)
            if score > best_score:
                best_score, best_clause = score, clause
        if best_score > 0:
            best_per_doc[doc_name] = (best_score, best_clause)

    if not best_per_doc:
        return REFUSAL_TEMPLATE

    # Rank documents by their best clause score.
    ranked = sorted(best_per_doc.items(), key=lambda x: x[1][0], reverse=True)
    top_score = ranked[0][1][0]

    # Collect all documents that share the top score.
    top_docs = [item for item in ranked if item[1][0] == top_score]

    # Enforcement rule 1: cross-document tie → refuse rather than blend.
    if len(top_docs) > 1:
        return REFUSAL_TEMPLATE

    # Weak match → refuse (not enough signal to give a reliable answer).
    if top_score < MIN_SCORE_THRESHOLD:
        return REFUSAL_TEMPLATE

    doc_name, (_, clause) = top_docs[0]
    citation = f"{doc_name} — Section {clause['ref']}"
    return f"[{citation}]\n\n{clause['text']}"


# ─── INTERACTIVE CLI ───────────────────────────────────────────────────────────

def main():
    print()
    print("=" * 62)
    print("  UC-X — Ask My Documents")
    print("  CMC Policy Assistant")
    print("=" * 62)
    print("Loading and indexing policy documents...")

    try:
        index = retrieve_documents()
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        return

    doc_count = len(index)
    clause_count = sum(len(clauses) for clauses in index.values())
    print(f"Ready. {doc_count} documents · {clause_count} clauses indexed.\n")
    print("Type a policy question and press Enter.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break

        print()
        answer = answer_question(question, index)
        print(answer)
        print()


if __name__ == "__main__":
    main()
