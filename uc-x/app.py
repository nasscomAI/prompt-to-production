"""
UC-X — Ask My Documents
Deterministic single-source policy Q&A over exactly three CMC policy documents.
Implements the agents.md contracts: one answer draws on ONE document and cites
filename + section number, conditions survive verbatim, cross-document
ambiguity (runner-up >= 75% of leader) refuses instead of blending, uncovered
questions get the refusal template verbatim with [relevant team] resolved
deterministically, and a hedging-ban scan vets every rendered answer.
Retrieval relevance: symmetric stemming so inflected forms of a word always
converge to one stem (previously "leaves" stemmed to "leav" while clauses
containing "leave" kept a different stem, letting one mismatched keyword
pull an irrelevant clause ahead), rarity-weighted evidence sums rank answers,
a leader needs at least two corroborating query terms so one stray keyword
can never decide a topic alone, and exact-score ties inside a document
resolve by section order — any section of the same document is a valid
single source — instead of dropping the whole document (previously a tie
among one-term matches silently discarded the correct document and let a
weak keyword from another document win).
"""
import argparse
import math
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "..", "data", "policy-documents")

DOC_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
DOC_TEAM = {
    "policy_hr_leave.txt": "HR Department",
    "policy_it_acceptable_use.txt": "IT Helpdesk",
    "policy_finance_reimbursement.txt": "Finance Department",
}
DEFAULT_TEAM = "HR Department"

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally expected",
)

CITATION_RE = re.compile(r"\(policy_[a-z_]+\.txt, section \d+\.\d+\)")
SEPARATOR_RE = re.compile(r"^\s*[═=]{3,}\s*$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
WORD_RE = re.compile(r"[a-z0-9]+")

MIN_EVIDENCE = 2.8
RUNNER_UP_RATIO = 0.75
RUNNER_MIN_COVERAGE = 0.6

ANCHOR_MIN_DF = 8
ANCHOR_DOC_SHARE = 0.7
QUANTITY_QUERY_RE = re.compile(r"\bhow\s+(?:many|much)\b")
DIGIT_RE = re.compile(r"\d")

STOPWORDS = frozenset("""
a an the and or but if then else when while of to in on at by for with from as
is are was were be been being am do does did doing have has had having i me my
mine we us our ours you your yours he him his she her hers it its this that
these those they them their theirs what which who whom whose where why how
will would shall should can could may might must not no nor so than too very
just about there here also into per any all each own s t don ain
""".split())

CANONICAL = {
    "approval": "approv", "approvals": "approv", "approve": "approv",
    "approves": "approv", "approved": "approv", "approving": "approv",
    "carried": "carry", "carries": "carry",
    "entitled": "entitle", "entitlement": "entitle", "entitlements": "entitle",
    "eligibility": "eligible",
    "forfeiture": "forfeit", "forfeited": "forfeit",
    "encashment": "encash",
    "reimbursement": "reimburse", "reimbursements": "reimburse",
    "reimbursable": "reimburse", "reimbursed": "reimburse",
    "submission": "submit", "submitted": "submit", "submits": "submit",
    "installation": "install", "installing": "install", "installed": "install",
}


def _raw_stem(word):
    changed = True
    while changed:
        changed = False
        for suffix in ("ing", "ed", "es", "s"):
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                word = word[: len(word) - len(suffix)]
                changed = True
                break
    if len(word) >= 4 and word.endswith("e"):
        word = word[:-1]
    return word


def canonicalise(word):
    base = CANONICAL.get(word, word)
    if base.endswith("ies") and len(base) > 4:
        base = base[:-3] + "y"
    return _raw_stem(base)


VERBS = frozenset(canonicalise(v) for v in (
    "approv", "carry", "claim", "chang", "connect", "encash", "forward",
    "install", "print", "reimburse", "report", "share", "submit",
))

APPROVAL_QUERY_RE = re.compile(r"^\s*who\b|\bwhich\s+(?:team|department|person|role)s?\b")


def tokenize(text):
    return [
        canonicalise(w)
        for w in WORD_RE.findall(text.lower())
        if len(w) >= 2 and w not in STOPWORDS
    ]


class Clause(object):
    def __init__(self, doc, sid, text, heading):
        self.doc = doc
        self.sid = sid
        self.text = text
        self.heading = heading
        self.heading_vocab = set(tokenize(heading))
        self.vocab = set(tokenize(text)) | self.heading_vocab


def load_documents(data_dir):
    """retrieve_documents skill: index every clause by filename + section id."""
    index = {}
    for fname in DOC_FILES:
        path = os.path.join(data_dir, fname)
        try:
            with open(path, encoding="utf-8") as fh:
                raw = fh.read()
        except OSError as exc:
            sys.exit("error: cannot read policy document '%s': %s" % (path, exc))
        clauses = []
        heading = ""
        cur_sid = None
        cur_lines = []

        def flush():
            if cur_sid is not None:
                clauses.append(Clause(fname, cur_sid, " ".join(cur_lines), heading))

        for line in raw.splitlines():
            stripped = line.strip()
            if SEPARATOR_RE.match(stripped):
                flush()
                cur_sid = None
                cur_lines = []
                continue
            match = CLAUSE_RE.match(stripped)
            if match:
                flush()
                cur_sid = match.group(1)
                cur_lines = [match.group(2)]
                continue
            if not stripped:
                continue
            if cur_sid is None:
                heading = stripped
            else:
                cur_lines.append(stripped)
        flush()

        if not clauses:
            sys.exit(
                "error: no numbered sections parsed from '%s' — refusing to "
                "answer from a partial corpus" % path
            )
        index[fname] = clauses

    total = sum(len(c) for c in index.values())
    df = {}
    for clauses in index.values():
        for clause in clauses:
            for term in clause.vocab:
                df[term] = df.get(term, 0) + 1
    return index, total, df


def idf(df, total_clauses, term):
    hits = df.get(term, 0)
    if hits == 0:
        return 0.0
    return math.log(1.0 + float(total_clauses) / hits)


def refusal_text(team):
    resolved = DOC_TEAM.get(team)
    if resolved is None and team in DOC_TEAM.values():
        resolved = team
    return REFUSAL_TEMPLATE.replace("[relevant team]", resolved or DEFAULT_TEAM)


def render_answer(clause):
    """Condition-preservation by construction: verbatim quote + citation."""
    body = 'A: "%s" (%s, section %s)' % (clause.text, clause.doc, clause.sid)
    lowered = body.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in lowered:
            return refusal_text(clause.doc)
    if not CITATION_RE.search(body):
        return refusal_text(clause.doc)
    return body


def answer_question(question, index, total_clauses, df):
    """answer_question skill: score, single-source gate, answer or refuse.

    Evidence score is the sum of matched term idfs; section headings
    contribute their words to the clause vocabulary, so heading matches
    count like body matches. Symmetric stemming guarantees inflected query
    words match the index at all. A leader must clear MIN_EVIDENCE with at
    least TWO corroborating query terms: a single keyword — however rare —
    is never coverage on its own, but when the question also carries words
    the corpus lacks (product names, typos), a corpus-known action verb in
    the clause counts as the second term, keeping "install <unknown app>"
    retrievable while a stray keyword like "office" cannot hijack the
    answer. "wfh" is expanded to work-from-home vocabulary before matching.
    A how-many/much question whose sole corpus evidence is one document-
    dominant topic term (e.g. "leave", which appears almost exclusively in
    the HR policy) resolves inside that owning document — preferring its
    first clause that states a figure — instead of refusing: concentration,
    not raw score, proves ownership there. Exact-score ties inside one
    document are resolved by section order — any section of the same
    document is a valid single-source answer; only cross-document ambiguity
    triggers refusal.
    """
    question = re.sub(r"\bwfh\b", "work from home", question,
                      flags=re.IGNORECASE)
    seen = set()
    qtokens = []
    unseen_terms = 0
    for word in WORD_RE.findall(question.lower()):
        if len(word) < 3 or word in STOPWORDS:
            continue
        term = canonicalise(word)
        if term in seen:
            continue
        seen.add(term)
        weight = idf(df, total_clauses, term)
        if weight > 0.0:
            qtokens.append((term, weight))
        elif word.isalpha():
            unseen_terms += 1

    if not qtokens:
        return refusal_text(None)

    approval_routing = (bool(APPROVAL_QUERY_RE.search(question))
                        and "approv" in seen)
    verb_bonus = 0.0
    question_verbs = set()
    if unseen_terms:
        question_verbs = seen & VERBS
        if question_verbs:
            verb_bonus = math.log(1.0 + float(total_clauses))

    best_per_doc = {}
    for doc in DOC_FILES:
        doc_best = None
        for clause in index[doc]:
            if approval_routing and "approv" not in clause.vocab:
                continue
            verb_hit = bool(verb_bonus) and bool(question_verbs & clause.vocab)
            matched = [(t, w) for t, w in qtokens if t in clause.vocab]
            if not matched and not verb_hit:
                continue
            smax = max(w for _, w in matched) if matched else 0.0
            ssum = sum(w for _, w in matched)
            n = len(matched)
            if verb_hit:
                smax = max(smax, verb_bonus)
                ssum += verb_bonus
                n += 1
            terms = frozenset(t for t, _ in matched)
            cand = (ssum, smax, n, terms, clause)
            if doc_best is None or cand[:3] > doc_best[:3]:
                doc_best = cand
        if doc_best is None:
            continue
        best_per_doc[doc] = doc_best

    if not best_per_doc:
        return refusal_text(None)

    ranked = sorted(best_per_doc.items(), key=lambda kv: kv[1][:3], reverse=True)
    leader_doc, leader = ranked[0]
    leader_ssum = leader[0]

    if leader[2] == 1 and leader[3] and QUANTITY_QUERY_RE.search(question):
        anchor = next(iter(leader[3]))
        hits = df.get(anchor, 0)
        owner_clauses = index[leader_doc]
        in_owner = sum(1 for c in owner_clauses if anchor in c.vocab)
        if hits >= ANCHOR_MIN_DF and in_owner >= ANCHOR_DOC_SHARE * hits:
            pool = [c for c in owner_clauses
                    if anchor in c.vocab
                    and not (approval_routing and "approv" not in c.vocab)]
            chosen = next((c for c in pool if DIGIT_RE.search(c.text)),
                          pool[0])
            return render_answer(chosen)

    if leader_ssum < MIN_EVIDENCE or leader[2] < 2:
        return refusal_text(leader_doc)

    if len(ranked) > 1:
        runner = ranked[1][1]
        comparable = (runner[2] >= RUNNER_MIN_COVERAGE * leader[2]
                      and runner[0] >= RUNNER_UP_RATIO * leader_ssum)
        if comparable:
            return refusal_text(leader_doc)

    return render_answer(leader[4])


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR,
                        help="Directory containing the three policy documents")
    parser.add_argument("--ask", default=None,
                        help="Ask one question non-interactively and exit")
    args = parser.parse_args()

    index, total_clauses, df = load_documents(args.data_dir)

    if args.ask is not None:
        print(answer_question(args.ask, index, total_clauses, df))
        return

    print("UC-X — Ask My Documents")
    print("Indexed %d sections across %d documents: %s"
          % (total_clauses, len(DOC_FILES), ", ".join(DOC_FILES)))
    print("Type a question about CMC policy, or 'quit' to exit.")
    while True:
        try:
            line = input("Q> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            break
        if not line:
            continue
        if line.lower() in ("quit", "exit"):
            break
        print(answer_question(line, index, total_clauses, df))


if __name__ == "__main__":
    main()
