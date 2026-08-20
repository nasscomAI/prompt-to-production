"""
UC-X app.py — Ask My Documents

Interactive CLI that answers questions from exactly one of the three CMC
policy documents, always citing the source document and section number.
Questions not covered by the documents receive the exact refusal template.
It never blends claims from two different documents into a single answer.

Enforcement (from agents.md):
  1. Never combine claims from two different documents into one answer
  2. Never use hedging phrases: "while not explicitly covered",
     "typically", "generally understood", "it is common practice"
  3. If the question is not in the documents — use the refusal template
     exactly, no variations
  4. Cite source document name + section number for every factual claim
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "in most cases",
]

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z0-9 ().\-/]*)\s*$")
BOX_LINE_RE = re.compile(r"^\s*[=\u2550\u2500\u2014-]{5,}\s*$")
WORD_RE = re.compile(r"[a-z0-9]+")

# Topic phrase map: (all-of phrases, doc, section). Phrases checked in order.
PHRASE_MAP = [
    (["slack"], "policy_it_acceptable_use.txt", "2.3"),
    (["install", "software"], "policy_it_acceptable_use.txt", "2.3"),
    (["carry forward"], "policy_hr_leave.txt", "2.6"),
    (["carry-over"], "policy_hr_leave.txt", "2.6"),
    (["home office", "allowance"], "policy_finance_reimbursement.txt", "3.1"),
    (["equipment allowance"], "policy_finance_reimbursement.txt", "3.1"),
    (["personal phone"], "policy_it_acceptable_use.txt", "3.1"),
    (["personal device"], "policy_it_acceptable_use.txt", "3.1"),
    (["byod"], "policy_it_acceptable_use.txt", "3.1"),
    (["meal receipt"], "policy_finance_reimbursement.txt", "2.6"),
    (["da and meal"], "policy_finance_reimbursement.txt", "2.6"),
    (["daily allowance"], "policy_finance_reimbursement.txt", "2.5"),
    (["leave without pay"], "policy_hr_leave.txt", "5.2"),
    (["lwp"], "policy_hr_leave.txt", "5.2"),
    (["maternity"], "policy_hr_leave.txt", "4.1"),
    (["paternity"], "policy_hr_leave.txt", "4.3"),
    (["encash"], "policy_hr_leave.txt", "7.2"),
    (["encashment"], "policy_hr_leave.txt", "7.2"),
    (["sick leave", "certificate"], "policy_hr_leave.txt", "3.2"),
    (["medical certificate"], "policy_hr_leave.txt", "3.2"),
    (["public holiday"], "policy_hr_leave.txt", "6.2"),
    (["password"], "policy_it_acceptable_use.txt", "4.1"),
    (["wifi"], "policy_it_acceptable_use.txt", "3.3"),
    (["guest wifi"], "policy_it_acceptable_use.txt", "3.3"),
]

STOPWORDS = {
    "can", "could", "would", "should", "may", "the", "and", "for", "with",
    "from", "what", "how", "when", "where", "who", "which", "this", "that",
    "these", "those", "there", "here", "you", "your", "my", "me", "i",
    "is", "are", "was", "were", "do", "does", "did", "have", "has", "had",
    "on", "in", "at", "to", "of", "a", "an", "be", "been", "it", "not",
    "or", "but", "if", "then", "than", "about", "any", "all", "some",
    "please", "tell", "give", "get", "into", "out", "over", "under",
}


def parse_document(path: str) -> dict:
    """Return {section_no: clause_text} for a policy document."""
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            raw = f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as f:
            raw = f.read()
    except OSError as exc:
        print(f"ERROR: cannot read policy file {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    clauses = {}
    current = None
    text = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or BOX_LINE_RE.match(stripped):
            continue
        m = CLAUSE_RE.match(line)
        if m:
            if current:
                clauses[current] = " ".join(text)
            current = m.group(1)
            text = [m.group(2).strip()]
            continue
        m = SECTION_RE.match(line)
        if m:
            if current:
                clauses[current] = " ".join(text)
                current = None
            continue
        if current:
            text.append(stripped)
    if current:
        clauses[current] = " ".join(text)
    return clauses


def retrieve_documents():
    """Load all three policy files, indexed by document name and section."""
    base = Path(__file__).resolve().parent
    docs = {}
    for name in DOC_FILES:
        path = base.parent / "data" / "policy-documents" / name
        docs[name] = parse_document(str(path))
    return docs


def _tokens(text):
    words = WORD_RE.findall(text.lower())
    return words


def _clause_tokens(clause_text):
    words = _tokens(clause_text)
    out = set(words)
    for w in words:
        if "-" in w:
            out.update(w.split("-"))
    return out


def answer_question(docs: dict, question: str) -> str:
    """
    Answer from a single document with citation, or return the exact
    refusal template. Never blends documents.
    """
    q = question.strip().lower()

    # 1. Exact topic phrases first (deterministic, single-source).
    for phrases, doc_name, section in PHRASE_MAP:
        if all(p in q for p in phrases):
            text = docs[doc_name][section]
            return (
                f"{text}\n\n"
                f"Source: {doc_name}, section {section}"
            )

    # 2. IDF-weighted token scoring over all clauses.
    q_tokens = [t for t in _tokens(q) if t not in STOPWORDS and len(t) >= 3]
    if not q_tokens:
        return REFUSAL_TEMPLATE

    doc_freq = Counter()
    for clauses in docs.values():
        seen = set()
        for clause_text in clauses.values():
            seen.update(_clause_tokens(clause_text))
        for t in seen:
            doc_freq[t] += 1

    scores = {}  # (doc, section) -> score
    for doc_name, clauses in docs.items():
        for section, clause_text in clauses.items():
            c_tokens = _clause_tokens(clause_text)
            score = 0.0
            for t in q_tokens:
                if t in c_tokens:
                    score += 1.0 / doc_freq.get(t, 4)
            scores[(doc_name, section)] = score

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best, best_score = ranked[0]
    second, second_score = ranked[1] if len(ranked) > 1 else (None, 0.0)

    if best_score < 1.5:
        return REFUSAL_TEMPLATE

    # 3. Cross-document guard: if a close second-best answer lives in a
    #    different document, refuse rather than risk a blend.
    if second is not None and second[0] != best[0] and second_score >= 0.6 * best_score:
        return REFUSAL_TEMPLATE

    doc_name, section = best
    return (
        f"{docs[doc_name][section]}\n\n"
        f"Source: {doc_name}, section {section}"
    )


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--question", required=False,
        help="Answer a single question and exit (otherwise interactive).",
    )
    args = parser.parse_args()

    docs = retrieve_documents()
    print("Ask My Documents — CMC policy Q&A")
    print(f"Indexed documents: {', '.join(DOC_FILES)}")
    print("Type a question, or 'quit' / 'exit' to stop.")
    print()

    def handle(question):
        if not question.strip():
            return
        print(answer_question(docs, question))
        print()

    if args.question:
        handle(args.question)
        return

    while True:
        try:
            question = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.strip().lower() in ("quit", "exit", "q"):
            break
        handle(question)


if __name__ == "__main__":
    main()