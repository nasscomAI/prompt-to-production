"""
UC-X — Ask My Documents

Answers policy questions from exactly one document with a citation, or returns
the refusal template verbatim. It never merges two documents into one answer and
never hedges: enforcement rules 1 to 3 in agents.md.

Run: python3 app.py            (interactive)
     python3 app.py --question "..."   (single question, for scripted checks)
"""
import argparse
import os
import re

DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "data", "policy-documents")
EXPECTED_DOCS = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt",
                 "policy_finance_reimbursement.txt"]

# Rule 3 — reproduced exactly as written in the UC README. Never reworded.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant team for guidance."
)

# Rule 2 — prohibited in every answer. Checked before an answer is returned.
HEDGES = [
    "while not explicitly", "not explicitly covered", "typically", "generally",
    "generally understood", "it is common", "common practice",
    "as is standard practice", "standard practice", "usually expected",
    "usually", "it appears", "it seems", "presumably", "likely that",
]

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\.?\s+(.*)$")
# Titles carry parentheses — "LEAVE WITHOUT PAY (LWP)", "PERSONAL DEVICES
# (BYOD)". Excluding them silently filed every clause of those sections under
# the preceding heading.
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 &/()',.-]+)\s*$")

STOPWORDS = set("""a an the is are was were be been being do does did can could may might
must shall should will would i me my we our you your it its this that these those of in on
at to for from with without and or but if then than as by about into over under again there
here what which who whom when where why how all any both each few more most other some such
no nor not only own same so too very s t just don now use used using get got have has had""".split())


def retrieve_documents(doc_dir: str = DOC_DIR):
    """Load all three policy files, indexed by document name and section number."""
    index, problems = [], []
    for name in EXPECTED_DOCS:
        path = os.path.join(doc_dir, name)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().split("\n")
        except OSError as exc:
            problems.append(f"{name}: {exc}")
            continue

        heading, clause, found = "", None, 0
        for line in lines:
            stripped = line.strip()
            if not stripped or set(stripped) == {"═"}:
                continue
            m_sec = SECTION_RE.match(stripped)
            if m_sec:
                heading = m_sec.group(2).strip()
                continue
            m_cl = CLAUSE_RE.match(stripped)
            if m_cl:
                clause = {"doc": name, "section": m_cl.group(1),
                          "heading": heading, "text": m_cl.group(2).strip()}
                index.append(clause)
                found += 1
            elif clause is not None and line.startswith("    "):
                clause["text"] += " " + stripped
        if found == 0:
            problems.append(f"{name}: no numbered clauses found")

    if problems:
        raise SystemExit("Cannot build the policy index:\n  " + "\n  ".join(problems)
                         + "\nRefusing to answer from a partial corpus.")
    return index


def _stem(word: str) -> str:
    """Crude suffix strip so a question's wording reaches the clause's wording.

    Without it "approves" does not reach "approval" and the dual-approver clause
    scores no higher than its neighbours, which is how the first run cited HR 2.5
    for a question section 5.2 answers.
    """
    for suffix, keep in (("ing", 5), ("ies", 5), ("ied", 5), ("es", 4),
                         ("ed", 4), ("al", 5), ("s", 4)):
        if len(word) > keep and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def _terms(question: str):
    """Content stems in question order. Order matters — see _score."""
    return [_stem(w) for w in re.findall(r"[a-z]+", question.lower())
            if w not in STOPWORDS and len(w) > 2]


def _phrases(question: str):
    """Contiguous 3- to 5-word runs of the question, stopwords kept.

    "leave without pay" is the whole of section 5's title but reduces to the
    common stems leave and pay once stopwords are dropped, which is how a
    question about who approves LWP first matched clause 2.5.
    """
    words = re.findall(r"[a-z]+", question.lower())
    out = []
    for n in (5, 4, 3):
        out += [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]
    return out


def _score(clause, terms, phrases):
    """Weighted term overlap plus a phrase bonus.

    Terms are weighted by their position in the question: the first content word
    is what is being asked about. Without this, "Can I install Slack on my work
    laptop" scores clause 2.1 above 2.3 because laptop and work are common in the
    IT policy while install — the actual subject — counts the same as either.
    """
    body = clause["text"].lower()
    head = clause["heading"].lower()
    score = 0.0
    seen = set()
    for i, t in enumerate(terms):
        if t in seen:
            continue
        seen.add(t)
        # The first content word is the action or object being asked about and
        # outweighs the rest. "install" decides "Can I install Slack on my work
        # laptop"; without this, laptop and work carry clause 2.1 over 2.3, and
        # "approves" loses to the wording of 5.1.
        weight = 5.0 if i == 0 else max(1.0, 3.0 - 0.5 * i)
        pat = rf"\b{re.escape(t)}\w*"
        if re.search(pat, body):
            score += 2 * weight             # the clause itself says it
        elif re.search(pat, head):
            score += 1 * weight             # only the section title says it
    for ph in phrases:
        if ph in body:
            score += 6
            break
        if ph in head:
            score += 4
            break
    return score


def answer_question(question: str, index):
    """Answer from exactly one document with a citation, or refuse verbatim."""
    refusal = {"answer": REFUSAL_TEMPLATE, "doc": None, "sections": [], "refused": True}
    if not question or not question.strip():
        return refusal

    terms = _terms(question)
    if not terms:
        return refusal

    phrases = _phrases(question)
    scored = [(_score(c, terms, phrases), c) for c in index]
    scored = [(s, c) for s, c in scored if s >= 2]
    if not scored:
        return refusal

    # Best score per document, then require a clear winner. Rule 1: where two
    # documents are too close to separate, refuse rather than pick silently.
    per_doc = {}
    for s, c in scored:
        per_doc.setdefault(c["doc"], []).append((s, c))
    ranked = sorted(((max(s for s, _ in v), d) for d, v in per_doc.items()), reverse=True)
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < 1:
        return refusal

    doc = ranked[0][1]
    best = sorted(per_doc[doc], key=lambda sc: (-sc[0], sc[1]["section"]))
    top_score = best[0][0]
    chosen = [c for s, c in best if s == top_score][:2]

    sections = [c["section"] for c in chosen]
    body = " ".join(c["text"] for c in chosen)
    rendered = f"{body}\n\nSource: {doc}, section{'s' if len(sections) > 1 else ''} {', '.join(sections)}"

    # Rules 1 and 2, checked rather than trusted, before the answer is returned.
    low = rendered.lower()
    if any(h in low for h in HEDGES):
        return refusal
    if len({c["doc"] for c in chosen}) > 1:
        return refusal
    return {"answer": rendered, "doc": doc, "sections": sections, "refused": False}


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", help="Answer one question and exit")
    args = parser.parse_args()

    index = retrieve_documents()
    if args.question:
        print(answer_question(args.question, index)["answer"])
        return

    print(f"Ask My Documents — {len(index)} clauses indexed from {len(EXPECTED_DOCS)} policies.")
    print("Type a question, or 'quit' to exit.\n")
    while True:
        try:
            q = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in {"quit", "exit", "q"}:
            break
        print(f"\nAnswer: {answer_question(q, index)['answer']}\n")


if __name__ == "__main__":
    main()
