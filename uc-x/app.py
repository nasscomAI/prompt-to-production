"""
UC-X — Ask My Documents

CRAFT cycle 1 fix: cross-document blending, hedged hallucination, missing citations.

The baseline transcript (uc-x/baseline_transcript.txt) shows all three failures.
Asked who approves leave without pay, it stitched HR 5.1, 1.1 and 2.1 together
and never mentioned the two approvers in 5.2. Asked about flexible working
culture — which appears in none of the three documents — it opened with "While
not explicitly covered, it is generally understood that" and then answered
anyway, using HR grievance clauses and a Finance processing deadline. Nothing in
the output said which document any sentence came from.

This version answers from exactly one document, cites document and section for
every claim, refuses with a fixed template when the question is not covered, and
fails its own test suite if a banned hedging phrase appears anywhere in an answer.

Usage:
    python app.py                    # interactive
    python app.py --ask "..."        # one question
    python app.py --test-suite       # the 7 README questions, scored
"""

import argparse
import math
import os
import re
import sys


# --------------------------------------------------------------------------
# Enforcement constants — these come straight from agents.md.
# --------------------------------------------------------------------------

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]
DEFAULT_DOC_DIR = os.path.join("..", "data", "policy-documents")

# agents.md / REFUSAL TEMPLATE — emitted character-for-character, never edited
# per question. The team slot is a single fixed string, not a per-topic guess,
# so there is exactly one refusal string in the system.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

# agents.md / NO HEDGING — any of these in an answer is a failure, not a style note.
BANNED_PHRASES = [
    "while not explicitly", "not explicitly covered", "generally understood",
    "it is common practice", "typically", "generally", "usually", "commonly",
    "as a rule", "in most cases", "it is likely", "probably", "should be fine",
    "i think", "presumably", "in general",
]

# agents.md / RETRIEVAL — declared query expansion. This widens the search only.
# It never introduces words into an answer; answers are always verbatim clause
# text from one document.
SYNONYMS = {
    "phone": ["device", "mobile"],
    "smartphone": ["device", "mobile"],
    "laptop": ["device", "computer"],
    "computer": ["device"],
    "file": ["data", "email"],
    "wfh": ["work-from-home", "home"],
    "da": ["allowance"],
    "lwp": ["leave", "pay"],
    "reimbursed": ["reimbursement"],
    "holiday": ["holiday"],
    "sick": ["sick"],
}

# agents.md / RETRIEVAL — acronyms are expanded on the CORPUS side so that a
# question asked in words can reach a clause written in initials. LWP in HR 5.2
# is the case that matters: asked "who approves leave without pay", the clause
# that names both approvers contains neither "leave" nor "pay".
ACRONYMS = {
    "lwp": ["leave", "without", "pay"],
    "lop": ["loss", "pay"],
    "da": ["daily", "allowance"],
    "wfh": ["work", "home"],
    "byod": ["personal", "device"],
    "mfa": ["multi-factor", "authentication"],
}

BIGRAM_BONUS = 1.5

# agents.md / COVERAGE FLOOR — a question must match at least this many distinct
# content terms in one clause before any answer is produced.
MIN_MATCHED_TERMS = 2
MIN_SCORE = 1.6
# Sibling clauses in the same document and section are included when they score
# at least this fraction of the best clause.
SIBLING_RATIO = 0.7
MAX_CLAUSES = 4

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 \-&/(),']+)$")
SEPARATOR_RE = re.compile(r"^[═─\-=_\s]+$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "can", "could",
    "do", "does", "did", "i", "my", "me", "we", "our", "you", "your", "to", "of",
    "for", "on", "in", "at", "by", "with", "and", "or", "if", "it", "this",
    "that", "what", "who", "when", "where", "how", "any", "some", "from", "as",
    "will", "would", "should", "may", "might", "have", "has", "had", "am",
    "there", "their", "them", "about", "also", "than", "then", "so", "such",
}

SUFFIXES = ["ational", "ation", "ments", "ment", "ing", "ers", "er", "als",
            "al", "ed", "es", "s", "e"]


class CorpusError(Exception):
    """Raised when the policy documents cannot be loaded."""


def stem(word):
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def tokenize(text):
    words = [w for w in re.findall(r"[a-z0-9\-]+", text.lower()) if w not in STOPWORDS]
    return [stem(w) for w in words]


def variants(word):
    """The stemmed word plus its declared synonyms, all stemmed."""
    out = {stem(word)}
    for synonym in SYNONYMS.get(word, []) + SYNONYMS.get(stem(word), []):
        out.add(stem(synonym))
    return out


def expand(question):
    """Declared synonym expansion, applied to the question only."""
    raw = [w for w in re.findall(r"[a-z0-9\-]+", question.lower()) if w not in STOPWORDS]
    terms = set()
    for word in raw:
        terms |= variants(word)
    return terms


def query_bigrams(question):
    """
    Adjacent-pair variants of the question. "personal phone" reaches
    "Personal devices" in IT 3.1 but not "Personal use" in IT 2.2 — which is the
    difference between the BYOD rule and the corporate-device rule.
    """
    raw = [w for w in re.findall(r"[a-z0-9\-]+", question.lower()) if w not in STOPWORDS]
    pairs = set()
    for first, second in zip(raw, raw[1:]):
        for left in variants(first):
            for right in variants(second):
                pairs.add(left + "|" + right)
    return pairs


def clause_bigrams(text):
    tokens = tokenize(text)
    return {a + "|" + b for a, b in zip(tokens, tokens[1:])}


# --------------------------------------------------------------------------
# skills.md :: retrieve_documents
# --------------------------------------------------------------------------

def retrieve_documents(doc_dir=DEFAULT_DOC_DIR):
    """Load all three policies, indexed by document name and section number."""
    index = []
    for name in DOCUMENTS:
        path = os.path.join(doc_dir, name)
        if not os.path.isfile(path):
            raise CorpusError("Missing policy document: {}".format(path))
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()

        section = ("0", "PREAMBLE")
        clause = None
        for line in lines:
            stripped = line.strip()
            if not stripped or SEPARATOR_RE.match(stripped):
                continue
            section_match = SECTION_RE.match(stripped)
            if section_match:
                section = (section_match.group(1), section_match.group(2).strip())
                clause = None
                continue
            clause_match = CLAUSE_RE.match(stripped)
            if clause_match:
                clause = {
                    "document": name,
                    "section": section[0],
                    "section_title": section[1],
                    "id": clause_match.group(1),
                    "text": clause_match.group(2).strip(),
                }
                index.append(clause)
                continue
            if clause is not None:
                clause["text"] = (clause["text"] + " " + stripped).strip()

    if not index:
        raise CorpusError("Loaded 0 clauses — refusing to answer from an empty index.")

    total = len(index)
    document_frequency = {}
    for clause in index:
        clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()
        clause["terms"] = set(tokenize(clause["text"]))
        for acronym, expansion in ACRONYMS.items():
            if acronym in clause["terms"] or acronym in clause["text"].lower().split():
                clause["terms"] |= {stem(w) for w in expansion}
        clause["bigrams"] = clause_bigrams(clause["text"])
        for term in clause["terms"]:
            document_frequency[term] = document_frequency.get(term, 0) + 1

    idf = {t: math.log(total / (1.0 + df)) + 0.25 for t, df in document_frequency.items()}
    return {"clauses": index, "idf": idf, "total": total}


# --------------------------------------------------------------------------
# skills.md :: answer_question
# --------------------------------------------------------------------------

def score_clauses(corpus, question):
    terms = expand(question)
    pairs = query_bigrams(question)
    scored = []
    for clause in corpus["clauses"]:
        matched = terms & clause["terms"]
        if not matched:
            continue
        weight = sum(corpus["idf"].get(t, 0.5) for t in matched)
        weight /= 1.0 + 0.02 * len(clause["terms"])
        matched_pairs = pairs & clause["bigrams"]
        weight += BIGRAM_BONUS * len(matched_pairs)
        scored.append({"score": weight, "matched": matched,
                       "pairs": matched_pairs, "clause": clause})
    scored.sort(key=lambda item: -item["score"])
    return scored


def answer_question(corpus, question):
    """
    Return (answer_text, sources).

    sources is a list of (document, clause_id) — always from ONE document, or
    empty when the answer is the refusal template.
    """
    scored = score_clauses(corpus, question)

    if not scored:
        return REFUSAL_TEMPLATE, []

    best = scored[0]
    if len(best["matched"]) < MIN_MATCHED_TERMS or best["score"] < MIN_SCORE:
        # agents.md / COVERAGE FLOOR — not enough of the question is in the
        # documents to answer it. Refuse rather than assemble something.
        return REFUSAL_TEMPLATE, []

    # agents.md / SINGLE SOURCE — the winning clause fixes the document AND the
    # section. Nothing outside that section is allowed into the answer, so an
    # answer can never be assembled from two documents.
    document = best["clause"]["document"]
    section = best["clause"]["section"]

    chosen = [
        item for item in scored
        if item["clause"]["document"] == document
        and item["clause"]["section"] == section
        and item["score"] >= best["score"] * SIBLING_RATIO
    ][:MAX_CLAUSES]
    chosen.sort(key=lambda item: [int(p) for p in item["clause"]["id"].split(".")])

    lines = []
    for item in chosen:
        clause = item["clause"]
        lines.append("{} section {} — {}".format(clause["document"], clause["id"], clause["text"]))

    body = "\n".join(lines)
    footer = "Source: {} — section{} {}".format(
        document,
        "" if len(chosen) == 1 else "s",
        ", ".join(item["clause"]["id"] for item in chosen),
    )
    return body + "\n" + footer, [(document, item["clause"]["id"]) for item in chosen]


def hedging_in(text):
    lowered = text.lower()
    return [phrase for phrase in BANNED_PHRASES if phrase in lowered]


# --------------------------------------------------------------------------
# The 7 README test questions, with the behaviour each one must produce
# --------------------------------------------------------------------------

TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?",
     [("policy_hr_leave.txt", "2")], False),
    ("Can I install Slack on my work laptop?",
     [("policy_it_acceptable_use.txt", "2")], False),
    ("What is the home office equipment allowance?",
     [("policy_finance_reimbursement.txt", "3")], False),
    ("Can I use my personal phone to access work files when working from home?",
     [("policy_it_acceptable_use.txt", "3")], True),
    ("What is the company view on flexible working culture?",
     [], False),
    ("Can I claim DA and meal receipts on the same day?",
     [("policy_finance_reimbursement.txt", "2")], False),
    ("Who approves leave without pay?",
     [("policy_hr_leave.txt", "5")], False),
]


def run_test_suite(corpus):
    print("UC-X TEST SUITE — the 7 questions from the README\n")
    failures = 0

    for index, (question, expected, refusal_ok) in enumerate(TEST_QUESTIONS, 1):
        answer, sources = answer_question(corpus, question)
        refused = not sources
        documents = {doc for doc, _ in sources}

        problems = []
        if len(documents) > 1:
            problems.append("BLENDED across {}".format(sorted(documents)))
        hedges = hedging_in(answer)
        if hedges:
            problems.append("HEDGING: {}".format(hedges))

        if not expected:
            if not refused:
                problems.append("expected the refusal template, got an answer")
            elif answer != REFUSAL_TEMPLATE:
                problems.append("refusal text was altered")
        else:
            want_doc, want_section = expected[0]
            if refused and not refusal_ok:
                problems.append("refused, but {} section {} covers it".format(want_doc, want_section))
            elif not refused:
                got_doc = sources[0][0]
                got_sections = {sid.split(".")[0] for _, sid in sources}
                if got_doc != want_doc:
                    problems.append("wrong document: got {}, want {}".format(got_doc, want_doc))
                elif want_section not in got_sections:
                    problems.append("wrong section: got {}, want {}".format(sorted(got_sections), want_section))

        status = "PASS" if not problems else "FAIL"
        if problems:
            failures += 1
        print("[{}] Q{}: {}".format(status, index, question))
        for line in answer.splitlines():
            print("      {}".format(line))
        for problem in problems:
            print("      !! {}".format(problem))
        print("")

    print("=" * 70)
    print("{} of {} passed.".format(len(TEST_QUESTIONS) - failures, len(TEST_QUESTIONS)))
    return 0 if failures == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", default=DEFAULT_DOC_DIR)
    parser.add_argument("--ask", help="Ask one question and exit")
    parser.add_argument("--test-suite", action="store_true", dest="test_suite",
                        help="Run the 7 README questions and score them")
    args = parser.parse_args()

    try:
        corpus = retrieve_documents(args.docs)
    except CorpusError as exc:
        print("REFUSED: {}".format(exc), file=sys.stderr)
        return 2

    if args.test_suite:
        return run_test_suite(corpus)

    if args.ask:
        answer, _ = answer_question(corpus, args.ask)
        print(answer)
        return 0

    print("Ask my documents. Blank line or Ctrl-D to quit.")
    while True:
        try:
            question = input("\n> ").strip()
        except EOFError:
            break
        if not question:
            break
        answer, _ = answer_question(corpus, question)
        print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
