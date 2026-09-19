"""
UC-X — Ask My Documents
Interactive CLI that answers questions from three policy documents.
Answers come from ONE document only, quote the source clause verbatim, and cite
document name + section number. Anything not covered gets the refusal template.

Run:  python app.py            (interactive)
      python app.py --question "Who approves leave without pay?"   (single question)
"""
import argparse
import math
import os
import re
import sys

DOC_FILES = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]

# Refusal template from the README, word for word (only [relevant team] is filled in).
REFUSAL = ("This question is not covered in the available policy documents\n"
           "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
           "Please contact {team} for guidance.")
DEFAULT_TEAM = "the relevant department"

STOPWORDS = set("""a an the i my me we our you your is are was be am do does did can could would should
what who whom how when where which why to for of on in at from with by or and if it its this that
there any as about get give tell please company use used using uses""".split())

# Query-side aliases (question wording -> wording used in the policies).
ALIASES = {"phone": ["device"], "phones": ["device"], "smartphone": ["device"], "mobile": ["device"],
           "slack": ["software"], "app": ["software"], "apps": ["software"],
           "wfh": ["work", "from", "home"], "lwp": ["leave", "without", "pay"]}

BANNED_PHRASES = ["while not explicitly covered", "typically", "generally understood",
                  "it is common practice", "as is standard practice"]

MIN_SCORE = 5.0          # below this the question is treated as "not in the documents"
COMPANION_RATIO = 0.5    # extra clauses from the SAME document must score >= 50% of the best
SHARED_IDF = 2.0         # ...and share at least one distinctive matched word with the best clause
PHRASE_BONUS = 4.0       # bonus per matching two-word phrase (e.g. "personal device")
AMBIGUITY_RATIO = 0.9    # another document scoring this close to the best -> refuse (no blending)
MAX_CLAUSES = 3


def _stem(word: str) -> str:
    w = word.lower()
    for suf in ("ing", "ed", "es", "al", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 2:
            w = w[: -len(suf)]
            break
    if w.endswith("e") and len(w) > 2:
        w = w[:-1]
    return w


def _tokens(text: str) -> list:
    """Ordered, stemmed tokens: stopwords removed, aliases substituted (same rules for
    questions and documents, so 'LWP' and 'leave without pay' match each other)."""
    out = []
    for w in re.findall(r"[A-Za-z0-9]+", text.lower()):
        if w in STOPWORDS or len(w) < 2:
            continue
        if w in ALIASES:
            out.extend(_stem(a) for a in ALIASES[w])
        else:
            out.append(_stem(w))
    return out


# ---------------------------------------------------------------- skill 1
def retrieve_documents(doc_dir: str) -> list:
    """Load all 3 policy files and index every clause by document name and section number.
    Returns [{"doc","section","title","text","tokens"}, ...]."""
    index = []
    for name in DOC_FILES:
        path = os.path.join(doc_dir, name)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Policy document not found: {path}")
        title, current = "", None
        with open(path, encoding="utf-8-sig") as f:
            for raw in f.read().splitlines():
                line = raw.strip()
                if not line or set(line) <= {"═"}:
                    continue
                m_sec = re.match(r"^(\d+)\.\s+([A-Z][A-Z &/()-]+)$", line)
                m_cl = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
                if m_sec:
                    title, current = m_sec.group(2).title(), None
                elif m_cl:
                    current = {"doc": name, "section": m_cl.group(1), "title": title, "text": m_cl.group(2)}
                    index.append(current)
                elif current is not None and raw.startswith(" "):
                    current["text"] += " " + line
    for c in index:
        seq = _tokens(c["title"] + " " + c["text"])
        c["tokens"] = set(seq)
        c["bigrams"] = _bigrams(_tokens(c["text"]))
    return index


def _idf(index: list) -> dict:
    df = {}
    for c in index:
        for t in c["tokens"]:
            df[t] = df.get(t, 0) + 1
    n = len(index)
    return {t: math.log(1 + n / d) for t, d in df.items()}


def _bigrams(seq: list) -> set:
    return {(seq[i], seq[i + 1]) for i in range(len(seq) - 1)}


# ---------------------------------------------------------------- skill 2
def answer_question(question: str, index: list) -> str:
    """Return a single-source answer with citations, or the refusal template."""
    if not question.strip():
        return "Please type a question."
    idf = _idf(index)
    qseq = _tokens(question)
    qt, qbi = set(qseq), _bigrams(qseq)
    scored = []
    for c in index:
        matched = qt & c["tokens"]
        score = sum(idf[t] for t in matched) + PHRASE_BONUS * len(qbi & c["bigrams"])
        scored.append((score, c))
    scored.sort(key=lambda x: (-x[0], x[1]["doc"], [int(p) for p in x[1]["section"].split(".")]))

    best_score, best = scored[0]
    if best_score < MIN_SCORE:
        return REFUSAL.format(team=DEFAULT_TEAM)

    # Never blend documents: if a different document is almost as good, refuse.
    other_best = max((s for s, c in scored if c["doc"] != best["doc"]), default=0)
    if other_best >= AMBIGUITY_RATIO * best_score:
        return REFUSAL.format(team=DEFAULT_TEAM)

    best_words = {t for t in qt & best["tokens"] if idf[t] >= SHARED_IDF}
    chosen = [c for s, c in scored
              if c["doc"] == best["doc"] and s >= COMPANION_RATIO * best_score
              and (c is best or best_words & qt & c["tokens"])][:MAX_CLAUSES]
    chosen.sort(key=lambda c: [int(p) for p in c["section"].split(".")])

    lines = [f"Source: {best['doc']}"]
    for c in chosen:
        lines.append(f'  Section {c["section"]}: "{c["text"]}"')
    answer = "\n".join(lines)
    assert not any(p in answer.lower() for p in BANNED_PHRASES)
    return answer


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", default=os.path.join(here, "..", "data", "policy-documents"),
                        help="Folder containing the three policy .txt files")
    parser.add_argument("--question", help="Ask one question and exit (default: interactive)")
    args = parser.parse_args()

    index = retrieve_documents(args.docs)
    if args.question:
        print(answer_question(args.question, index))
        return

    print("Ask My Documents - HR leave, IT acceptable use and Finance reimbursement policies.")
    print("Type a question, or 'exit' to quit.\n")
    while True:
        try:
            q = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in {"exit", "quit", "q"}:
            break
        print(answer_question(q, index) + "\n")


if __name__ == "__main__":
    main()