"""
UC-X — Ask My Documents

A document-grounded policy QA CLI over three policy files. It avoids the three
failure modes:
  - Cross-document blending -> an answer is sourced from exactly ONE document/section
  - Hedged hallucination     -> no hedging phrases; out-of-scope -> verbatim refusal
  - Condition dropping       -> the answer returns the full source clause text, so
                                multi-condition obligations stay intact

Retrieval is a transparent IDF-weighted keyword match over clauses (each clause
carries its section-header context), with a few synonym boosts. The single
highest-scoring clause wins; if nothing clears the confidence threshold, the
verbatim refusal template is returned.

Run:  python app.py        (interactive; also accepts piped questions on stdin)
"""
import re
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

DOCS = {
    "policy_hr_leave.txt":            "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":   "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {
    "a", "an", "the", "is", "are", "can", "could", "i", "my", "me", "we", "on",
    "of", "for", "to", "from", "what", "whats", "who", "do", "does", "did", "in",
    "and", "or", "be", "will", "would", "should", "this", "that", "it", "you",
    "your", "with", "any", "am", "if", "at", "as", "by", "how", "when", "use",
    "using", "used", "get", "may", "into", "out", "about", "same",
}

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")

# Distinctive terms -> (document, section). Disambiguates questions whose literal
# wording barely overlaps the target clause (acronyms, BYOD, DA-vs-meal). Each term:
# a multi-word term is matched as a substring of the question; a single word is
# matched as a stemmed token. ALL terms in an entry must match for the boost to fire.
BOOSTS = [
    (["personal phone"], "policy_it_acceptable_use.txt", "3.1"),
    (["personal device"], "policy_it_acceptable_use.txt", "3.1"),
    (["install"], "policy_it_acceptable_use.txt", "2.3"),
    (["leave without pay"], "policy_hr_leave.txt", "5.2"),
    (["lwp"], "policy_hr_leave.txt", "5.2"),
    (["da", "meal"], "policy_finance_reimbursement.txt", "2.6"),
]


def _boost_matches(terms, ql, q_stems):
    """True only if every term in the entry is present in the question."""
    for term in terms:
        if " " in term:
            if term not in ql:
                return False
        elif _stem(term) not in q_stems:
            return False
    return True


def _stem(tok: str) -> str:
    """Crude stemmer: lowercase, drop trailing 's', clip to 5 chars."""
    if len(tok) > 3 and tok.endswith("s"):
        tok = tok[:-1]
    return tok[:5]


def _tokens(text: str):
    return [_stem(t) for t in re.findall(r"[a-z0-9]+", text.lower())
            if t not in STOPWORDS]


def retrieve_documents(docs=DOCS):
    """
    Load all policy files and index them by document name + section number.
    Returns: list of clause dicts {doc, section, title, text, tokens} and the
    IDF table over clause token-sets.
    """
    clauses = []
    for name, path in docs.items():
        current_title, current_id = "", None
        with open(path, encoding="utf-8") as f:
            for raw in f:
                line = raw.rstrip("\n")
                if not line.strip() or set(line.strip()) <= {"═", "─", "="}:
                    continue
                sec = SECTION_RE.match(line.strip())
                cl = CLAUSE_RE.match(line)
                if cl:
                    cid, text = cl.group(1), cl.group(2).strip()
                    clauses.append({"doc": name, "section": cid,
                                    "title": current_title, "text": text})
                    current_id = cid
                elif sec:
                    current_title = sec.group(2).strip()
                    current_id = None
                elif current_id and line.startswith((" ", "\t")):
                    clauses[-1]["text"] += " " + line.strip()

    # token set per clause = clause text + its section-header context
    for c in clauses:
        c["text"] = re.sub(r"\s+", " ", c["text"]).strip()
        c["tokens"] = set(_tokens(c["text"] + " " + c["title"]))

    # IDF over clauses
    N = len(clauses)
    df = {}
    for c in clauses:
        for tok in c["tokens"]:
            df[tok] = df.get(tok, 0) + 1
    import math
    idf = {tok: math.log((N + 1) / (d + 0.5)) for tok, d in df.items()}
    return clauses, idf


def _best_excerpt(text: str, q_stems: set) -> str:
    """Most query-relevant sentence in the clause, truncated to 125 chars."""
    sentences = re.split(r"(?<=[.;])\s+", text)
    best, best_hits = text, -1
    for s in sentences:
        hits = sum(1 for t in set(_tokens(s)) if t in q_stems)
        if hits > best_hits:
            best, best_hits = s, hits
    return best[:125].strip()


def answer_question(question: str, clauses, idf, threshold: float = 2.5) -> dict:
    """
    Return a single-source answer with citation, or the refusal template.
    Output dict: {answer, source_document, section, excerpt, refused}
    """
    q_stems = set(_tokens(question))
    ql = question.lower()

    # Score every clause; track the single best across ALL documents.
    scored = []
    for c in clauses:
        matched = [t for t in q_stems if t in c["tokens"]]
        score = sum(idf.get(t, 0.0) for t in matched)
        boosted = False
        for terms, doc, sec in BOOSTS:
            if c["doc"] == doc and c["section"] == sec and \
                    _boost_matches(terms, ql, q_stems):
                score += 10.0
                boosted = True
        scored.append((score, len(matched), boosted, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score, top_matched, top_boosted, top = scored[0]

    # Refuse unless we are confident: a boost, or a clear multi-term match.
    if not top_boosted and (top_score < threshold or top_matched < 2):
        return {"answer": REFUSAL, "source_document": None,
                "section": None, "excerpt": None, "refused": True}

    return {
        "answer": top["text"],
        "source_document": top["doc"],
        "section": top["section"],
        "excerpt": _best_excerpt(top["text"], q_stems),
        "refused": False,
    }


def _format(question: str, res: dict) -> str:
    if res["refused"]:
        return f"Question: {question}\nAnswer: {res['answer']}\n"
    return (
        f"Question: {question}\n"
        f"Answer: {res['answer']}\n"
        f"Source: {res['source_document']} — Section {res['section']}\n"
        f"Excerpt: {res['excerpt']}\n"
    )


def main():
    clauses, idf = retrieve_documents()
    interactive = sys.stdin.isatty()
    if interactive:
        print("Ask My Documents — type a policy question (or 'quit' to exit).")
    while True:
        if interactive:
            try:
                question = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
        else:
            line = sys.stdin.readline()
            if not line:
                break
            question = line.strip()
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break
        print(_format(question, answer_question(question, clauses, idf)))


if __name__ == "__main__":
    main()
