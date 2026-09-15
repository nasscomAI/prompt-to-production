"""
UC-X — Ask My Documents

Document-grounded Q&A over three CMC policy documents.

Enforcement rules from agents.md mapped to code:
  1. single-source answers only — a question is routed to ONE document;
     if two documents match equally the system refuses instead of blending
  2. no hedged phrasing is ever produced — answers quote the source clause
  3. when a question is not covered, the refusal template is used verbatim
  4. every answer cites the document name and section number
  5. conditions are never dropped — the full clause is quoted

Matching: query terms are stemmed and expanded with a small synonym table,
documents are routed by term coverage, then the best clause in the routed
document is chosen by term overlap with rare-term weighting and boosts for
action terms ("install", "claim", "approve") and scope terms ("personal",
"same"), which disambiguate the personal-phone and DA-and-meal traps.

Standard library only — runs on Python 3.9+ with no dependencies.
"""
import argparse
import os
import re
import sys

DOCUMENTS = [
    ("policy_hr_leave.txt", "policy_hr_leave.txt"),
    ("policy_it_acceptable_use.txt", "policy_it_acceptable_use.txt"),
    ("policy_finance_reimbursement.txt", "policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard practice",
]

STOPWORDS = {
    "a", "an", "the", "what", "which", "who", "whom", "whose", "why", "how",
    "can", "could", "would", "should", "will", "may", "must", "do", "does",
    "did", "is", "are", "am", "be", "been", "being", "of", "on", "in", "to",
    "for", "my", "me", "i", "we", "you", "your", "it", "its", "this", "that",
    "these", "those", "with", "when", "where", "from", "about", "at", "as",
    "if", "or", "and", "but", "by", "not", "no", "any", "all", "have", "has",
    "had", "there", "here", "get", "got", "please", "tell", "want", "know",
    "use", "used", "using",
}

SYNONYMS = {
    "phone": ["personal device", "mobile"],
    "laptop": ["personal device", "corporate device"],
    "computer": ["laptop", "personal device"],
    "slack": ["software"],
    "leave": ["annual leave"],
    "allowance": ["reimbursement"],
    "approve": ["approval", "approved", "approves"],
    "claim": ["reimburse"],
    "work": ["working", "work from home"],
    "device": ["personal device", "corporate device"],
    "pay": ["loss of pay", "lop", "lwp"],
}

# Action terms: clauses governing the query's action verb are boosted.
# Generic terms like "reimburse"/"submit" are deliberately excluded — they
# appear across many clauses and would out-rank clauses on the true topic.
ACTION_TERMS = {"install", "claim", "approv", "carry", "forfeit", "encash",
                "access"}
# Scope terms: narrow which clause applies (e.g. personal vs corporate).
# These are stored in stemmed form (personal -> person, corporate -> corpor)
# so they match the stemmed clause terms.
SCOPE_TERMS = {"person", "corpor", "written", "verbal", "same",
               "permanent", "temporary", "simultaneous"}
BOOST = 5.0
# Section titles describe scope ("LEAVE WITHOUT PAY (LWP)"), so a clause whose
# section heading matches the query is strongly preferred over a coincidental
# body-text match.
TITLE_WEIGHT = 3.0

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 &\-\/()]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def _data_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "data", "policy-documents")


def parse_document(path):
    """Return sections as a list of (num, title, [(clause_id, text)])."""
    sections = []
    current = None
    clause_id = None
    clause_lines = []

    def flush():
        nonlocal clause_id, clause_lines
        if clause_id is not None and clause_lines:
            text = re.sub(r"\s+", " ", " ".join(clause_lines)).strip()
            if current:
                current[2].append((clause_id, text))
            clause_id = None
            clause_lines = []

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            stripped = raw.strip()
            if not stripped or stripped.count("═") > 3:
                continue
            match = CLAUSE_RE.match(stripped)
            if match:
                flush()
                clause_id = match.group(1)
                clause_lines = [match.group(2)]
                continue
            match = SECTION_RE.match(stripped)
            if match:
                flush()
                current = [match.group(1), match.group(2), []]
                sections.append(current)
                continue
            if clause_id is not None:
                clause_lines.append(stripped)
    flush()
    return sections


def build_index():
    """Load all documents into a flat clause index."""
    missing = []
    index = []
    for name, _ in DOCUMENTS:
        path = os.path.join(_data_dir(), name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        for num, title, clauses in parse_document(path):
            for cid, text in clauses:
                index.append({"doc": name, "section": cid, "text": text,
                              "title": title})
    if missing:
        raise FileNotFoundError(f"Could not load policy documents: {', '.join(missing)}")
    return index


def stem(word):
    w = word.lower()
    for suffix in ("izations", "ization", "ational", "ations", "ation", "ingly",
                   "ing", "ments", "ment", "tions", "tion", "ness", "ities",
                   "ies", "ers", "es", "ed", "er", "al", "ly", "e", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 4:
            return w[:-len(suffix)]
    return w


def clause_stems(text):
    return {stem(w) for w in re.findall(r"[a-z]+", text.lower())}


def query_terms(question):
    words = [w for w in re.findall(r"[a-z]+", question.lower())
             if w not in STOPWORDS and len(w) > 2]
    terms = set()
    for word in words:
        terms.add(stem(word))
        for syn in SYNONYMS.get(word, []):
            for piece in syn.split():
                if piece in STOPWORDS or len(piece) <= 2:
                    continue
                terms.add(stem(piece))
    return terms


def answer_question(question, index):
    """Return an answer dict {doc, section, text} or the refusal template."""
    terms = query_terms(question)
    if not terms:
        return REFUSAL_TEMPLATE

    by_doc = {}
    for clause in index:
        by_doc.setdefault(clause["doc"], []).append(clause)

    route = {}
    for doc, clauses in by_doc.items():
        matched = set()
        for clause in clauses:
            matched |= terms & clause_stems(clause["text"])
        route[doc] = len(matched)

    top = max(route.values())
    if top == 0:
        return REFUSAL_TEMPLATE
    winners = [doc for doc, score in route.items() if score == top]
    if len(winners) > 1:
        return REFUSAL_TEMPLATE  # blend guard: no single source

    doc = winners[0]
    clauses = by_doc[doc]

    df = {}
    for clause in clauses:
        for term in clause_stems(clause["text"]):
            df[term] = df.get(term, 0) + 1

    best = None
    best_score = 0.0
    for clause in clauses:
        matched = terms & clause_stems(clause["text"])
        if not matched:
            continue
        score = sum(1 + 3 / (1 + df.get(term, 1)) for term in matched)
        title_matched = terms & clause_stems(clause["title"])
        score += TITLE_WEIGHT * len(title_matched)
        if matched & ACTION_TERMS:
            score += BOOST
        if matched & SCOPE_TERMS:
            score += BOOST
        if score > best_score:
            best_score = score
            best = clause

    if best is None or best_score <= 0:
        return REFUSAL_TEMPLATE

    return {"doc": best["doc"], "section": best["section"], "text": best["text"]}


def format_answer(answer):
    return (
        f"{answer['doc']} — section {answer['section']}\n"
        f"\"{answer['text']}\""
    )


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", help="Answer a single question and exit")
    args = parser.parse_args()

    try:
        index = build_index()
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    if args.question:
        answer = answer_question(args.question, index)
        print(format_answer(answer) if isinstance(answer, dict) else answer)
        return

    print("Ask a question about the policy documents (type 'quit' to exit).")
    interactive = sys.stdin.isatty()
    while True:
        try:
            if interactive:
                question = input("> ").strip()
            else:
                line = sys.stdin.readline()
                if not line:
                    break
                question = line.strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit", "bye"):
            break
        answer = answer_question(question, index)
        print(format_answer(answer) if isinstance(answer, dict) else answer)
        print()


if __name__ == "__main__":
    main()
