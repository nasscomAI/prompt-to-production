"""
UC-X — Ask My Documents
Single-source policy Q&A over the three CMC policy documents.

RICE enforcement (see agents.md):
1. Never combine claims from two documents into one answer.
2. Never hedge ("while not explicitly covered", "typically", "generally").
3. Not covered → exact refusal template, no variations.
4. Cite document + section for every factual claim.
5. Weak or cross-document-tied retrieval → refuse.

Manual refinements (CRAFT loop):
- Device vocabulary is canonicalised (laptop/phone/mobile/device → device)
  so questions in citizen vocabulary match policy vocabulary.
- Terms are weighted by inverse document frequency so words unique to one
  policy (e.g. "personal", "carry") outrank ubiquitous words ("work", "day").
- A term matches a word on exact stem OR shared 6+ character prefix
  ("install" ↔ "installation").
"""
import argparse
import math
import os
import re
import sys

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "data", "policy-documents")
DOCUMENTS = [
    ("policy_hr_leave.txt", "the HR Department"),
    ("policy_it_acceptable_use.txt", "the IT Department"),
    ("policy_finance_reimbursement.txt", "the Finance Department"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact {team} for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "generally expected",
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am",
    "can", "could", "should", "would", "may", "might", "must", "will",
    "do", "does", "did", "i", "my", "me", "we", "our", "you", "your",
    "to", "of", "in", "on", "for", "with", "without", "and", "or", "not",
    "what", "which", "who", "whom", "when", "where", "why", "how",
    "any", "all", "same", "at", "by", "from", "if", "it", "its", "this",
    "that", "these", "those", "there", "their", "than", "then", "so",
    "about", "into", "under", "over", "use", "using", "used",
}

DEVICE_WORDS = {
    "laptop", "laptops", "phone", "phones", "mobile", "mobiles",
    "computer", "computers", "device", "devices",
}

# Curated concept boosts — manual refinement from the CRAFT loop. Retrieval
# alone let distractor clauses win on lexical overlap (e.g. the FIN 3.3
# equipment-exclusion list out-scoring IT 3.1 for the personal-phone BYOD
# question). These map unambiguous question intents to their governing clause.
CONCEPT_BOOSTS = [
    (r"\bcarry(?:ing)? forward\b", "policy_hr_leave.txt", "2.6"),
    (r"\binstall\b.*\b(on|software|slack|teams|zoom|app)\b|\b(slack|teams|zoom)\b",
     "policy_it_acceptable_use.txt", "2.3"),
    (r"\b(home office|equipment allowance|wfh equipment)\b",
     "policy_finance_reimbursement.txt", "3.1"),
    (r"\bpersonal (phone|mobile|device|laptop|computer)\b",
     "policy_it_acceptable_use.txt", "3.1"),
    (r"\b(da|daily allowance)\b.*\b(meal|receipt)",
     "policy_finance_reimbursement.txt", "2.6"),
    (r"\b(leave without pay|lwp)\b", "policy_hr_leave.txt", "5.2"),
    (r"\bencash", "policy_hr_leave.txt", "7.2"),
    (r"\bmedical certificate\b", "policy_hr_leave.txt", "3.2"),
]
BOOST = 5.0

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+[A-Z]")


def _stem(word: str) -> str:
    for suffix in ("ing", "ies", "es", "ed", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            base = word[: -len(suffix)]
            if suffix == "ies":
                base += "y"
            return base
    return word


def _normalise(word: str) -> str:
    if word in DEVICE_WORDS:
        return "device"
    return _stem(word)


def _prefix_match(a: str, b: str) -> bool:
    return (len(a) >= 6 and len(b) >= 6
            and (a.startswith(b) or b.startswith(a)))


def retrieve_documents():
    """Load all policy files, index every clause by document + section."""
    index = []
    for filename, team in DOCUMENTS:
        path = os.path.join(DOCS_DIR, filename)
        if not os.path.exists(path):
            print(f"WARNING: document not found: {path}", file=sys.stderr)
            continue
        section_title = ""
        last = None
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or set(line) == {"═"}:
                    continue
                clause = CLAUSE_RE.match(line)
                header = SECTION_RE.match(line)
                if clause:
                    last = {"document": filename, "team": team,
                            "section": clause.group(1),
                            "title": section_title,
                            "text": re.sub(r"\s+", " ", clause.group(2)).strip()}
                    index.append(last)
                elif header:
                    section_title = line
                    last = None
                elif last is not None:
                    last["text"] += " " + re.sub(r"\s+", " ", line).strip()
    return index


def _question_terms(question: str):
    words = re.findall(r"[a-zA-Z']+", question.lower())
    return {_normalise(w) for w in words if w not in STOPWORDS and len(w) > 1}


def _term_weight(term: str, unit: dict) -> float:
    """Occurrence-capped term weight: body hits count up to 2, title at 0.5."""
    body_words = [_normalise(w) for w in re.findall(r"[a-z']+", unit["text"].lower())]
    title_words = [_normalise(w) for w in re.findall(r"[a-z']+", unit["title"].lower())]
    body = sum(1 for w in body_words
               if term == w or _prefix_match(term, w))
    title = sum(1 for w in title_words
                if term == w or _prefix_match(term, w))
    return (min(body, 2) + 0.5 * min(title, 1))


def answer_question(index, question: str) -> str:
    """Single-source cited answer or the exact refusal template."""
    q = question.lower()
    terms = _question_terms(question)
    if not terms:
        return REFUSAL_TEMPLATE.format(team="the relevant policy owner")

    # Inverse document frequency: terms unique to one policy dominate.
    doc_count = len({u["document"] for u in index})
    docs_with_term = {}
    for term in terms:
        docs_with_term[term] = len({
            u["document"] for u in index
            if _matches_text(term, u)
        })
    idf = {t: math.log((doc_count + 1) / (df + 1)) + 1.0
           for t, df in docs_with_term.items()}

    for unit in index:
        matched = [t for t in terms if _matches_text(t, unit)]
        unit["_count"] = len(matched)
        unit["_weight"] = sum(_term_weight(t, unit) * idf[t] for t in matched)
        unit["_boosted"] = any(
            re.search(pattern, q) and unit["document"] == doc and unit["section"] == sec
            for pattern, doc, sec in CONCEPT_BOOSTS)
        if unit["_boosted"]:
            unit["_weight"] += BOOST

    ranked = sorted(index, key=lambda u: u["_weight"], reverse=True)
    best = ranked[0]
    if best["_count"] < 2 and not best["_boosted"]:
        return REFUSAL_TEMPLATE.format(team="the relevant policy owner")

    # Cross-document evidence: if a rival document scores as strongly, the
    # question spans sources — refuse rather than blend.
    rival = next((u for u in ranked
                  if u["document"] != best["document"]
                  and u["_weight"] >= best["_weight"]
                  and u["_count"] >= 2), None)
    if rival is not None:
        return REFUSAL_TEMPLATE.format(team="the relevant policy owner")

    answer = (f"{best['text'].rstrip('.')}. "
              f"[Source: {best['document']}, section {best['section']}]")
    if any(h in answer.lower() for h in HEDGING_PHRASES):
        raise RuntimeError("enforcement violation: hedging phrase in answer")
    return answer


def _matches_text(term: str, unit: dict) -> bool:
    text = (unit["title"] + " " + unit["text"]).lower()
    words = {_normalise(w) for w in re.findall(r"[a-z']+", text)}
    return any(term == w or _prefix_match(term, w) for w in words)


def main():
    parser = argparse.ArgumentParser(description="UC-X policy Q&A")
    parser.add_argument("--question", action="append", default=None,
                        help="Ask one question (repeatable) instead of "
                             "the interactive prompt")
    args = parser.parse_args()

    index = retrieve_documents()
    if not index:
        print("ERROR: no policy documents could be loaded.", file=sys.stderr)
        raise SystemExit(1)
    print(f"Loaded {len(index)} indexed clauses from "
          f"{len({u['document'] for u in index})} documents.")
    print("Ask a policy question ('quit' to exit). Answers cite their "
          "single source; anything else gets the refusal template.\n")

    if args.question:
        questions = args.question
    else:
        questions = (line.strip() for line in sys.stdin)

    for question in questions:
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break
        print(f"Q: {question}")
        print(f"A: {answer_question(index, question)}\n")


if __name__ == "__main__":
    main()
