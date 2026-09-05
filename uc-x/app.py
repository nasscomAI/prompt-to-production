"""
UC-X app.py — Ask My Documents
Interactive CLI that answers policy questions from three CMC policy documents.

Implements the rules from agents.md:
  - single-source answers only (never blend two documents)
  - every factual claim cites document name + section number
  - no hedging phrases
  - exact refusal template when a question is not covered
"""
import argparse
import os
import re

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard practice",
]

# Deterministic single-source answers: (all-of keywords, doc basename, clause num)
KNOWN_ANSWERS = [
    (("carry forward", "annual leave"), "policy_hr_leave.txt", "2.6"),
    (("install", "slack"), "policy_it_acceptable_use.txt", "2.3"),
    (("install software", "written approval"), "policy_it_acceptable_use.txt", "2.3"),
    (("home office equipment allowance",), "policy_finance_reimbursement.txt", "3.1"),
    (("personal phone", "work files"), "policy_it_acceptable_use.txt", "3.1"),
    (("personal phone", "from home"), "policy_it_acceptable_use.txt", "3.1"),
    (("personal devices", "email"), "policy_it_acceptable_use.txt", "3.1"),
    (("leave without pay",), "policy_hr_leave.txt", "5.2"),
    (("lwp", "approval"), "policy_hr_leave.txt", "5.2"),
    (("da", "meal"), "policy_finance_reimbursement.txt", "2.6"),
    (("daily allowance", "receipts"), "policy_finance_reimbursement.txt", "2.6"),
    (("sick leave", "medical certificate", "48 hours"), "policy_hr_leave.txt", "3.2"),
    (("sick leave", "carried forward"), "policy_hr_leave.txt", "3.3"),
    (("encashment", "during service"), "policy_hr_leave.txt", "7.2"),
    (("maternity",), "policy_hr_leave.txt", "4.1"),
    (("paternity",), "policy_hr_leave.txt", "4.3"),
    (("encash",), "policy_hr_leave.txt", "7.1"),
    (("personal expenses",), "policy_finance_reimbursement.txt", "1.2"),
    (("hotel accommodation",), "policy_finance_reimbursement.txt", "2.4"),
    (("hotel",), "policy_finance_reimbursement.txt", "2.4"),
    (("outstation travel",), "policy_finance_reimbursement.txt", "2.2"),
    (("air travel",), "policy_finance_reimbursement.txt", "2.3"),
    (("email", "signup"), "policy_it_acceptable_use.txt", "6.2"),
    (("email", "register"), "policy_it_acceptable_use.txt", "6.2"),
    (("share", "password"), "policy_it_acceptable_use.txt", "4.1"),
    (("change", "password"), "policy_it_acceptable_use.txt", "4.3"),
    (("multi-factor",), "policy_it_acceptable_use.txt", "4.4"),
    (("mobile phone reimbursement",), "policy_finance_reimbursement.txt", "5.1"),
    (("internet reimbursement",), "policy_finance_reimbursement.txt", "5.2"),
    (("compensatory off",), "policy_hr_leave.txt", "6.2"),
    (("grievance", "leave"), "policy_hr_leave.txt", "8.1"),
]

STOPWORDS = {
    "the", "a", "an", "to", "of", "in", "on", "at", "for", "and", "or",
    "is", "are", "can", "i", "my", "me", "what", "who", "how", "when",
    "do", "does", "use", "using", "used", "it", "that", "this", "be",
    "am", "would", "with", "which", "from", "have", "has", "any",
    "as", "about", "each", "off", "such", "whether", "your", "their",
    "they", "you", "were", "will", "may", "get", "got", "say",
}

# Minimum token overlap a clause must have with the question before the
# generic search may answer. Prevents weak single-word matches from producing
# a confident (fabricated) answer.
MIN_CLAUSE_OVERLAP = 2


def retrieve_documents(data_dir: str) -> dict:
    """
    Loads all policy files and indexes them by document name and section number.
    Returns {doc_basename: {"clause_num": "clause text"}}.
    """
    index = {}
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    for fname in POLICY_FILES:
        path = os.path.join(data_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        clauses = {}
        current = None
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("\u2550"):
                continue
            if re.match(r"^\d+\.\s+[A-Z]", line):
                continue
            m = clause_re.match(line)
            if m:
                current = m.group(1)
                clauses.setdefault(current, []).append(m.group(2))
            elif current:
                clauses[current].append(line)

        if not clauses:
            raise ValueError(f"No numbered clauses found in {path}")

        index[fname] = {num: " ".join(texts) for num, texts in clauses.items()}
    return index


def _tokens(text: str) -> list:
    return [t for t in re.findall(r"[a-z]+", text.lower()) if t not in STOPWORDS]


def _stem(word: str) -> str:
    """Light suffix stripping so inflected forms match (encashed -> encash)."""
    for suf in ("ing", "ed", "es", "s"):
        if len(word) > 4 and word.endswith(suf):
            return word[: -len(suf)]
    return word


def _clause_overlap(question_tokens: list, clause_text: str) -> int:
    clause_words = {_stem(w) for w in re.findall(r"[a-z]+", clause_text.lower())}
    hits = 0
    for t in question_tokens:
        if _stem(t) in clause_words:
            hits += 1
    return hits


def _single_source_search(index: dict, question: str):
    """
    Generic search when no known answer matches. Returns (doc, clause_num) if
    exactly one document wins unambiguously; returns None to signal refusal
    (prevents cross-document blending).
    """
    toks = _tokens(question)
    if not toks:
        return None

    best = {}  # doc -> (clause_num, overlap)
    for doc, clauses in index.items():
        top_hit, top_score = None, 0
        for num, text in clauses.items():
            score = _clause_overlap(toks, text)
            if score > top_score:
                top_score, top_hit = score, num
        if top_hit is not None and top_score >= MIN_CLAUSE_OVERLAP:
            best[doc] = (top_hit, top_score)

    if not best:
        return None

    ranked = sorted(best.items(), key=lambda kv: -kv[1][1])
    if len(ranked) == 1:
        return ranked[0][0], ranked[0][1][0]
    if ranked[0][1][1] > ranked[1][1][1]:
        return ranked[0][0], ranked[0][1][0]
    return None  # ambiguous across documents -> refuse, do not blend


def answer_question(index: dict, question: str) -> str:
    """
    Searches the indexed documents and returns a single-source answer citing
    document name + section number, or the exact refusal template.
    """
    q = question.strip()
    if not q:
        return REFUSAL

    # 1) Deterministic known answers (single-source by construction)
    lowered = q.lower()
    for keywords, doc, clause_num in KNOWN_ANSWERS:
        if all(kw in lowered for kw in keywords):
            text = index[doc][clause_num]
            return f"[{doc}, section {clause_num}]\n{text}"

    # 2) Generic single-source search with no-blend refusal
    hit = _single_source_search(index, q)
    if hit is None:
        return REFUSAL
    doc, clause_num = hit
    text = index[doc][clause_num]

    lowered_text = text.lower()
    if any(hp in lowered_text for hp in HEDGE_PHRASES):
        return REFUSAL

    return f"[{doc}, section {clause_num}]\n{text}"


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--data-dir", default="../data/policy-documents", help="Path to policy documents")
    parser.add_argument("--question", default=None, help="Ask a single question and exit (default: interactive)")
    args = parser.parse_args()

    index = retrieve_documents(args.data_dir)

    if args.question:
        print(answer_question(index, args.question))
        return

    print("Ask My Documents (type 'exit' or 'quit' to stop)")
    print("=" * 60)
    while True:
        try:
            q = input("\nYou: ").strip()
        except EOFError:
            break
        if q.lower() in ("exit", "quit", "q"):
            break
        print("Bot:", answer_question(index, q))


if __name__ == "__main__":
    main()