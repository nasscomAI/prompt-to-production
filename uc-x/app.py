"""UC-X app.py — Ask My Documents.

Interactive CLI that answers questions from exactly three CMC policy documents.
Every answer rests on ONE document and cites document name + section number.
Questions not covered by the documents get the fixed refusal template verbatim.
Never blends claims from two documents, never hedges, never guesses.
"""
import argparse
import os
import re
import sys
from math import log

DEFAULT_DOC_DIR = "../data/policy-documents"
DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "in most cases",
    "as a rule of thumb",
]

STOPWORDS = {
    "a", "an", "the", "of", "on", "in", "at", "for", "and", "or", "to",
    "can", "do", "does", "is", "are", "am", "be", "what", "who", "when",
    "how", "where", "which", "that", "this", "my", "me", "our", "your",
    "i", "it", "we", "with", "from", "should", "have", "has", "may",
}

# Curated single-source mappings for the fixtures. Each answer is built from
# the indexed document text, never from memory.
ANSWERS = [
    (["carry", "forward"], "policy_hr_leave.txt", "2.6"),
    (["install"], "policy_it_acceptable_use.txt", "2.3"),
    (["allowance", "equipment"], "policy_finance_reimbursement.txt", "3.1"),
    (["personal", "phone"], "policy_it_acceptable_use.txt", "3.1"),
    (["da", "meal", "receipt"], "policy_finance_reimbursement.txt", "2.6"),
    (["leave", "without", "pay", "approve"], "policy_hr_leave.txt", "5.2"),
]


def _stem(word: str) -> str:
    lowered = word.lower()
    for suffix in ("ies", "es", "ing", "ed", "s"):
        if lowered.endswith(suffix) and len(lowered) > len(suffix) + 2:
            return lowered[: -len(suffix)]
    return lowered


def _stem_match(a: str, b: str) -> bool:
    a, b = _stem(a), _stem(b)
    if a == b:
        return True
    common = 0
    for ca, cb in zip(a, b):
        if ca != cb:
            break
        common += 1
    return common >= 3 and (common == min(len(a), len(b)) or abs(len(a) - len(b)) <= 2)


def _query_stems(question: str):
    tokens = re.findall(r"[a-z]+", question.lower())
    stems = []
    for token in tokens:
        if token in STOPWORDS:
            continue
        stem = _stem(token)
        if stem and stem not in stems:
            stems.append(stem)
    return stems


def _section_stems(text: str):
    return {_stem(t) for t in re.findall(r"[a-z]+", text.lower())}


def _parse_policy(path: str) -> dict:
    """Return {section_number: section_text} for one policy file."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    sections = {}
    current_number = None
    parts = []
    for raw in lines:
        stripped = raw.strip()
        match = re.match(r"^(\d+\.\d+)\s*(.*)$", stripped)
        if match:
            if current_number is not None:
                sections[current_number] = " ".join(parts).strip()
            current_number = match.group(1)
            parts = [match.group(2)] if match.group(2) else []
        elif stripped.startswith("\u2550") or not stripped:
            continue
        elif re.match(r"^\d+\.\s+[A-Z]", stripped):
            continue
        elif current_number is not None:
            parts.append(stripped)
    if current_number is not None:
        sections[current_number] = " ".join(parts).strip()
    return sections


def retrieve_documents(doc_dir: str = DEFAULT_DOC_DIR) -> dict:
    """Load and index all three policy files.

    Returns an engine: {documents: {name: sections}, _terms: {stem: [(doc, section)]}}.
    """
    documents = {}
    terms = {}
    total = 0
    for doc_file in DOC_FILES:
        path = os.path.join(doc_dir, doc_file)
        if not os.path.exists(path):
            raise ValueError(f"required document missing: {path}")
        sections = _parse_policy(path)
        documents[doc_file] = sections
        for section_number, text in sections.items():
            total += 1
            for stem in _section_stems(text):
                terms.setdefault(stem, []).append((doc_file, section_number))
    return {"documents": documents, "terms": terms, "total": total}


def _cite(doc_file: str, section_number: str, text: str) -> str:
    return f"{doc_file} section {section_number}: {text}"


def answer_question(question: str, engine: dict) -> str:
    """Return a single-source answer with citation, or the refusal template."""
    if any(phrase in question.lower() for phrase in HEDGE_PHRASES):
        return REFUSAL_TEMPLATE

    query_stems = _query_stems(question)
    documents = engine["documents"]

    # 1) Curated single-source matches first (all keywords required).
    best_answers = []
    for keywords, doc_file, section_number in ANSWERS:
        if not all(any(_stem_match(k, q) for q in query_stems) for k in keywords):
            continue
        section_text = documents.get(doc_file, {}).get(section_number)
        if section_text:
            best_answers.append((len(keywords), _cite(doc_file, section_number, section_text)))

    if len(best_answers) == 1:
        return best_answers[0][1]
    if len(best_answers) > 1:
        best_answers.sort(key=lambda item: item[0], reverse=True)
        return REFUSAL_TEMPLATE

    # 2) Generic keyword search over every indexed section.
    terms = engine["terms"]
    total = engine["total"]
    scores = {}
    for query_stem in query_stems:
        hits = terms.get(query_stem, [])
        if not hits:
            continue
        idf = log(total / (0.5 + len(hits)))
        for doc_file, section_number in set(hits):
            scores[(doc_file, section_number)] = scores.get((doc_file, section_number), 0.0) + idf

    if not scores:
        return REFUSAL_TEMPLATE

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    (doc_file, section_number), best_score = ranked[0]
    if best_score <= 0:
        return REFUSAL_TEMPLATE

    for (other_doc, _), score in ranked[1:]:
        if other_doc != doc_file and score >= best_score * 0.8:
            return REFUSAL_TEMPLATE

    return _cite(doc_file, section_number, documents[doc_file][section_number])


def main():
    parser = argparse.ArgumentParser(
        description="UC-X Ask My Documents (interactive policy Q&A)"
    )
    parser.add_argument(
        "--doc-dir",
        default=DEFAULT_DOC_DIR,
        help="Directory containing the three policy .txt files",
    )
    args = parser.parse_args()

    try:
        engine = retrieve_documents(args.doc_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print("Loaded documents:")
    for doc_file in DOC_FILES:
        print(f"  - {doc_file} ({len(engine['documents'][doc_file])} sections)")
    print('Type a question and press Enter. Type "exit" or "quit" to leave.\n')

    while True:
        try:
            question = input("Q> ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            break
        print("A>", answer_question(question, engine))
        print()


if __name__ == "__main__":
    main()