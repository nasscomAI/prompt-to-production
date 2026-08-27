"""
UC-X — Ask My Documents

Single-source policy Q&A over three CMC policy documents. Built to the
enforcement rules in agents.md and the skill contracts in skills.md.

Run (interactive):
    python app.py

Run (verify against the 7 README test questions):
    python app.py --selftest
"""
import argparse
import os
import re

DOC_DIR = os.path.join("..", "data", "policy-documents")
DOCS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z].*)$")

# Very common words that should not drive matching.
STOPWORDS = set("""
a an the is are can i my me you your we our of to for on in at with and or not do does
what who how when where which this that use used using be been am pm from into it its
""".split())

# Domain synonyms so questions map to document vocabulary (single words only,
# to keep word-level matching clean).
SYNONYMS = {
    "phone": ["device", "devices", "byod", "mobile"],
    "personal": ["byod"],
    "laptop": ["laptops", "corporate"],
    "install": ["software"],
    "slack": ["software", "install"],
    "carry": ["forward", "carried"],
    "forward": ["carried"],
    "allowance": ["equipment"],
    "equipment": ["allowance"],
    "home": ["wfh"],
    "office": ["equipment"],
    "da": ["daily", "allowance"],
    "meal": ["meals"],
    "receipts": ["receipt"],
    "approves": ["approval", "requires"],
    "approve": ["approval", "requires"],
    "pay": ["lwp"],
    "without": ["lwp"],
}


# --- Skill: retrieve_documents ----------------------------------------------

def retrieve_documents(paths):
    """Load and index the policy documents by document name and clause number."""
    index = {}
    for path in paths:
        name = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            raise SystemExit(f"ERROR: could not open policy document '{path}': {exc}")

        clauses = []
        heading = ""
        current = None
        for raw in lines:
            line = raw.rstrip()
            if not line or set(line) <= set("═ "):
                continue
            clause_match = CLAUSE_RE.match(line)
            section_match = SECTION_RE.match(line)
            if section_match and not clause_match:
                heading = section_match.group(2).strip()
                current = None
            elif clause_match:
                current = {
                    "document": name,
                    "number": clause_match.group(1),
                    "heading": heading,
                    "text": clause_match.group(2).strip(),
                }
                clauses.append(current)
            elif current is not None:
                current["text"] += " " + line.strip()
        index[name] = clauses
    return index


# --- Skill: answer_question -------------------------------------------------

def _words(text: str):
    """Split into lowercase words, splitting hyphens so 'work-from-home' -> words."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _clause_words(clause):
    return set(_words(clause["heading"] + " " + clause["text"]))


def _query_terms(question: str):
    """Content words from the question plus single-word synonyms (stopwords removed)."""
    terms = set()
    for w in _words(question):
        if w in STOPWORDS or len(w) < 2:
            continue
        terms.add(w)
        for syn in SYNONYMS.get(w, []):
            terms.add(syn)
    return terms


def _term_matches_wordset(term, wordset):
    """Word-level match with light prefix stemming (meal~meals, claim~claimed)."""
    if term in wordset:
        return True
    for w in wordset:
        short, long = (term, w) if len(term) <= len(w) else (w, term)
        if len(short) >= 4 and long.startswith(short):
            return True
    return False


def _build_idf(index):
    """Inverse document frequency per word across all clauses (rarer = higher weight)."""
    import math
    clause_wordsets = []
    for clauses in index.values():
        for c in clauses:
            clause_wordsets.append(_clause_words(c))
    n = len(clause_wordsets) or 1
    df = {}
    for ws in clause_wordsets:
        for w in ws:
            df[w] = df.get(w, 0) + 1
    return {w: math.log((n + 1) / (count + 1)) + 1.0 for w, count in df.items()}, n


HEADING_BOOST = 2.0  # section-heading matches are strong topic signals


def _clause_score(query_terms, body_wordset, heading_wordset, idf):
    """
    IDF-weighted score for query terms in a clause. Matches in the section
    heading are weighted higher (topic relevance), which keeps a question about
    'personal' devices on the PERSONAL DEVICES section rather than CORPORATE.
    """
    score = 0.0
    distinct = 0
    for term in query_terms:
        weight = idf.get(term, 1.0)
        if _term_matches_wordset(term, heading_wordset):
            score += weight * HEADING_BOOST
            distinct += 1
        elif _term_matches_wordset(term, body_wordset):
            score += weight
            distinct += 1
    return score, distinct


def answer_question(question, index, min_distinct=2, min_score=2.5):
    """
    Answer from the single best-matching document, or return the refusal template.

    Enforces single-source: scores every clause with IDF-weighted word matching,
    picks the single strongest clause, and answers only from that clause's
    document. Refuses when the match is too weak (guards against hallucination on
    out-of-scope questions).
    """
    qterms = _query_terms(question)
    idf, _ = _build_idf(index)

    scored = []  # (score, distinct, clause)
    for clauses in index.values():
        for c in clauses:
            body_ws = set(_words(c["text"]))
            heading_ws = set(_words(c["heading"]))
            score, distinct = _clause_score(qterms, body_ws, heading_ws, idf)
            if score > 0:
                scored.append((score, distinct, c))

    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    top_score, top_distinct, top_clause = scored[0]

    # Relevance gate: refuse rather than hallucinate on weak matches.
    if top_distinct < min_distinct or top_score < min_score:
        return REFUSAL_TEMPLATE

    top_doc = top_clause["document"]

    # Single-source: keep only near-top clauses FROM THE SAME document.
    chosen = [top_clause]
    for score, distinct, c in scored[1:]:
        if c["document"] != top_doc:
            continue
        if score >= top_score - 1e-9 or (top_score - score) / top_score <= 0.15:
            if c["number"] != top_clause["number"]:
                chosen.append(c)
        if len(chosen) >= 2:
            break

    lines = [f"According to {c['document']} section {c['number']}: {c['text']}" for c in chosen]
    return "\n".join(lines)


# --- CLI --------------------------------------------------------------------

SELFTEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def _load_index():
    paths = [os.path.join(DOC_DIR, d) for d in DOCS]
    return retrieve_documents(paths)


def run_selftest():
    index = _load_index()
    for q in SELFTEST_QUESTIONS:
        print("Q:", q)
        print(answer_question(q, index))
        print("-" * 70)


def run_interactive():
    index = _load_index()
    print("Ask My Documents — single-source policy Q&A. Type 'quit' to exit.")
    while True:
        try:
            q = input("\nQuestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in ("quit", "exit", ""):
            break
        print(answer_question(q, index))


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the 7 README test questions and print answers")
    parser.add_argument("--question", default="", help="Answer a single question and exit")
    args = parser.parse_args()

    if args.selftest:
        run_selftest()
    elif args.question:
        print(answer_question(args.question, _load_index()))
    else:
        run_interactive()


if __name__ == "__main__":
    main()
