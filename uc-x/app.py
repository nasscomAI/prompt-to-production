"""
UC-X — Ask My Documents

The failure this file is built against is the blended answer. Given

    IT 3.1  personal devices may access CMC email and the self-service portal only
    HR      mentions approved remote work tools

a helpful system produces "Yes, you can use your personal phone for approved remote work
tools and email." Both premises are true. The conclusion appears in neither document, and
it grants permission that does not exist.

The defence here is structural, not instructional: an answer is assembled from clauses
belonging to a single document, and the single-source property is asserted before the
answer is allowed to print. There is no code path that emits sentences from two documents,
so "don't blend" is not a rule the system has to remember.

Answer text is always verbatim clause text. Paraphrase is where "Department Head and the
HR Director" becomes "requires approval", and where "email and the portal only" loses
the word "only".

Run:
    python3 app.py            # interactive
    python3 app.py --test     # the 7 README test questions
"""
import argparse
import math
import os
import re
import sys

DOC_DIR = os.path.join("..", "data", "policy-documents")
DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# Verbatim from the UC-X README. Printed character for character, never edited,
# never appended to.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Enforcement: hedged hallucination. If any of these reaches the output, the answer is
# replaced by the refusal template.
BANNED_HEDGES = [
    "while not explicitly covered", "not explicitly covered", "typically",
    "generally understood", "generally speaking", "it is common practice",
    "usually", "normally", "in most cases", "as far as i know", "it appears that",
    "should be fine", "i believe", "probably", "presumably", "it is likely",
    "you may want to", "broadly speaking", "in principle",
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "am",
    "i", "my", "me", "we", "our", "you", "your", "they", "their", "it", "its",
    "can", "could", "should", "would", "will", "shall", "may", "might", "must",
    "do", "does", "did", "done", "have", "has", "had", "of", "to", "in", "on",
    "at", "by", "for", "with", "from", "as", "and", "or", "but", "if", "then",
    "than", "that", "this", "these", "those", "what", "which", "who", "whom",
    "when", "where", "why", "how", "any", "all", "some", "no", "not", "there",
    "about", "into", "over", "under", "same", "other", "such", "per", "also",
    # Document-generic: present in nearly every clause, so they carry no signal.
    "policy", "employee", "employees", "cmc", "city", "municipal", "corporation",
    "section", "clause", "department", "please", "get", "use", "used",
}

# Retrieval aids only. These help a question's wording reach the clause that governs it;
# they can never appear in an answer, because answers are verbatim clause text.
SYNONYMS = {
    "phone": {"phone", "device", "devices", "mobile"},
    "phones": {"phone", "device", "devices", "mobile"},
    "mobile": {"mobile", "phone", "device", "devices"},
    "laptop": {"laptop", "laptops", "device", "devices", "corporate"},
    "laptops": {"laptop", "laptops", "device", "devices", "corporate"},
    "files": {"files", "data", "documents"},
    "file": {"files", "data", "documents"},
    "install": {"install", "installation", "software"},
    "installing": {"install", "installation", "software"},
    "approves": {"approval", "approved", "approve", "approves"},
    "approve": {"approval", "approved", "approve", "approves"},
    "claim": {"claim", "claims", "claimed", "reimbursable", "reimbursement"},
    "claimed": {"claim", "claims", "claimed", "reimbursable", "reimbursement"},
    "allowance": {"allowance", "reimbursable", "reimbursement", "entitled"},
    "carry": {"carry", "carried", "forward"},
    "forward": {"forward", "carry", "carried"},
    "da": {"da", "allowance", "daily"},
    "meal": {"meal", "meals"},
    "receipts": {"receipts", "receipt"},
    "unused": {"unused", "carry", "forward"},
    "home": {"home"},
    "office": {"office"},
}

# --- Thresholds. Every one of these is a refusal boundary, tuned in the CRAFT log. ---
# A match must rest on at least one term this distinctive (idf), not on common words.
DISTINCTIVE_IDF = 1.6
# A single distinctive term is a coincidence, not coverage: "flexible working culture"
# matches "working" in "within 10 working days" and nothing else.
MIN_MATCHED_TERMS = 2
# Total score floor for the best clause. Below this, the question is not covered.
MIN_SCORE = 6.0
# If the runner-up document scores at least this fraction of the winner, neither is
# clearly governing -> refuse instead of choosing.
CONTENTION_RATIO = 0.80
# Another document scoring at least this fraction of the winner holds material the
# answer did not address. Reported in the audit line, never merged into the answer.
PARTIAL_COVERAGE_RATIO = 0.35
# A document is scored by its top N clauses summed, not by its single best clause. One
# incidental match must not let an unrelated document rival a document with several
# on-topic clauses.
DOC_SCORE_CLAUSES = 3
# Clauses within this fraction of the best clause's score are included in the answer
# (same document only).
CLAUSE_INCLUDE_RATIO = 0.55
MAX_CLAUSES = 3

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z \-—&/()]+)$")
BANNER_RE = re.compile(r"^[═=]{5,}$")
REFERENCE_RE = re.compile(r"Document Reference:\s*(\S+)")


def _terms(text: str):
    """Content words, lowercased, hyphen-split, plural-normalised."""
    words = re.findall(r"[A-Za-z][A-Za-z0-9]*", text.replace("-", " ").lower())
    out = set()
    for word in words:
        if word in STOPWORDS or len(word) < 2:
            continue
        out.add(word)
        # Crude plural stripping, but never on -ss/-us: "access" must not also become
        # "acces", which would double-count one term's idf and inflate the score.
        if (word.endswith("s") and len(word) > 3
                and not word.endswith(("ss", "us", "is"))
                and word[:-1] not in STOPWORDS):
            out.add(word[:-1])
    return out


def _expand(question_terms):
    expanded = set()
    for term in question_terms:
        expanded |= SYNONYMS.get(term, {term})
    return expanded


def retrieve_documents(paths) -> dict:
    """Load all three policy files and index them by document name and section number."""
    docs, clauses = {}, []

    for path in paths:
        name = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except FileNotFoundError:
            sys.exit(
                f"ERROR: policy document not found: {path}\n"
                f"       Refusing to run on a partial document set — it would silently\n"
                f"       change which questions count as 'not covered'."
            )

        reference, heading = name, ""
        current = None
        found = 0

        for raw in lines:
            line = raw.strip()
            if not line or BANNER_RE.match(line):
                continue
            ref_match = REFERENCE_RE.search(line)
            if ref_match:
                reference = ref_match.group(1)
                continue

            clause_match = CLAUSE_RE.match(line)
            section_match = SECTION_RE.match(line)

            if clause_match:
                current = {
                    "doc": name, "reference": reference,
                    "ref": clause_match.group(1), "heading": heading,
                    "text": clause_match.group(2),
                }
                clauses.append(current)
                found += 1
            elif section_match:
                heading = section_match.group(2).strip()
                current = None
            elif current is not None:
                current["text"] += " " + line

        if not found:
            sys.exit(f"ERROR: no numbered clauses found in {path}")
        docs[name] = {"reference": reference, "clause_count": found}

    for clause in clauses:
        clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()
        clause["terms"] = _terms(clause["text"] + " " + clause["heading"])

    # Document frequency, so a distinctive term can be told from a common one.
    doc_frequency = {}
    for clause in clauses:
        for term in clause["terms"]:
            doc_frequency[term] = doc_frequency.get(term, 0) + 1

    total = len(clauses)
    idf = {term: math.log(total / count) for term, count in doc_frequency.items()}

    return {"docs": docs, "clauses": clauses, "idf": idf, "total_clauses": total}


def _score_clause(clause, query_terms, idf):
    matched = clause["terms"] & query_terms
    score = sum(idf.get(term, 0.0) for term in matched)
    best_idf = max((idf.get(term, 0.0) for term in matched), default=0.0)
    return score, matched, best_idf


def answer_question(question: str, index: dict) -> dict:
    """
    Return either a single-source cited answer or the refusal template.

    There is no code path that assembles sentences from two documents.
    """
    query_terms = _expand(_terms(question))

    scored = []
    for clause in index["clauses"]:
        score, matched, best_idf = _score_clause(clause, query_terms, index["idf"])
        if score > 0:
            scored.append((score, best_idf, matched, clause))
    scored.sort(key=lambda t: -t[0])

    def refuse(reason):
        return {"outcome": "refusal", "document": None, "citations": [],
                "text": REFUSAL_TEMPLATE, "reason": reason, "unaddressed": []}

    if not scored:
        return refuse("no clause shares a content term with the question")

    top_score, top_idf, top_matched, top_clause = scored[0]

    # Enforcement: a match resting only on common words is not coverage.
    if top_idf < DISTINCTIVE_IDF:
        return refuse(
            f"best match rests only on common terms "
            f"({', '.join(sorted(top_matched)) or 'none'}); no distinctive term matched "
            f"(highest idf {top_idf:.2f} < {DISTINCTIVE_IDF})"
        )
    if len(top_matched) < MIN_MATCHED_TERMS:
        return refuse(
            f"best match shares only {len(top_matched)} term "
            f"({', '.join(sorted(top_matched))}) with the question — a single incidental "
            f"term is coincidence, not coverage"
        )
    if top_score < MIN_SCORE:
        return refuse(f"best match score {top_score:.2f} below coverage floor "
                      f"{MIN_SCORE}")

    # Each document is scored by its top DOC_SCORE_CLAUSES clauses summed, so a document
    # with several on-topic clauses outranks one with a single incidental match.
    grouped = {}
    for score, _idf, _matched, clause in scored:
        grouped.setdefault(clause["doc"], []).append(score)
    per_doc = {doc: sum(sorted(scores, reverse=True)[:DOC_SCORE_CLAUSES])
               for doc, scores in grouped.items()}
    ranked_docs = sorted(per_doc.items(), key=lambda kv: -kv[1])

    winner, winner_score = ranked_docs[0]
    if len(ranked_docs) > 1:
        runner_up, runner_score = ranked_docs[1]
        if runner_score >= CONTENTION_RATIO * winner_score:
            # Enforcement: refuse rather than pick arbitrarily — and never answer from
            # both, which is the blend this UC is about.
            return refuse(
                f"cross-document contention: {winner} scored {winner_score:.2f} and "
                f"{runner_up} scored {runner_score:.2f} "
                f"({runner_score / winner_score:.0%} of the winner, at or above the "
                f"{CONTENTION_RATIO:.0%} threshold); neither clearly governs"
            )

    # Enforcement: clauses from the winning document ONLY.
    in_winner = [(s, c) for s, _i, _m, c in scored if c["doc"] == winner]

    # Second narrowing: pick the governing SECTION the same way, by summed top clauses.
    # Without this, "personal phone" is answered from section 2 (Corporate Devices),
    # because "mobile phones issued by CMC" outscores the BYOD section that actually
    # governs the question. Same document, wrong subject.
    section_scores = {}
    for score, clause in in_winner:
        section = clause["ref"].split(".")[0]
        section_scores.setdefault(section, []).append(score)
    governing_section = max(
        section_scores.items(),
        key=lambda kv: sum(sorted(kv[1], reverse=True)[:DOC_SCORE_CLAUSES]),
    )[0]

    section_best = max(s for s, c in in_winner
                       if c["ref"].split(".")[0] == governing_section)
    selected = [(s, c) for s, c in in_winner
                if c["ref"].split(".")[0] == governing_section
                and s >= CLAUSE_INCLUDE_RATIO * section_best][:MAX_CLAUSES]
    selected.sort(key=lambda sc: [int(p) for p in sc[1]["ref"].split(".")])

    parts = []
    citations = []
    for _score, clause in selected:
        # Verbatim. No paraphrase path exists.
        parts.append(f'{clause["doc"]} section {clause["ref"]} '
                     f'({clause["reference"]}, {clause["heading"].title()}):\n'
                     f'  "{clause["text"]}"')
        citations.append({"doc": clause["doc"], "ref": clause["ref"]})

    text = "\n".join(parts)

    # ---- Assertions. A defective answer is replaced, not shown with a warning. ----
    cited_docs = {c["doc"] for c in citations}
    if len(cited_docs) != 1:
        return refuse(f"single-source assertion failed — answer spanned {cited_docs}")

    lowered = text.lower()
    hedges = [phrase for phrase in BANNED_HEDGES if phrase in lowered]
    if hedges:
        return refuse(f"hedging phrase present in answer: {hedges}")

    # Enforcement: a limiting 'only'/'not' in a quoted clause must survive into the
    # answer. Trivially true for verbatim quotes — asserted so it stays true if the
    # rendering ever changes.
    for _score, clause in selected:
        for limiter in ("only", "not", "cannot", "must not"):
            source_count = len(re.findall(rf"\b{limiter}\b", clause["text"], re.I))
            answer_count = len(re.findall(rf"\b{limiter}\b", text, re.I))
            if source_count > answer_count:
                return refuse(f"limiter '{limiter}' lost from {clause['ref']}")

    # A compound question ("casual leave AND broadband") is answered from one document,
    # which is correct — but answering half a question without saying so is its own kind
    # of misleading. Other documents holding substantive material are named in the audit
    # line, NEVER in the answer text, so this can never become a blend.
    unaddressed = [doc for doc, score in ranked_docs[1:]
                   if score >= PARTIAL_COVERAGE_RATIO * winner_score]

    return {"outcome": "answer", "document": winner, "citations": citations,
            "text": text, "unaddressed": unaddressed,
            "reason": f"single governing document {winner} (score {winner_score:.2f}), "
                      f"governing section {governing_section}; "
                      f"{len(citations)} clause(s) cited verbatim"}


TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?",
     "HR policy section 2.6 — exact limit, exact forfeiture date"),
    ("Can I install Slack on my work laptop?",
     "IT policy section 2.3 — requires written IT approval"),
    ("What is the home office equipment allowance?",
     "Finance section 3.1 — Rs 8,000 one-time, permanent WFH only"),
    ("Can I use my personal phone to access work files when working from home?",
     "Single-source IT answer OR clean refusal — must NOT blend"),
    ("What is the company view on flexible working culture?",
     "Refusal template — not in any document"),
    ("Can I claim DA and meal receipts on the same day?",
     "Finance section 2.6 — NO, explicitly prohibited"),
    ("Who approves leave without pay?",
     "HR section 5.2 — Department Head AND HR Director, both required"),
]


def _print_result(question, result, expected=None):
    print("=" * 74)
    print(f"Q: {question}")
    if expected:
        print(f"   expected: {expected}")
    print("-" * 74)
    print(result["text"])
    print("-" * 74)
    label = "ANSWER" if result["outcome"] == "answer" else "REFUSAL"
    print(f"[{label}] {result['reason']}")
    if result["outcome"] == "answer":
        print(f"[AUDIT] sources cited: "
              f"{sorted({c['doc'] for c in result['citations']})} "
              f"(count must be 1)")
        if result.get("unaddressed"):
            print(f"[AUDIT] NOT addressed above — {', '.join(result['unaddressed'])} "
                  f"also holds material matching this question. Ask about it "
                  f"separately; it is deliberately not merged into the answer.")
    print()


def main():
    parser = argparse.ArgumentParser(description="UC-X single-source policy lookup")
    parser.add_argument("--test", action="store_true",
                        help="run the 7 README test questions and exit")
    parser.add_argument("--doc-dir", default=DOC_DIR,
                        help="directory containing the three policy documents")
    args = parser.parse_args()

    paths = [os.path.join(args.doc_dir, name) for name in DOCUMENTS]
    index = retrieve_documents(paths)

    print(f"Indexed {len(index['docs'])} documents, "
          f"{index['total_clauses']} numbered clauses:")
    for name, meta in index["docs"].items():
        print(f"  {name:<34} {meta['reference']:<12} {meta['clause_count']} clauses")
    print()

    if args.test:
        answers = refusals = 0
        for question, expected in TEST_QUESTIONS:
            result = answer_question(question, index)
            _print_result(question, result, expected)
            if result["outcome"] == "answer":
                answers += 1
                assert len({c["doc"] for c in result["citations"]}) == 1
            else:
                refusals += 1
                assert result["text"] == REFUSAL_TEMPLATE, \
                    "refusal text deviated from the template"
        print("=" * 74)
        print(f"{len(TEST_QUESTIONS)} questions: {answers} single-source answers, "
              f"{refusals} template refusals, 0 blended answers.")
        print("Every answer cited exactly one document. Every refusal was the template "
              "character for character.")
        return

    print("Ask a question about the three policy documents. Ctrl-D or 'quit' to exit.")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            return
        _print_result(question, answer_question(question, index))


if __name__ == "__main__":
    main()
