"""
UC-X "Ask My Documents" agent.

Answers employee questions strictly from three CMC policy documents:
  ../data/policy-documents/policy_hr_leave.txt
  ../data/policy-documents/policy_it_acceptable_use.txt
  ../data/policy-documents/policy_finance_reimbursement.txt

Behaviour:
  - Answers are always grounded in a SINGLE source document.
  - Never combines claims from two different documents into one answer.
  - Every factual answer cites the source filename and section number.
  - Unsupported questions return the exact refusal template.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(BASE_DIR, "..", "data", "policy-documents")

DOC_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "\n"
    "Please contact [relevant team] for guidance."
)

STOPWORDS = frozenset(
    """
    a an the this that these those is are was were be been being can could
    would should may might must shall will do does did have has had i me my
    we our you your he she it its they their them who whom whose which what
    when where why how on in at for to of with without from by about into
    and or but not if then than so as all any each per rs am pm or
    """.split()
)

# Intent groups.  Key = intent, value = (list of variant phrases, canonical token).
INTENT_GROUPS = {
    "approval": (
        ("approved", "approves", "approve", "approval", "pre-approved"),
        "approval",
    ),
    "install": (
        ("install", "installs", "installed", "installing", "installation"),
        "install",
    ),
    "claim": (
        ("claim", "claims", "claimed", "claiming", "reimbursement", "reimbursed"),
        "claim",
    ),
    "access": (("access", "accesses", "accessing", "accessed"), "access"),
    "carryforward": (
        ("carry forward", "carried forward", "carry over", "carryover"),
        "carry",
    ),
    "use": (("use", "uses", "used", "using"), "use"),
    "require": (("require", "requires", "required", "requirement"), "required"),
}

# Strong prohibition / permission-gate phrasing.
PERMISSION_STRONG = (
    "must not",
    "may not",
    "cannot",
    "prohibited",
    "not permitted",
    "not allowed",
    "without written approval",
)
# Weaker permission / approval markers.
PERMISSION_WEAK = (
    "must",
    "may",
    "not",
    "permitted",
    "allowed",
    "approval",
    "approved",
    "approve",
    "approves",
    "require",
    "requires",
    "required",
    "only",
)

PERMISSION_QUESTION_PREFIXES = (
    "can ",
    "may ",
    "am i ",
    "is it ",
    "are we ",
    "are i ",
    "would i be allowed",
    "is ... allowed",
)

DOMAIN_KEYWORDS = {
    "policy_hr_leave.txt": {
        "carry forward": 6,
        "carried forward": 6,
        "annual leave": 6,
        "sick leave": 6,
        "leave without pay": 6,
        "leave encashment": 6,
        "loss of pay": 5,
        "public holiday": 5,
        "compensatory off": 5,
        "medical certificate": 5,
        "grievance": 4,
        "maternity": 5,
        "paternity": 5,
        "encash": 5,
        "lwp": 6,
        "paid leave": 4,
        "unapproved absence": 4,
        "leave": 3,
        "forfeit": 2,
    },
    "policy_it_acceptable_use.txt": {
        "personal device": 7,
        "personal phone": 7,
        "corporate device": 6,
        "endpoint security": 6,
        "acceptable use": 6,
        "work files": 4,
        "laptop": 6,
        "desktop": 5,
        "smartphone": 5,
        "byod": 4,
        "install": 5,
        "installed": 3,
        "installation": 4,
        "software": 4,
        "password": 5,
        "mfa": 4,
        "wifi": 3,
        "network": 3,
        "cmc email": 5,
        "email": 4,
        "access": 4,
        "internet": 3,
        "security": 3,
        "system access": 4,
        "data": 2,
    },
    "policy_finance_reimbursement.txt": {
        "reimbursement": 6,
        "reimburse": 6,
        "claim": 6,
        "claims": 6,
        "daily allowance": 6,
        "allowance": 6,
        "receipts": 6,
        "receipt": 4,
        "da": 5,
        "meal": 3,
        "meals": 4,
        "expense": 5,
        "expenses": 5,
        "travel": 4,
        "outstation": 4,
        "hotel": 4,
        "air travel": 5,
        "economy class": 4,
        "work from home": 5,
        "home office": 5,
        "training": 4,
        "course fee": 4,
        "exam fee": 4,
    },
}

MIN_DOMAIN_SCORE = 6
DOMAIN_MARGIN = 1.5
SECTION_INCLUDE_RATIO = 0.8
INTENT_WEIGHT = 20
CANONICAL_BONUS = 3
PHRASE_WEIGHT = 3
PHRASE_CAP = 12
PERMISSION_CAP = 6

SECTION_RE = re.compile(r"^(\d+\.\d+)\s+[A-Za-z]")
MAIN_HEADER_RE = re.compile(r"^\d+\.\s+[A-Z][A-Z0-9 ().\-']*$")


def tokens(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return [tok for tok in text.split() if tok and not tok.isdigit()]


def normalized(text):
    return " ".join(tokens(text))


def _has_variant(variants, tok_set, ntokens):
    for variant in variants:
        vt = variant.split()
        if len(vt) == 1:
            if variant in tok_set:
                return True
        else:
            if variant in ntokens:
                return True
    return False


def parse_document(path):
    sections = {}
    cur = None
    buf = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            m = SECTION_RE.match(line)
            if m:
                if cur is not None:
                    sections[cur] = " ".join(buf).strip()
                cur = m.group(1)
                buf = [line[m.end():].strip()]
                continue
            if MAIN_HEADER_RE.match(line) or line.startswith("\u2550"):
                continue
            if cur is not None:
                buf.append(line)
    if cur is not None:
        sections[cur] = " ".join(buf).strip()
    return sections


def load_documents():
    docs = {}
    for name in DOC_FILES:
        path = os.path.join(DOC_DIR, name)
        docs[name] = parse_document(path)
    return docs


def score_domain(qtokens, qtext, keywords):
    score = 0
    for phrase, weight in keywords.items():
        pt = phrase.split()
        if len(pt) == 1:
            if phrase in qtokens:
                score += weight
        elif phrase in qtext:
            score += weight
    return score


def is_permission_question(question):
    q = question.strip().lower()
    for prefix in PERMISSION_QUESTION_PREFIXES:
        if q.startswith(prefix):
            return True
    for kw in ("allowed", "permitted", "approve", "approval", "approves"):
        if kw in q:
            return True
    return False


def score_section(question, qtokens, qtext, section_tokens, section_text):
    """Score one section against the question."""
    score = 0

    stal = set(section_tokens)
    content = [t for t in qtokens if t not in STOPWORDS]

    for tok in content:
        if tok in stal:
            score += 2

    q_ngrams = []
    for n in (2, 3):
        for i in range(len(qtokens) - n + 1):
            q_ngrams.append(tuple(qtokens[i:i + n]))
    seen = set()
    phrase_hits = 0
    for ngram in q_ngrams:
        if ngram in seen:
            continue
        seen.add(ngram)
        if ngram in _windows(section_tokens, len(ngram)):
            score += PHRASE_WEIGHT
            phrase_hits += 1
            if phrase_hits * PHRASE_WEIGHT >= PHRASE_CAP:
                break

    for group, (variants, canonical) in INTENT_GROUPS.items():
        q_has = _has_variant(variants, set(qtokens), qtext)
        s_has = _has_variant(variants, stal, section_text)
        if q_has and s_has:
            score += INTENT_WEIGHT
            if canonical in stal:
                score += CANONICAL_BONUS

    if is_permission_question(question):
        perm_score = 0
        for m in PERMISSION_STRONG:
            if m in section_text:
                perm_score += 2
        for m in PERMISSION_WEAK:
            if m in section_text:
                perm_score += 1
        score += min(perm_score, PERMISSION_CAP)

    return score


def _windows(seq, size):
    return {tuple(seq[i:i + size]) for i in range(len(seq) - size + 1)}


def answer_question(question, docs):
    qtokens = tokens(question)
    if not qtokens:
        return REFUSAL_TEMPLATE
    qtext = " ".join(qtokens)

    domain_scores = []
    for name, sections in docs.items():
        dscore = score_domain(qtokens, qtext, DOMAIN_KEYWORDS[name])
        domain_scores.append((name, dscore))

    ranked_docs = sorted(domain_scores, key=lambda kv: -kv[1])
    best_doc, best = ranked_docs[0]
    second = ranked_docs[1][1] if len(ranked_docs) > 1 else 0.0

    if best < MIN_DOMAIN_SCORE or best < DOMAIN_MARGIN * second:
        return REFUSAL_TEMPLATE

    sections = docs[best_doc]
    sec_scores = []
    for num, text in sections.items():
        secure = tokens(text)
        stext = " ".join(secure)
        s = score_section(question, qtokens, qtext, secure, stext)
        sec_scores.append((num, s, text))

    ranked_sec = sorted(sec_scores, key=lambda item: -item[1])
    top_num, top_score, _ = ranked_sec[0]

    if top_score <= 0:
        return REFUSAL_TEMPLATE

    cutoff = SECTION_INCLUDE_RATIO * top_score
    picked = sorted((num, text) for num, s, text in ranked_sec if s >= cutoff)

    return compose_answer(best_doc, picked)


def compose_answer(doc_name, picked):
    parts = []
    for num, text in picked:
        parts.append(
            "Source: {0} - Section {1}\n{1} {2}".format(doc_name, num, text)
        )
    return "\n\n".join(parts)


def main():
    docs = load_documents()
    print("UC-X - Ask My Documents")
    print("Type a question, or 'quit' / 'exit' to stop.")
    print()
    while True:
        try:
            question = input("Q> ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break
        print()
        print(answer_question(question, docs))
        print()


if __name__ == "__main__":
    main()