"""
UC-X — Ask My Documents

Answers policy questions strictly from three documents, honoring the enforcement
rules in agents.md and the skill contracts in skills.md.

Two structural guarantees prevent cross-document blending and hedged
hallucination: answer_question returns EXACTLY ONE clause (so two documents can
never be merged into one answer), and any question that does not clear the
relevance threshold returns the fixed refusal template verbatim — there is no
free-text generation path that could hedge.

Run:  python app.py            (interactive)
      python app.py --selftest (runs the 7 README test questions)
"""
import argparse
import math
import re
import sys

DOCS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z].*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
DIVIDER_RE = re.compile(r"^[═=]+$")

STOPWORDS = {
    "the", "a", "an", "i", "can", "my", "is", "to", "on", "for", "of", "do", "does",
    "what", "when", "in", "from", "and", "or", "be", "are", "with", "use", "used",
    "this", "that", "it", "if", "at", "by", "as", "me", "you", "your", "any",
    "view", "about", "company",
}

# Map question vocabulary to document vocabulary so intent words score. Kept
# deliberately tight — over-broad synonyms (e.g. laptop->computer) pull answers
# toward clauses that merely list the noun instead of the governing rule.
SYNONYMS = {
    "slack": ["software", "install"], "app": ["software"], "application": ["software"],
    "phone": ["device"], "encash": ["encashment"], "wfh": ["home"],
    "approve": ["approval"], "approves": ["approval"],
}


def _tokens(text: str):
    raw = re.findall(r"[a-zA-Z][a-zA-Z\-]*", text.lower())
    out = []
    for w in raw:
        if w in STOPWORDS or len(w) <= 1:
            continue
        out.append(w[:-1] if w.endswith("s") and len(w) > 3 else w)
    return out


def retrieve_documents(paths):
    """Parse all docs into a flat clause index with an IDF table over clause tokens."""
    index = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        doc_name = path.split("/")[-1]
        doc_ref = next((l.split(":", 1)[1].strip() for l in lines if "Document Reference" in l), doc_name)
        section_num = section_title = None
        clause = None
        for line in lines:
            s = line.strip()
            if DIVIDER_RE.match(s):
                continue
            sec, cls = SECTION_RE.match(s), CLAUSE_RE.match(s)
            if sec:
                section_num, section_title = sec.group(1), sec.group(2).strip()
                clause = None
            elif cls:
                clause = {"doc_name": doc_name, "doc_ref": doc_ref, "section": section_num,
                          "section_title": section_title or "", "clause_id": cls.group(1),
                          "text": cls.group(2).strip()}
                index.append(clause)
            elif clause is not None and s:
                clause["text"] += " " + s

    # Token sets: text and section title kept separate so a title (topic) match
    # can be weighted higher. Union is used for the IDF table.
    for c in index:
        c["text_tokens"] = set(_tokens(c["text"]))
        c["title_tokens"] = set(_tokens(c["section_title"]))
        c["tokens"] = c["text_tokens"] | c["title_tokens"]
    N = len(index)
    df = {}
    for c in index:
        for t in c["tokens"]:
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log(N / (1 + n)) + 1 for t, n in df.items()}
    return {"clauses": index, "idf": idf}


# A match must clear this IDF-weighted score AND hit 2+ distinct query terms.
SCORE_MIN = 3.0
MATCH_MIN = 2
# Matching a clause's section heading is strong topic evidence; weight it.
TITLE_BONUS = 1.0
# If the best clause from a DIFFERENT document scores within this fraction of the
# top clause, the question is genuinely cross-document ambiguous → refuse rather
# than risk a misleading single-source pick (e.g. the personal-phone trap).
AMBIGUITY_MARGIN = 0.10


def _expand(qtokens):
    expanded = list(qtokens)
    for t in qtokens:
        expanded.extend(SYNONYMS.get(t, []))
    return set(expanded)


def answer_question(question: str, index: dict) -> str:
    """Return one cited clause, or the verbatim refusal template. Never blends."""
    qtokens = _expand(_tokens(question))
    idf = index["idf"]

    scored = []
    for c in index["clauses"]:
        title_hits = qtokens & c["title_tokens"]
        # Section-topic words count once (via the title); only the non-title text
        # words distinguish clauses within the same section (e.g. 5.2's "approval").
        text_extra_hits = (qtokens & c["text_tokens"]) - c["title_tokens"]
        score = (sum(idf.get(t, 0.0) for t in text_extra_hits)
                 + TITLE_BONUS * sum(idf.get(t, 0.0) for t in title_hits))
        n_hits = len(text_extra_hits | title_hits)
        scored.append((score, n_hits, c))

    score, n_hits, best = max(scored, key=lambda x: x[0])
    if score < SCORE_MIN or n_hits < MATCH_MIN:
        return REFUSAL

    # Cross-document ambiguity: if another document's best clause is nearly as
    # strong, refuse rather than commit to one side of a blend.
    rival = max((s for s, _, c in scored if c["doc_name"] != best["doc_name"]), default=0.0)
    if rival >= score * (1 - AMBIGUITY_MARGIN):
        return REFUSAL

    return (f"[{best['doc_name']} · Section {best['clause_id']}]\n"
            f"\"{best['text']}\"")


TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--selftest", action="store_true", help="Run the 7 README test questions")
    args = parser.parse_args()

    index = retrieve_documents(DOCS)
    print(f"Indexed {len(index['clauses'])} clauses from {len(DOCS)} documents.\n")

    if args.selftest:
        for q in TEST_QUESTIONS:
            print(f"Q: {q}")
            print(answer_question(q, index))
            print("-" * 70)
        return

    print("Ask a policy question (blank line or Ctrl-D to quit).")
    while True:
        try:
            q = input("\n> ").strip()
        except EOFError:
            break
        if not q:
            break
        print(answer_question(q, index))


if __name__ == "__main__":
    main()
