"""
UC-X app.py — "Ask My Documents"

A grounded, single-source Q&A CLI over three CMC policy documents:
  - policy_hr_leave.txt
  - policy_it_acceptable_use.txt
  - policy_finance_reimbursement.txt

Design goal (see agents.md / skills.md / README.md):
  - Every factual answer comes from exactly ONE clause of ONE document and is cited
    as "<filename> §<clause>". Two documents are NEVER blended into one answer.
  - Questions not covered by a single document get the refusal template, verbatim.
  - No hedging phrases are ever emitted — it is answer-with-citation or refuse.

Approach (deterministic, matching the UC-0A/0B/0C pattern — no LLM at runtime):
  retrieve_documents parses the files into numbered clauses and builds an IDF table.
  answer_question scores every clause by IDF-weighted term overlap (clause body +
  section heading), then applies a coverage gate and a cross-document ambiguity gate:
    - a single clause must cover >= COVERAGE_MIN of the question's content terms,
      otherwise the question is "not covered"  -> refuse;
    - if clauses from two different documents both clear that bar, the question is
      cross-document ambiguous            -> refuse (this is the anti-blend rule);
    - otherwise the single highest-scoring clause is returned, with its citation.
"""
import argparse
import math
import os
import re
import sys

# ---------------------------------------------------------------------------
# The three policy documents (default locations, relative to this file).
# ---------------------------------------------------------------------------

DOC_FILENAMES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)


def _default_doc_paths():
    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.normpath(os.path.join(here, "..", "data", "policy-documents"))
    return [os.path.join(base, name) for name in DOC_FILENAMES]


# The refusal template — used verbatim, defined once, identical to agents.md.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)

# ---------------------------------------------------------------------------
# Retrieval tuning constants.
# ---------------------------------------------------------------------------

# A clause must cover at least this share of the question's content terms for the
# question to count as "covered". Below this -> refuse (not covered / too weak).
# Matching is done against clause BODIES only: section headings such as
# "WORK FROM HOME EQUIPMENT" contain generic words ("work", "home") that otherwise
# match almost every clause and drown out the substantive text.
COVERAGE_MIN = 0.5
# Repeated terms help, but with diminishing returns.
TF_CAP = 3
# Action / obligation verbs that identify what a clause is *about*. When one of these
# is both asked and present in a clause body, it is the crux of the question ("who
# APPROVES", "can I INSTALL"), so its match is weighted far above incidental nouns.
INTENT_MULTIPLIER = 3.0
INTENT_FOCUS = frozenset({
    "approv", "install", "carry", "forward", "encash", "reimburs",
    "claim", "forfeit", "share", "transmit", "connect",
})

# Acronym vocabulary the documents define but employees ask about in words. Each
# acronym below actually appears in a clause body, so expanding the question with it
# lets "leave without pay" reach the clauses that say "LWP", etc. Query-side only.
PHRASE_EXPANSIONS = {
    "leave without pay": "lwp",
    "loss of pay": "lop",
    "daily allowance": "da",
    "multi factor authentication": "mfa",
    "multi-factor authentication": "mfa",
}

# ---------------------------------------------------------------------------
# Parsing / tokenisation.
# ---------------------------------------------------------------------------

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+(.+)$")
SEPARATOR_RE = re.compile(r"^[\u2550=\-\s]+$")

STOPWORDS = frozenset("""
a an the this that these those and or but if then so of to in on at by for from with
without within into over under about as is are was were be been being do does did done
can could will would shall should may might must i you he she it we they me my your our
their his her its what which who whom whose when where why how not no yes any some all
each every use using used get got have has had am here there than too very just also
please tell explain want need know about
""".split())

# Domain lemmas: map surface forms to a shared stem so, e.g., "approves" (question)
# matches "approval" (clause). Applied before the generic suffix stripper.
LEMMA = {
    "approves": "approv", "approve": "approv", "approved": "approv",
    "approval": "approv", "approving": "approv", "approver": "approv",
    "approvers": "approv", "preapproved": "approv", "pre-approved": "approv",
    "installs": "install", "installed": "install", "installing": "install",
    "installation": "install",
    "reimburse": "reimburs", "reimbursed": "reimburs", "reimbursement": "reimburs",
    "reimbursements": "reimburs", "reimbursable": "reimburs",
    "forfeit": "forfeit", "forfeited": "forfeit", "forfeiture": "forfeit",
    "encash": "encash", "encashed": "encash", "encashment": "encash",
    "phones": "phone", "smartphone": "phone", "smartphones": "phone",
    "leaves": "leave", "files": "file", "laptops": "laptop", "receipts": "receipt",
    "devices": "device", "allowances": "allowance", "claimed": "claim",
    "claiming": "claim", "claims": "claim", "certificates": "certificate",
    "certification": "certificate", "certifications": "certificate",
    "carryforward": "carry", "carried": "carry",
}


def normalize(word):
    """Lowercase lemma/stem for a single already-lowercased word."""
    if word in LEMMA:
        return LEMMA[word]
    for suffix in ("ing", "ed"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def tokenize(text):
    """Return a list of normalized content tokens (stopwords removed)."""
    raw = re.findall(r"[a-z0-9]+", text.lower())
    out = []
    for w in raw:
        if w in STOPWORDS:
            continue
        n = normalize(w)
        if n and n not in STOPWORDS:
            out.append(n)
    return out


# ---------------------------------------------------------------------------
# Skill 1: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(paths=None):
    """Load the policy files and build a searchable clause index.

    Returns a dict:
      {
        "clauses": [ {doc, section_number, section_title, number, text,
                      body_tf: {token: count}, tokens: set, title_tokens: set}, ... ],
        "idf": {token: idf_value},
        "docs": [filenames...],
      }
    """
    if paths is None:
        paths = _default_doc_paths()

    clauses = []
    docs = []
    for path in paths:
        filename = os.path.basename(path)
        docs.append(filename)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            sys.exit(
                f"ERROR: cannot read policy file '{path}': {getattr(exc, 'strerror', exc)}. "
                f"All three documents are required; refusing to run on a partial corpus."
            )

        section_number = "0"
        section_title = "GENERAL"
        current = None
        for line in lines:
            stripped = line.strip()
            if not stripped or SEPARATOR_RE.match(stripped):
                continue

            clause_match = CLAUSE_RE.match(stripped)
            section_match = SECTION_RE.match(stripped)

            if clause_match:
                current = {
                    "doc": filename,
                    "section_number": section_number,
                    "section_title": section_title,
                    "number": clause_match.group(1),
                    "text": clause_match.group(2).strip(),
                }
                clauses.append(current)
            elif section_match:
                section_number = section_match.group(1)
                section_title = section_match.group(2).strip()
                current = None
            else:
                # Continuation of the previous clause (wrapped line).
                if current is not None:
                    current["text"] = (current["text"] + " " + stripped).strip()

    # Per-clause token structures.
    for c in clauses:
        body = tokenize(c["text"])
        tf = {}
        for t in body:
            tf[t] = tf.get(t, 0) + 1
        c["body_tf"] = tf
        c["tokens"] = set(body)

    # IDF over clause bodies (title tokens reuse the same table).
    n = len(clauses) or 1
    df = {}
    for c in clauses:
        for t in c["tokens"]:
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log(n / dfi) for t, dfi in df.items()}

    return {"clauses": clauses, "idf": idf, "docs": docs}


# ---------------------------------------------------------------------------
# Skill 2: answer_question
# ---------------------------------------------------------------------------

def _score_clause(clause, q_tokens, idf):
    """Return (score, matched_token_set) for one clause against the question.

    Matching is against the clause BODY only. A query term that is an action/intent
    verb (see INTENT_FOCUS) gets a large multiplier when it appears in the body, so
    the clause that actually governs the asked action outranks clauses that merely
    share incidental nouns with the question.
    """
    score = 0.0
    matched = set()
    for t in q_tokens:
        weight = idf.get(t, 0.0)
        if weight <= 0.0:
            continue
        body_tf = min(clause["body_tf"].get(t, 0), TF_CAP)
        if body_tf == 0:
            continue
        matched.add(t)
        contribution = weight * body_tf
        if t in INTENT_FOCUS:
            contribution *= INTENT_MULTIPLIER
        score += contribution
    return score, matched


def answer_question(question, index):
    """Answer one question from the index, or refuse. Never blends, never hedges."""
    if not question or not question.strip():
        return {"refused": True, "answer": REFUSAL_TEMPLATE, "citation": "",
                "reason": "empty question"}

    # Preserve distinct content terms, in order, for a stable coverage denominator.
    q_tokens = list(dict.fromkeys(tokenize(question)))
    # Expand known multi-word policy terms into the acronyms the clauses actually use.
    raw = question.lower()
    for phrase, acronym in PHRASE_EXPANSIONS.items():
        if phrase in raw and acronym not in q_tokens:
            q_tokens.append(acronym)
    if not q_tokens:
        return {"refused": True, "answer": REFUSAL_TEMPLATE, "citation": "",
                "reason": "no content terms in question"}

    idf = index["idf"]

    # Coverage is measured only against terms that actually exist in the documents.
    # Filler and out-of-vocabulary words ("while", "still", "flexible") can never be
    # matched, so counting them would unfairly drag coverage down (false refusals).
    in_vocab = [t for t in q_tokens if idf.get(t, 0.0) > 0.0]
    denom = len(in_vocab)
    if denom == 0:
        # Nothing the question asks about appears in any document.
        return {"refused": True, "answer": REFUSAL_TEMPLATE, "citation": "",
                "reason": "no question term appears in the documents"}

    scored = []
    for c in index["clauses"]:
        score, matched = _score_clause(c, q_tokens, idf)
        if matched:
            coverage = len(matched) / denom
            scored.append((score, coverage, matched, c))

    # A clause "qualifies" as a real answer if it covers at least COVERAGE_MIN of the
    # in-vocab terms AND either matches two distinct terms or matches an action/intent
    # verb. A single incidental match on a generic word (e.g. only "work" for
    # "flexible working culture") does not qualify -> the question is not covered.
    qualifying = [
        (score, cov, matched, c) for score, cov, matched, c in scored
        if cov >= COVERAGE_MIN and (len(matched) >= 2 or (matched & INTENT_FOCUS))
    ]
    if not qualifying:
        return {"refused": True, "answer": REFUSAL_TEMPLATE, "citation": "",
                "reason": "no single clause covers enough of the question"}

    # Anti-blend gate: if qualifying clauses come from two or more documents, the
    # question is cross-document ambiguous -> refuse rather than pick or merge.
    covering_docs = {c["doc"] for _, _, _, c in qualifying}
    if len(covering_docs) >= 2:
        return {"refused": True, "answer": REFUSAL_TEMPLATE, "citation": "",
                "reason": f"cross-document ambiguity across {sorted(covering_docs)}"}

    # Single-source answer: within the one covering document, return its highest-scoring
    # clause. The answer is composed from that one clause only, so nothing is blended
    # and no fact outside it can appear.
    doc = next(iter(covering_docs))
    in_doc = [row for row in scored if row[3]["doc"] == doc]
    in_doc.sort(key=lambda r: (r[0], r[1]), reverse=True)
    best_score, best_cov, _, best = in_doc[0]
    citation = f"{best['doc']} \u00a7{best['number']}"
    answer = f"{best['text']} [{citation}]"
    return {"refused": False, "answer": answer, "citation": citation,
            "reason": f"single-source, coverage {best_cov:.2f}, score {best_score:.2f}"}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

BANNER = (
    "Ask My Documents \u2014 CMC policy assistant\n"
    "Indexed: policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt\n"
    "Answers are single-source and cited. Not-covered questions are refused.\n"
    "Type your question, or 'quit' to exit.\n"
)

SELFTEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def _run_selftest(index):
    print("=== SELF-TEST: the 7 README questions ===\n")
    for q in SELFTEST_QUESTIONS:
        result = answer_question(q, index)
        print(f"Q: {q}")
        if result["refused"]:
            print("A: [REFUSED]")
            print("   " + result["answer"].replace("\n", "\n   "))
        else:
            print(f"A: {result['answer']}")
        print(f"   (why: {result['reason']})\n")


def main():
    parser = argparse.ArgumentParser(
        description="Ask questions about CMC HR/IT/Finance policy — single-source, cited answers."
    )
    parser.add_argument("--docs", nargs="*", default=None,
                        help="Optional override for the three policy file paths.")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the 7 README test questions and exit.")
    parser.add_argument("--ask", default=None,
                        help="Ask a single question non-interactively and exit.")
    args = parser.parse_args()

    index = retrieve_documents(args.docs)

    if args.selftest:
        _run_selftest(index)
        return

    if args.ask is not None:
        result = answer_question(args.ask, index)
        print(result["answer"])
        return

    print(BANNER)
    while True:
        try:
            question = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"quit", "exit", "q"}:
            break
        if not question:
            continue
        result = answer_question(question, index)
        print()
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()
