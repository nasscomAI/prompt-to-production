"""
UC-X — Ask My Documents

Policy Q&A over the three CMC policy files. Every answer comes from ONE document only,
quotes the clause text as written, and cites document + section. If no clause covers the
question well enough — or a clause from another document covers it almost as well — the
exact refusal template is returned instead. No blending, no hedging.

Usage:
  python app.py                          # interactive
  python app.py --ask "Who approves leave without pay?"
"""
import argparse
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(HERE, "..", "data", "policy-documents")
DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the HR, IT or Finance department for guidance."
)
BANNED_HEDGES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "generally", "usually",
]

STOPWORDS = set("""
a an the i me my we our you your is are am be can could do does to of in on at for from
with by and or as it its this that what which who whom how when where why if any there
same about under into per than then so not no yes will would should may might
""".split())
# Present in almost every clause; they carry no weight and never count as evidence.
GENERIC = {"work", "employee", "policy", "cmc", "company", "staff"}
# Irregular forms the suffix stripper would otherwise split apart.
LEMMAS = {"used": "use", "using": "use", "uses": "use", "approves": "approv", "approved": "approv"}

# Question word → words the policies actually use for it.
SYNONYMS = {
    "phone": ["phone", "mobile", "device", "smartphone"],
    "mobile": ["mobile", "phone", "device"],
    "laptop": ["laptop", "device", "corporate"],
    "computer": ["computer", "device", "laptop", "desktop"],
    "slack": ["software"],
    "app": ["software"],
    "install": ["install"],
    "unused": ["unused"],
    "da": ["da", "allowance"],
    "lwp": ["lwp"],
    "allowance": ["allowance"],
    "equipment": ["equipment"],
    "receipt": ["receipt"],
    "meal": ["meal"],
}
PHRASES = {
    r"leave without pay": "lwp",
    r"daily allowance": "da",
    r"carry[- ]forward": "carry_forward",
    r"work[- ]from[- ]home": "home",
    r"personal (?:phones?|devices?|mobiles?)": "personal_device",
}
MIN_EVIDENCE_TERMS = 2       # distinct non-generic question terms the best clause must contain
TIE_RATIO = 0.9              # a second document this close to the best → ambiguous → refuse
FOLLOW_RATIO = 0.75          # extra clauses from the same document shown if this close


def _stem(word):
    if word in LEMMAS:
        return LEMMAS[word]
    for suffix, repl in (("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("al", ""), ("s", "")):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)] + repl
    return word


def _tokens(text):
    low = text.lower()
    for pat, repl in PHRASES.items():
        low = re.sub(pat, " " + repl + " ", low)
    words = re.findall(r"[a-z_]+|\d+", low)
    return [_stem(w) for w in words if w not in STOPWORDS]


def retrieve_documents(doc_dir=DOC_DIR):
    """Load all policy files and index them as clauses: [{doc, section, heading, text, tokens}]."""
    clauses = []
    for name in DOCUMENTS:
        path = os.path.join(doc_dir, name)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            sys.exit(f"Refusing to start: {path} not found - answers would be incomplete.")
        heading, current = "", None
        for raw in lines:
            line = raw.strip()
            if not line or set(line) <= {"\u2550", "="}:
                continue
            m_head = re.match(r"^(\d+)\.\s+([A-Z][A-Z ()\u2013\u2014&'/,-]+)$", line)
            m_clause = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
            if m_head and not m_clause:
                heading, current = m_head.group(2).strip(), None
            elif m_clause:
                current = {"doc": name, "section": m_clause.group(1), "heading": heading,
                           "text": m_clause.group(2)}
                clauses.append(current)
            elif current is not None:
                current["text"] += " " + line
    for c in clauses:
        c["tokens"] = set(_tokens(c["heading"] + " " + c["text"]))
    # inverse document frequency over clauses: rare words carry more evidence
    n = len(clauses)
    df = {}
    for c in clauses:
        for t in c["tokens"]:
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log(1 + n / d) for t, d in df.items()}
    return clauses, idf


def _score(question_terms, clause, idf):
    """Sum, per question term, the idf of the best clause word matching it.

    An exact match counts in full, a synonym match counts half, and each clause word can
    back only one question term (so 'device' cannot count for both 'mobile' and 'phone').
    """
    score, evidence, used = 0.0, [], set()
    for term in question_terms:
        if term in GENERIC:
            continue
        options = [(o, 1.0 if o == term else 0.5)
                   for o in dict.fromkeys([term] + [_stem(s) for s in SYNONYMS.get(term, [])])]
        hits = [(idf.get(o, 0) * w, o) for o, w in options
                if o in clause["tokens"] and o not in used]
        if hits:
            value, word = max(hits)
            score += value
            used.add(word)
            evidence.append(term)
    return score, evidence


def answer_question(question, clauses, idf):
    """Return a single-source cited answer, or the refusal template."""
    terms = list(dict.fromkeys(_tokens(question)))
    if not terms:
        return REFUSAL

    scored = []
    for c in clauses:
        s, ev = _score(terms, c, idf)
        if s > 0:
            scored.append((s, ev, c))
    if not scored:
        return REFUSAL
    scored.sort(key=lambda x: -x[0])
    best_score, best_ev, best = scored[0]

    if len(set(best_ev)) < MIN_EVIDENCE_TERMS:
        return REFUSAL

    # Single-source rule: a different document scoring almost as well means the
    # question straddles documents - refuse rather than blend.
    rival = next((x for x in scored if x[2]["doc"] != best["doc"]), None)
    if rival and rival[0] >= TIE_RATIO * best_score and len(set(rival[1])) >= MIN_EVIDENCE_TERMS:
        return REFUSAL

    picked = [x[2] for x in scored
              if x[2]["doc"] == best["doc"] and x[0] >= FOLLOW_RATIO * best_score][:3]
    picked.sort(key=lambda c: [int(p) for p in c["section"].split(".")])

    sections = ", ".join(c["section"] for c in picked)
    lines = [f"Source: {best['doc']} - section {sections}"]
    for c in picked:
        lines.append(f"  [{c['section']}] {c['text']}")
    answer = "\n".join(lines)

    assert not any(h in answer.lower() for h in BANNED_HEDGES), "hedging phrase in answer"
    return answer


def main():
    parser = argparse.ArgumentParser(description="UC-X single-source policy Q&A")
    parser.add_argument("--ask", help="Answer one question and exit")
    args = parser.parse_args()

    clauses, idf = retrieve_documents()
    if args.ask:
        print(answer_question(args.ask, clauses, idf))
        return

    print(f"Indexed {len(clauses)} clauses from {len(DOCUMENTS)} policy documents.")
    print("Ask a policy question (blank line or 'exit' to quit).")
    while True:
        try:
            q = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q or q.lower() in {"exit", "quit"}:
            break
        print(answer_question(q, clauses, idf))


if __name__ == "__main__":
    main()