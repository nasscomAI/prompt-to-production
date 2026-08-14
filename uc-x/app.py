"""
UC-X — Policy Document Q&A
Rule-based Q&A enforced by uc-x/agents.md.
Every answer comes from exactly one policy document and cites the document
name and section number. Answers are single-source quotes; when a question is
not covered, or the best matches span more than one document, the exact
refusal template is used. Information from multiple policies is never blended.
"""
import os
import re

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Concept list: (question_regex, section_regex, weight).
# The question_regex activates the concept from the user's wording; the
# section_regex finds evidence of that concept inside a policy clause.
# Higher weight = more decisive concept (e.g. the DA/meal "same day" rule).
CONCEPTS = [
    (re.compile(r"carry forward|carry-forward"),
     re.compile(r"carry[- ]?forward"), 2),
    (re.compile(r"leave without pay|lwp"),
     re.compile(r"leave without pay|lwp"), 2),
    (re.compile(r"annual leave"), re.compile(r"annual leave"), 2),
    (re.compile(r"sick leave"), re.compile(r"sick leave"), 2),
    (re.compile(r"\bleave\b"), re.compile(r"\bleave\b"), 1),
    (re.compile(r"install"), re.compile(r"install\w*"), 2),
    (re.compile(r"software|slack"), re.compile(r"\bsoftware\b"), 2),
    (re.compile(r"laptop"), re.compile(r"laptop\w*|corporate device\w*"), 2),
    (re.compile(r"personal phone|personal device|phone"),
     re.compile(r"personal device\w*"), 2),
    (re.compile(r"work from home|working from home|from home|work files|remote work|home office"),
     re.compile(r"work[- ]?from[- ]?home|home office"), 2),
    (re.compile(r"home office|equipment allowance|allowance"),
     re.compile(r"allowance"), 2),
    (re.compile(r"daily allowance|da "),
     re.compile(r"daily allowance|\bda\b"), 2),
    (re.compile(r"meal"), re.compile(r"meal\w*"), 2),
    (re.compile(r"receipt"), re.compile(r"receipt\w*"), 2),
    (re.compile(r"approve|approval|approves"),
     re.compile(r"approve\w*|approval\w*"), 2),
    (re.compile(r"reimburs"), re.compile(r"reimburs\w*"), 2),
    (re.compile(r"same day|simultaneously"),
     re.compile(r"simultaneously|same day"), 3),
    (re.compile(r"\buse\w*|access\w*"),
     re.compile(r"\buse\w*|access\w*"), 1),
]


def _parse_clauses(path):
    """Index one policy file by section number: {section_id: text}."""
    clauses = {}
    current = None
    buf = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n")
            m = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
            if m:
                if current is not None:
                    clauses[current] = " ".join(buf)
                current = m.group(1)
                buf = [m.group(2).strip()]
            elif current is not None:
                s = stripped.strip()
                if not s or s.startswith("\u2550"):
                    continue
                if re.match(r"^\d+\.\s+\S", s):
                    clauses[current] = " ".join(buf)
                    current = None
                    buf = []
                else:
                    buf.append(s)
    if current is not None:
        clauses[current] = " ".join(buf)
    return clauses


def retrieve_documents():
    """Load all 3 policy files, indexed by document name and section number."""
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "data", "policy-documents")
    docs = {}
    for fname in POLICY_FILES:
        path = os.path.join(base, fname)
        if not os.path.exists(path):
            raise SystemExit("REFUSED: policy file not found: %s" % path)
        docs[fname] = _parse_clauses(path)
    return docs


def answer_question(question, docs):
    """Return a single-source answer with citation, or the refusal template."""
    q = (question or "").strip()
    if not q:
        return REFUSAL_TEMPLATE
    q_lower = q.lower()

    # Concepts activated by this question.
    activated = [(q_rx, s_rx, w) for q_rx, s_rx, w in CONCEPTS
                 if q_rx.search(q_lower)]
    if not activated:
        return REFUSAL_TEMPLATE

    # Score every section across every document.
    scored = []  # (score, doc_name, section_id)
    for doc_name, clauses in docs.items():
        for sid, text in clauses.items():
            norm = re.sub(r"\s+", " ", text).lower()
            score = sum(w for _, s_rx, w in activated if s_rx.search(norm))
            if score > 0:
                scored.append((score, doc_name, sid))

    if not scored:
        return REFUSAL_TEMPLATE

    best_score = max(s for s, _, _ in scored)
    top = [(doc, sid) for s, doc, sid in scored if s == best_score]
    top.sort(key=lambda pair: _section_key(pair[1]))

    # Never blend: if the best matches span two documents, refuse.
    documents_used = {doc for doc, _ in top}
    if len(documents_used) > 1:
        return REFUSAL_TEMPLATE

    doc_name, sid = top[0]
    quote = re.sub(r"\s+", " ", docs[doc_name][sid])
    return "Source: %s, section %s\n\n%s" % (doc_name, sid, quote)


def _section_key(sid):
    a, b = sid.split(".")
    return (int(a), int(b))


def main():
    docs = retrieve_documents()
    print("Policy Q&A ready.")
    print("Documents indexed: %s" % ", ".join(POLICY_FILES))
    print("Type 'exit' or 'quit' to end.")
    while True:
        try:
            q = input("\nYour question: ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            break
        print("\n" + answer_question(q, docs))


if __name__ == "__main__":
    main()