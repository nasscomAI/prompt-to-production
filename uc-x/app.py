"""
UC-X — Ask My Documents
Single-source policy Q&A built to the agents.md enforcement rules: every
answer cites exactly one document and section, claims from different
documents are never blended, hedged phrasing cannot occur (answers are
quoted clause text or the refusal template, nothing else), and uncovered
questions get the refusal template verbatim.
"""
import argparse
import math
import os
import re

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact the HR, IT, or "
    "Finance Department for guidance."
)

SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z \-&(),'()]+?)\s*$")
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
DIVIDER_RE = re.compile(r"^[\s═=\-]+$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "for", "with", "and", "or", "but", "if", "then",
    "than", "that", "this", "these", "those", "it", "its", "as", "at", "by",
    "from", "can", "could", "may", "might", "will", "would", "shall",
    "should", "do", "does", "did", "have", "has", "had", "i", "my", "me",
    "we", "our", "you", "your", "he", "she", "they", "them", "their",
    "what", "which", "who", "whom", "whose", "when", "where", "why", "how",
    "so", "such", "there", "here", "any", "all", "each", "every", "more",
    "most", "some", "only", "own", "too", "very", "just", "about", "into",
    "over", "under", "again", "once", "while", "until", "because",
}

STEM_SYNONYMS = {
    "phone": {"devic"}, "smartphon": {"devic"}, "mobil": {"devic"},
    "laptop": {"devic", "corpor"}, "comput": {"devic"},
    "instal": {"softwar"}, "slack": {"softwar"},
    "fil": {"data", "email"}, "document": {"data"},
}

MIN_CLAUSE_SCORE = 4.0
MIN_COVERAGE = 0.5
DOC_TIE_MARGIN = 0.75
MAX_ANSWER_CLAUSES = 3


def _stem(word):
    for suffix in ("ational", "tional", "ization", "ation", "ition",
                   "ement", "ments", "ingly", "ings", "ment", "ness",
                   "tion", "sion", "ing", "ies", "ied", "ers", "est",
                   "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[:-len(suffix)]
            break
    if len(word) > 3 and word.endswith("e"):
        word = word[:-1]
    if len(word) > 4 and word.endswith("al"):
        word = word[:-2]
    return word


def _tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower())
            if len(t) > 1 and t not in STOPWORDS]


def _stems(text):
    return [_stem(t) for t in _tokenize(text)]


def retrieve_documents(docs_dir):
    """Load all policy files, index by document name and section number."""
    index = []
    for document in DOCUMENTS:
        path = os.path.join(docs_dir, document)
        if not os.path.exists(path):
            raise SystemExit("Missing required document: %s" % path)
        with open(path, encoding="utf-8-sig") as f:
            raw_lines = f.read().splitlines()

        section_number, section_title = "", ""
        for line in raw_lines:
            divider = DIVIDER_RE.match(line)
            section_match = SECTION_RE.match(line)
            clause_match = CLAUSE_RE.match(line)
            if divider:
                continue
            if section_match:
                section_number = section_match.group(1)
                section_title = section_match.group(2).strip()
                continue
            if clause_match:
                index.append({
                    "document": document,
                    "section": section_number,
                    "section_title": section_title,
                    "clause_id": clause_match.group(1),
                    "text": clause_match.group(2).strip(),
                })
            elif index and line.strip() and index[-1]["section"] == section_number:
                index[-1]["text"] += " " + line.strip()
    return index


def _score_question(index, question):
    q_stems = set(_stems(question))
    extra = set()
    for stem in q_stems:
        extra |= STEM_SYNONYMS.get(stem, set())

    df = {}
    for entry in index:
        for stem in set(_stems(entry["section_title"] + " " + entry["text"])):
            df[stem] = df.get(stem, 0) + 1

    def idf(stem):
        return math.log((len(index) + 1) / (df.get(stem, 0) + 1)) + 1.0

    scored = []
    for entry in index:
        c_stems = set(_stems(entry["section_title"] + " " + entry["text"]))
        exact = q_stems & c_stems
        syn = {s for s in extra if s in c_stems}
        score = sum(idf(s) for s in exact) + 0.6 * sum(idf(s) for s in syn)
        covered = len(exact | syn)
        scored.append((score, covered, len(q_stems), entry))
    return scored


def answer_question(index, question):
    """Return a cited single-source answer or the exact refusal template."""
    scored = _score_question(index, question)
    scored.sort(key=lambda item: item[0], reverse=True)

    best_score, best_covered, q_len, best_entry = scored[0]
    doc_totals = {}
    for score, _, _, entry in scored:
        doc_totals.setdefault(entry["document"], []).append(score)

    def top_sum(doc):
        return sum(sorted(doc_totals[doc], reverse=True)[:2])

    ranking = sorted(((doc, top_sum(doc)) for doc in doc_totals),
                     key=lambda kv: kv[1], reverse=True)
    if (best_score < MIN_CLAUSE_SCORE or best_covered < MIN_COVERAGE * max(q_len, 1)):
        return REFUSAL_TEMPLATE
    if len(ranking) > 1 and (ranking[1][1] >= DOC_TIE_MARGIN * ranking[0][1]):
        return REFUSAL_TEMPLATE

    cutoff = best_score * 0.6
    picked = [(s, e) for s, _, _, e in scored[:MAX_ANSWER_CLAUSES * 2]
              if s >= cutoff and e["document"] == best_entry["document"]]
    picked = sorted(picked, key=lambda pair: pair[1]["clause_id"])[:MAX_ANSWER_CLAUSES]

    lines = []
    for _, entry in picked:
        lines.append("[%s § %s]" % (entry["document"], entry["clause_id"]))
        lines.append('"%s"' % entry["text"])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs-dir", default="../data/policy-documents",
                        help="Directory containing the three policy .txt files")
    parser.add_argument("--ask", default=None,
                        help="Ask one question non-interactively")
    args = parser.parse_args()

    index = retrieve_documents(args.docs_dir)
    print("Indexed %d documents, %d clauses." % (len(DOCUMENTS), len(index)))

    if args.ask:
        print(answer_question(index, args.ask))
        return

    print("Type a question ('quit' to exit).")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question or question.lower() in ("quit", "exit"):
            break
        print(answer_question(index, question))


if __name__ == "__main__":
    main()
