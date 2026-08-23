"""
UC-X — Ask My Documents
Deterministic single-source policy Q&A over three CMC policy documents.
Every answer is either verbatim clause text from exactly ONE document with
inline citations, or the exact refusal template. Never blends documents.

Run:            python app.py
One-shot:       python app.py --ask "Can I carry forward unused annual leave?"
Run all tests:  python app.py --run-tests
"""
import argparse
import math
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "policy-documents")

DOCUMENT_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

BANNED_HEDGES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am",
    "do", "does", "did", "can", "could", "will", "would", "shall", "should",
    "may", "might", "must", "i", "me", "my", "we", "our", "you", "your",
    "he", "she", "it", "its", "they", "them", "their", "this", "that",
    "these", "those", "of", "for", "to", "in", "on", "at", "by", "with",
    "from", "and", "or", "if", "as", "when", "what", "which", "who", "whom",
    "whose", "how", "why", "where", "there", "here", "about", "into", "up",
}

# Curated domain phrase index: phrase -> list of (document, section).
# Deterministic stage-1 retrieval. Phrases are matched against the
# normalised question (lowercased, whitespace collapsed). The document with
# the most specific hits wins; only that document's sections are used.
DOMAIN_PHRASE_INDEX = {
    # HR — annual leave / carry forward / encashment
    "carry forward": [("policy_hr_leave.txt", "2.6"), ("policy_hr_leave.txt", "2.7")],
    "carry-forward": [("policy_hr_leave.txt", "2.6"), ("policy_hr_leave.txt", "2.7")],
    "unused annual leave": [("policy_hr_leave.txt", "2.6"), ("policy_hr_leave.txt", "2.7")],
    "annual leave": [
        ("policy_hr_leave.txt", "2.1"), ("policy_hr_leave.txt", "2.6"),
        ("policy_hr_leave.txt", "7.1"),
    ],
    "leave encashment": [("policy_hr_leave.txt", "7.1"), ("policy_hr_leave.txt", "7.2"),
                         ("policy_hr_leave.txt", "7.3")],
    "encash": [("policy_hr_leave.txt", "7.1"), ("policy_hr_leave.txt", "7.2"),
               ("policy_hr_leave.txt", "7.3")],
    # HR — sick leave
    "sick leave": [("policy_hr_leave.txt", "3.1"), ("policy_hr_leave.txt", "3.2"),
                   ("policy_hr_leave.txt", "3.3")],
    "medical certificate": [("policy_hr_leave.txt", "3.2"),
                            ("policy_hr_leave.txt", "3.4")],
    # HR — maternity / paternity
    "maternity leave": [("policy_hr_leave.txt", "4.1"), ("policy_hr_leave.txt", "4.2")],
    "paternity leave": [("policy_hr_leave.txt", "4.3"), ("policy_hr_leave.txt", "4.4")],
    # HR — LWP
    "leave without pay": [("policy_hr_leave.txt", "5.1"), ("policy_hr_leave.txt", "5.2"),
                          ("policy_hr_leave.txt", "5.3")],
    "lwp": [("policy_hr_leave.txt", "5.1"), ("policy_hr_leave.txt", "5.2"),
            ("policy_hr_leave.txt", "5.3")],
    "unpaid leave": [("policy_hr_leave.txt", "5.1"), ("policy_hr_leave.txt", "5.2"),
                     ("policy_hr_leave.txt", "5.3")],
    # HR — holidays / grievances / applications
    "public holiday": [("policy_hr_leave.txt", "6.1"), ("policy_hr_leave.txt", "6.2")],
    "compensatory off": [("policy_hr_leave.txt", "6.2"), ("policy_hr_leave.txt", "6.3")],
    "leave application": [("policy_hr_leave.txt", "2.3"), ("policy_hr_leave.txt", "2.4")],
    "leave grievance": [("policy_hr_leave.txt", "8.1")],
    # IT — corporate devices / software installation
    "install": [("policy_it_acceptable_use.txt", "2.3"),
                ("policy_it_acceptable_use.txt", "2.4")],
    "installation": [("policy_it_acceptable_use.txt", "2.3"),
                     ("policy_it_acceptable_use.txt", "2.4")],
    "slack": [("policy_it_acceptable_use.txt", "2.3"),
              ("policy_it_acceptable_use.txt", "2.4")],
    "install software": [("policy_it_acceptable_use.txt", "2.3"),
                         ("policy_it_acceptable_use.txt", "2.4")],
    "install on my work laptop": [("policy_it_acceptable_use.txt", "2.3"),
                                  ("policy_it_acceptable_use.txt", "2.4")],
    "install on work laptop": [("policy_it_acceptable_use.txt", "2.3"),
                               ("policy_it_acceptable_use.txt", "2.4")],
    "software on corporate": [("policy_it_acceptable_use.txt", "2.3"),
                              ("policy_it_acceptable_use.txt", "2.4")],
    "software catalogue": [("policy_it_acceptable_use.txt", "2.4")],
    "corporate device": [("policy_it_acceptable_use.txt", "2.1"),
                         ("policy_it_acceptable_use.txt", "2.2")],
    "endpoint security agent": [("policy_it_acceptable_use.txt", "2.6")],
    # IT — BYOD / personal devices
    "personal device": [("policy_it_acceptable_use.txt", "3.1"),
                        ("policy_it_acceptable_use.txt", "3.2"),
                        ("policy_it_acceptable_use.txt", "3.3")],
    "personal phone": [("policy_it_acceptable_use.txt", "3.1"),
                       ("policy_it_acceptable_use.txt", "3.2")],
    "personal laptop": [("policy_it_acceptable_use.txt", "3.1"),
                        ("policy_it_acceptable_use.txt", "3.2"),
                        ("policy_it_acceptable_use.txt", "3.3")],
    "personal mobile": [("policy_it_acceptable_use.txt", "3.1"),
                        ("policy_it_acceptable_use.txt", "3.2")],
    "byod": [("policy_it_acceptable_use.txt", "3.1"),
             ("policy_it_acceptable_use.txt", "3.2"),
             ("policy_it_acceptable_use.txt", "3.3")],
    "guest wifi": [("policy_it_acceptable_use.txt", "3.3")],
    # IT — passwords / data handling / email
    "share my password": [("policy_it_acceptable_use.txt", "4.1"),
                          ("policy_it_acceptable_use.txt", "4.2")],
    "password": [("policy_it_acceptable_use.txt", "4.1"), ("policy_it_acceptable_use.txt", "4.3")],
    "multi-factor": [("policy_it_acceptable_use.txt", "4.4")],
    "mfa": [("policy_it_acceptable_use.txt", "4.4")],
    "personal email account": [("policy_it_acceptable_use.txt", "5.2")],
    "confidential": [("policy_it_acceptable_use.txt", "5.1"),
                     ("policy_it_acceptable_use.txt", "5.2"),
                     ("policy_it_acceptable_use.txt", "5.3")],
    "personal cloud": [("policy_it_acceptable_use.txt", "5.1")],
    "mass email": [("policy_it_acceptable_use.txt", "6.3")],
    # Finance — travel
    "local travel": [("policy_finance_reimbursement.txt", "2.1")],
    "outstation": [("policy_finance_reimbursement.txt", "2.2"),
                   ("policy_finance_reimbursement.txt", "2.4"),
                   ("policy_finance_reimbursement.txt", "2.5")],
    "air travel": [("policy_finance_reimbursement.txt", "2.3")],
    "business class": [("policy_finance_reimbursement.txt", "2.3")],
    "hotel": [("policy_finance_reimbursement.txt", "2.4")],
    "daily allowance": [("policy_finance_reimbursement.txt", "2.5"),
                        ("policy_finance_reimbursement.txt", "2.6")],
    " da ": [("policy_finance_reimbursement.txt", "2.5"),
             ("policy_finance_reimbursement.txt", "2.6")],
    "da and meal": [("policy_finance_reimbursement.txt", "2.5"),
                    ("policy_finance_reimbursement.txt", "2.6")],
    "meal receipt": [("policy_finance_reimbursement.txt", "2.5"),
                     ("policy_finance_reimbursement.txt", "2.6")],
    "meal expense": [("policy_finance_reimbursement.txt", "2.6")],
    # Finance — WFH equipment
    "home office equipment allowance": [("policy_finance_reimbursement.txt", "3.1"),
                                        ("policy_finance_reimbursement.txt", "3.2"),
                                        ("policy_finance_reimbursement.txt", "3.3")],
    "equipment allowance": [("policy_finance_reimbursement.txt", "3.1"),
                            ("policy_finance_reimbursement.txt", "3.2"),
                            ("policy_finance_reimbursement.txt", "3.3")],
    "wfh allowance": [("policy_finance_reimbursement.txt", "3.1"),
                      ("policy_finance_reimbursement.txt", "3.5")],
    # Finance — training
    "training": [("policy_finance_reimbursement.txt", "4.1"),
                 ("policy_finance_reimbursement.txt", "4.2")],
    "course fee": [("policy_finance_reimbursement.txt", "4.2")],
    "certification": [("policy_finance_reimbursement.txt", "4.3"),
                      ("policy_finance_reimbursement.txt", "4.4")],
    # Finance — mobile/internet/submission
    "mobile phone reimbursement": [("policy_finance_reimbursement.txt", "5.1")],
    "internet reimbursement": [("policy_finance_reimbursement.txt", "5.2")],
    "claim submit": [("policy_finance_reimbursement.txt", "1.3"),
                     ("policy_finance_reimbursement.txt", "6.1")],
    "submit claim": [("policy_finance_reimbursement.txt", "1.3"),
                     ("policy_finance_reimbursement.txt", "6.1")],
    "reimburse": [("policy_finance_reimbursement.txt", "1.1"),
                  ("policy_finance_reimbursement.txt", "1.2")],
}


def retrieve_documents():
    """Skill: retrieve_documents. Parse each policy file into clauses."""
    index = {}
    for filename in DOCUMENT_FILES:
        path = os.path.join(DATA_DIR, filename)
        if not os.path.isfile(path):
            raise SystemExit("Missing required document: %s" % path)
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        reference = None
        clauses = []
        current = None  # [section, text_parts]
        clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")
        for line in lines:
            stripped = line.strip()
            m = clause_re.match(stripped)
            if m:
                if current:
                    clauses.append({"section": current[0], "text": " ".join(current[1])})
                current = [m.group(1), [m.group(2)]]
                continue
            if not stripped or set(stripped) == {"═"}:
                continue
            ref_m = re.match(r"^Document Reference:\s*(\S+)", stripped)
            if ref_m:
                reference = ref_m.group(1)
                continue
            if stripped.endswith(":") or re.match(r"^\d+\.\s+[A-Z]", stripped):
                continue
            if current is not None and line.startswith("    "):
                current[1].append(stripped)
        if current:
            clauses.append({"section": current[0], "text": " ".join(current[1])})
        if not clauses or not reference:
            raise SystemExit("Unreadable or unparsable document: %s" % path)
        index[filename] = {"reference": reference, "clauses": clauses}
    return index


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def singular(token):
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokenize(text):
    tokens = []
    for tok in normalize(text).split():
        if tok in STOPWORDS:
            continue
        tokens.append(singular(tok))
    return tokens


def find_domain_hits(question_norm):
    """Stage 1: curated phrase index (whole-word match). Returns {doc: set(sections)}."""
    hits = {}
    for phrase, anchors in DOMAIN_PHRASE_INDEX.items():
        p = normalize(phrase)
        if re.search(r"\b" + re.escape(p) + r"\b", question_norm):
            for doc, sec in anchors:
                hits.setdefault(doc, set()).add(sec)
    return hits


def keyword_scores(question, index):
    """Stage 2: IDF-weighted token overlap per clause. Returns list of
    (score, matched_token_count, doc, section, text), best first."""
    q_tokens = set(tokenize(question))
    all_clauses = [(doc, c["section"], c["text"]) for doc, d in index.items() for c in d["clauses"]]
    df = {}
    for _, _, text in all_clauses:
        for t in set(tokenize(text)):
            df[t] = df.get(t, 0) + 1
    n = len(all_clauses)

    def idf(t):
        return math.log((n + 1) / (df.get(t, 0) + 1)) + 1.0

    scored = []
    for doc, sec, text in all_clauses:
        c_tokens = set(tokenize(text))
        matched = [t for t in q_tokens if t in c_tokens]
        score = sum(idf(t) for t in matched)
        scored.append((score, len(matched), doc, sec, text))
    scored.sort(key=lambda x: (-x[0], doc_sort_key(x[2]), x[3]))
    return scored


def doc_sort_key(doc):
    return DOCUMENT_FILES.index(doc)


def answer_question(question, index):
    """Skill: answer_question. Returns (answer_text, source_doc_or_None)."""
    q_norm = normalize(question)
    domain_hits = find_domain_hits(q_norm)

    if domain_hits:
        best_doc = max(domain_hits.items(),
                       key=lambda kv: (len(kv[1]), -doc_sort_key(kv[0])))[0]
        sections = sorted(domain_hits[best_doc])
        lines = ["[Source: %s]" % best_doc]
        for sec in sections:
            clause = next(c for c in index[best_doc]["clauses"] if c["section"] == sec)
            lines.append('"%s" (%s §%s)' % (clause["text"], index[best_doc]["reference"], sec))
        answer = "\n".join(lines)
        check_hedges(answer)
        return answer, best_doc

    scored = keyword_scores(question, index)
    # Fallback confidence gate: require >=2 distinct content-token matches on
    # the best clause, so single generic words ("working") cannot trigger an
    # answer and uncovered topics get the refusal template.
    best_score, best_matches, best_doc, _, _ = scored[0] if scored else (0.0, 0, None, "", "")
    if best_doc is None or best_matches < 2:
        return REFUSAL_TEMPLATE, None

    cutoff = 0.75 * best_score
    picked = [s for s in scored if s[0] >= cutoff and s[1] == best_doc][:3]
    lines = ["[Source: %s]" % best_doc]
    for score, matches, doc, sec, text in sorted(picked, key=lambda x: (doc_sort_key(x[2]), x[3])):
        lines.append('"%s" (%s §%s)' % (text, index[best_doc]["reference"], sec))
    answer = "\n".join(lines)
    check_hedges(answer)
    return answer, best_doc


def check_hedges(answer):
    low = answer.lower()
    for phrase in BANNED_HEDGES:
        if phrase in low:
            raise SystemExit(
                "Output guard tripped: banned hedging phrase %r would have been emitted." % phrase)


TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?",
     {"expect_doc": "policy_hr_leave.txt", "must_cite": ["2.6"]}),
    ("Can I install Slack on my work laptop?",
     {"expect_doc": "policy_it_acceptable_use.txt", "must_cite": ["2.3"]}),
    ("What is the home office equipment allowance?",
     {"expect_doc": "policy_finance_reimbursement.txt", "must_cite": ["3.1"]}),
    ("Can I use my personal phone for work files from home?",
     {"expect_doc": "policy_it_acceptable_use.txt", "must_cite": ["3.1"],
      "forbid_docs": ["policy_finance_reimbursement.txt", "policy_hr_leave.txt"]}),
    ("What is the company view on flexible working culture?",
     {"expect_refusal": True}),
    ("Can I claim DA and meal receipts on the same day?",
     {"expect_doc": "policy_finance_reimbursement.txt", "must_cite": ["2.6"]}),
    ("Who approves leave without pay?",
     {"expect_doc": "policy_hr_leave.txt", "must_cite": ["5.2"]}),
]


def run_tests(index):
    failures = 0
    print("=" * 70)
    print("UC-X validation — 7 test questions")
    print("=" * 70)
    for question, expect in TEST_QUESTIONS:
        answer, src = answer_question(question, index)
        ok = True
        problems = []
        if expect.get("expect_refusal"):
            if answer != REFUSAL_TEMPLATE:
                ok = False
                problems.append("expected exact refusal template")
        else:
            if answer == REFUSAL_TEMPLATE:
                ok = False
                problems.append("unexpected refusal")
            else:
                if src != expect.get("expect_doc"):
                    ok = False
                    problems.append("source=%r expected %r" % (src, expect.get("expect_doc")))
                for bad_doc in expect.get("forbid_docs", []):
                    if bad_doc in (answer or ""):
                        ok = False
                        problems.append("blended in forbidden doc %s" % bad_doc)
                for cite in expect.get("must_cite", []):
                    if ("§%s)" % cite) not in answer:
                        ok = False
                        problems.append("missing citation §%s" % cite)
        try:
            check_hedges(answer)
        except SystemExit as exc:
            ok = False
            problems.append(str(exc))
        status = "PASS" if ok else "FAIL"
        print("\n[%s] %s" % (status, question))
        for line in answer.splitlines():
            print("    " + line)
        for p in problems:
            print("    !! %s" % p)
        if not ok:
            failures += 1
    print("\n%d/%d passed" % (len(TEST_QUESTIONS) - failures, len(TEST_QUESTIONS)))
    return 1 if failures else 0


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--ask", metavar="QUESTION", help="ask one question and exit")
    parser.add_argument("--run-tests", action="store_true", help="run the 7 validation questions")
    args = parser.parse_args()

    index = retrieve_documents()

    if args.run_tests:
        sys.exit(run_tests(index))

    if args.ask is not None:
        answer, _ = answer_question(args.ask, index)
        print(answer)
        return

    print("UC-X — Ask My Documents (CMC policy Q&A)")
    print("Answered strictly from: %s" % ", ".join(DOCUMENT_FILES))
    print("Type your question, or 'quit' to exit.\n")
    while True:
        try:
            question = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break
        answer, _ = answer_question(question, index)
        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()
