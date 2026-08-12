"""
UC-X — Ask My Documents
Built via RICE -> agents.md -> skills.md -> CRAFT workflow.

Fixes applied over the naive baseline (see git history for the naive
Control-step run and its failures):
  1. Retrieval failure -> replaced blind substring/word search with a
                           clause-level index (retrieve_documents) plus an
                           IDF-weighted scorer with a light synonym table
                           and exact-phrase bonus (answer_question), so
                           relevant clauses actually outrank generic noise.
  2. Cross-document blending / no attribution -> scoring is grouped by
                           document; only the single best-scoring document
                           is ever used for an answer, and every answer
                           states its filename + clause number(s).
  3. False-confidence / hedged hallucination -> a minimum relevance floor
                           and a document-vs-document margin check trigger
                           the EXACT refusal template (never a paraphrase
                           of it, never a hedge phrase) whenever no clause
                           clears the floor or two documents are too close
                           to call.
  4. Console crash on non-ASCII text -> stdout is reconfigured to UTF-8
                           defensively at startup.

See agents.md for the enforcement rules this file implements and skills.md
for the two skills (retrieve_documents, answer_question) this file defines.
"""
import re
import sys

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Relevance floor: a document's best clause must clear this weighted score
# to be considered "on topic" at all.
MIN_RELEVANCE = 1.2
# If the second-best document's score is within this fraction of the best
# document's score, treat it as genuine cross-document ambiguity and
# refuse rather than pick one (agents.md: never blend, never guess).
AMBIGUITY_MARGIN = 0.6

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "i", "you", "he", "she", "it", "we", "they", "my", "your", "their",
    "this", "that", "these", "those", "to", "of", "in", "on", "for",
    "and", "or", "but", "if", "with", "at", "by", "from", "as", "do",
    "does", "did", "can", "could", "will", "would", "should", "what",
    "who", "when", "where", "why", "how", "about", "into", "up", "out",
    "not", "no", "so", "than", "then", "there", "here", "any", "same",
    "day", "days",  # generic across every document; do NOT drive matches
}

# Small alias table so everyday phrasing ("laptop", "phone") reaches the
# document's own vocabulary ("device", "corporate"). This is a general
# retrieval aid built from the corpus/question vocabulary, not a
# question -> answer lookup: it never determines the answer text itself,
# only which clauses are considered for scoring.
SYNONYMS = {
    "laptop": {"device", "devices", "corporate"},
    "computer": {"device", "devices", "corporate", "desktop"},
    "phone": {"device", "devices", "mobile"},
    "mobile": {"device", "devices", "phone"},
    "install": {"installation", "installed", "software"},
    "software": {"install", "installation", "application", "program"},
    "app": {"software", "application"},
    "wifi": {"network", "internet"},
    "files": {"data", "email", "portal", "document", "documents"},
    "allowance": {"reimbursement", "reimbursable", "entitled", "entitlement"},
    "receipts": {"receipt", "bill", "bills"},
    "meal": {"meals", "food"},
    "approves": {"approval", "approved", "approve"},
    "approve": {"approval", "approved", "approves"},
    "culture": {"practice", "policy"},
    "flexible": {"flexi", "hybrid"},
}

DIVIDER_RE = re.compile(r"^[═=]{5,}$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z0-9][A-Z0-9 \-/&()]*)$")
WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str):
    return WORD_RE.findall(text.lower())


def _parse_clauses(file_path: str):
    """Parse one policy .txt into a flat list of {section, section_title,
    text} clauses, joining wrapped physical lines into single logical
    sentences (same approach as UC-0B's retrieve_policy). Each clause
    remembers its parent section title (e.g. "LEAVE WITHOUT PAY (LWP)")
    because a clause that uses an abbreviation ("LWP requires approval...")
    would otherwise lose to a neighbouring clause that happens to spell the
    term out in full -- the section header is where the full term lives."""
    with open(file_path, encoding="utf-8") as f:
        text = f.read()

    clauses = []
    current_section_title = ""
    current_clause = None  # (number, [parts])

    def flush():
        nonlocal current_clause
        if current_clause:
            num, parts = current_clause
            joined = re.sub(r"\s+", " ", " ".join(p.strip() for p in parts if p.strip())).strip()
            clauses.append({"section": num, "section_title": current_section_title, "text": joined})
        current_clause = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or DIVIDER_RE.match(line):
            continue
        m_clause = CLAUSE_RE.match(line)
        if m_clause:
            flush()
            current_clause = (m_clause.group(1), [m_clause.group(2)])
            continue
        m_section = SECTION_RE.match(line)
        if m_section:
            flush()
            current_section_title = m_section.group(2).strip()
            continue
        if current_clause is not None:
            current_clause[1].append(line)
    flush()
    return clauses


def retrieve_documents(paths=None):
    """
    Load all policy files and index every clause by document name and
    section number, plus a corpus-wide document-frequency table for
    IDF-style scoring in answer_question.
    """
    paths = paths or DOC_PATHS
    index = {}
    for path in paths:
        try:
            index[path.split("/")[-1]] = _parse_clauses(path)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Required policy document not found: {path}. "
                f"Refusing to answer from an incomplete document set."
            )

    doc_freq = {}
    total_clauses = 0
    for clauses in index.values():
        for clause in clauses:
            total_clauses += 1
            for term in set(_tokenize(clause["text"])):
                doc_freq[term] = doc_freq.get(term, 0) + 1

    if total_clauses == 0:
        raise ValueError("No clauses were parsed from any policy document. Refusing to answer.")

    return index, doc_freq, total_clauses


def _expand_terms(tokens):
    expanded = set(tokens)
    for tok in tokens:
        expanded |= SYNONYMS.get(tok, set())
    return expanded


def _score_clause(question_terms, question_text_lower, clause_text, section_title, doc_freq, total_clauses):
    # Score against the clause's own text PLUS its parent section title.
    # A clause that only uses an abbreviation ("LWP requires approval...")
    # still gets credit for the spelled-out term because the section
    # header ("5. LEAVE WITHOUT PAY (LWP)") carries it -- without this, a
    # neighbouring clause that happens to spell the phrase out wins by
    # phrase-match bonus alone, even if it is the wrong clause.
    context_text = f"{clause_text} {section_title}"
    context_terms = set(_tokenize(context_text))
    context_lower = context_text.lower()

    score = 0.0
    for term in question_terms & context_terms:
        if term in STOPWORDS or len(term) < 3:
            continue
        df = doc_freq.get(term, 1)
        weight = 1.0 / (1 + (df / max(1, total_clauses)) * 20)  # rarer term -> higher weight
        score += weight

    # Exact-phrase bonus: consecutive question bigrams/trigrams that
    # appear verbatim in the clause+section context are strong evidence.
    q_words = [w for w in _tokenize(question_text_lower) if w not in STOPWORDS]
    for n in (3, 2):
        for i in range(len(q_words) - n + 1):
            phrase = " ".join(q_words[i:i + n])
            if len(phrase) > 5 and phrase in context_lower:
                score += 1.5

    # A clause's OWN text matching (not just its section title) is what
    # actually answers the question -- require at least one direct term
    # overlap with the clause text itself, not just the shared section
    # title, or this clause is not really evidence for this question.
    if not (question_terms & set(_tokenize(clause_text))):
        score *= 0.15

    return score


def answer_question(question: str, index, doc_freq, total_clauses):
    """
    Score the question against every clause; if a single document has a
    clear best-scoring clause, answer from that document only (verbatim,
    cited). Otherwise refuse with the exact template.
    """
    raw_tokens = [t for t in _tokenize(question) if t not in STOPWORDS and len(t) >= 3]
    question_terms = _expand_terms(raw_tokens)

    if not raw_tokens:
        return {"status": "refused", "source_document": None, "sections": [], "text": REFUSAL_TEMPLATE}

    doc_best = {}   # doc -> [ (section, section_title, text, score) ... sorted best first ]
    for doc_name, clauses in index.items():
        scored = []
        for clause in clauses:
            s = _score_clause(
                question_terms, question, clause["text"], clause["section_title"],
                doc_freq, total_clauses,
            )
            if s > 0:
                scored.append((clause["section"], clause["section_title"], clause["text"], s))
        scored.sort(key=lambda c: c[3], reverse=True)
        doc_best[doc_name] = scored

    ranked_docs = sorted(
        doc_best.items(),
        key=lambda item: item[1][0][3] if item[1] else 0.0,
        reverse=True,
    )

    top_doc, top_clauses = ranked_docs[0]
    top_score = top_clauses[0][3] if top_clauses else 0.0

    if top_score < MIN_RELEVANCE:
        return {"status": "refused", "source_document": None, "sections": [], "text": REFUSAL_TEMPLATE}

    if len(ranked_docs) > 1:
        second_doc, second_clauses = ranked_docs[1]
        second_score = second_clauses[0][3] if second_clauses else 0.0
        if second_score >= AMBIGUITY_MARGIN * top_score and second_score >= MIN_RELEVANCE:
            return {"status": "refused", "source_document": None, "sections": [], "text": REFUSAL_TEMPLATE}

    # Within the winning document, keep clauses that are reasonably close
    # to the top one -- captures directly-related multi-clause answers
    # (e.g. HR 2.6 + 2.7 for a carry-forward question) without pulling in
    # weak, unrelated matches.
    cited = [c for c in top_clauses if c[3] >= 0.5 * top_score]
    cited = cited[:3]

    lines = [f"Source: {top_doc}"]
    for section, section_title, text, _score in cited:
        lines.append(f"  [{section}] ({section_title}) {text}")

    return {
        "status": "answered",
        "source_document": top_doc,
        "sections": [c[0] for c in cited],
        "text": "\n".join(lines),
    }


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass  # older Python without reconfigure(); best effort

    try:
        index, doc_freq, total_clauses = retrieve_documents()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Startup failed: {exc}")
        sys.exit(1)

    print("UC-X Ask My Documents")
    print(f"Indexed {total_clauses} clauses across {len(index)} documents: {', '.join(index)}")
    print("Type a question, or 'exit' to quit.")
    while True:
        try:
            question = input("> ")
        except EOFError:
            break
        if not question.strip():
            continue
        if question.strip().lower() in ("exit", "quit"):
            break
        result = answer_question(question, index, doc_freq, total_clauses)
        print(result["text"])
        print()


if __name__ == "__main__":
    main()
