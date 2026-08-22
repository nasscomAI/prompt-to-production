"""
UC-X app.py — Ask My Documents.
No LLM is called here: this is a deterministic term-scoring retriever over the 3 policy
files. Rarer shared terms score higher (a lightweight IDF), each answer is drawn from
exactly one document, and everything that isn't a clean single-source match refuses
instead of blending or hedging.
"""
import argparse
import glob
import math
import os
import re
import sys
from collections import defaultdict

REFUSAL_NOT_COVERED = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "be", "do", "does", "did", "can", "could",
    "will", "would", "should", "of", "to", "for", "on", "in", "at", "and", "or", "my",
    "i", "me", "you", "your", "what", "who", "when", "where", "why", "how", "this",
    "that", "these", "those", "it", "its", "with", "as", "if", "not", "no",
}

DOC_META = {
    "policy_hr_leave.txt": "HR-POL-001",
    "policy_it_acceptable_use.txt": "IT-POL-003",
    "policy_finance_reimbursement.txt": "FIN-POL-007",
}

SECTION_PATTERN = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 /,&()]*)$")
CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
MIN_SCORE = 1.2

# A small domain thesaurus, not a per-question hack: "phone"/"laptop"/"mobile" are all
# the same governance concept (a personal computing device) in these policies, but pure
# keyword overlap can't see that "personal phone" and "personal devices" are the same topic.
ALIASES = {
    "phone": "device", "laptop": "device", "mobile": "device", "smartphone": "device",
    "tablet": "device",
}

# Acronyms the source documents introduce once and then use bare in later clauses
# (e.g. section 5 spells out "Leave Without Pay" only in 5.1, then says "LWP" in
# 5.2-5.4). Expanding them keeps those clauses discoverable on the spelled-out terms.
EXPANSIONS = {
    "lwp": ["leave", "withou", "pay"],
}


def _tokenize(text: str) -> set:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    stems = set()
    for w in words:
        if w in STOPWORDS or len(w) < 3:
            continue
        if w.endswith("s") and len(w) > 3:
            w = w[:-1]
        w = ALIASES.get(w, w)
        if w in EXPANSIONS:
            stems.update(EXPANSIONS[w])
        else:
            stems.add(w[:6])
    return stems


def _parse_policy_file(path: str) -> list:
    """Same section/clause parser as UC-0B, generalised across all 3 policy docs."""
    doc_name = os.path.basename(path)
    doc_ref = DOC_META.get(doc_name, doc_name)

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    clauses = []
    current_section_title = None
    current_clause = None  # [number, [text_parts]]

    def flush():
        if current_clause:
            clauses.append({
                "doc_name": doc_name,
                "doc_ref": doc_ref,
                "section_title": current_section_title,
                "clause_number": current_clause[0],
                "text": " ".join(current_clause[1]),
            })

    for raw_line in lines:
        line = raw_line.strip()
        if not line or set(line) == {"═"}:
            continue
        section_match = SECTION_PATTERN.match(line)
        clause_match = CLAUSE_PATTERN.match(line)

        if clause_match:
            flush()
            current_clause = [clause_match.group(1), [clause_match.group(2).strip()]]
        elif section_match:
            flush()
            current_clause = None
            current_section_title = section_match.group(2).strip()
        elif current_clause:
            current_clause[1].append(line)

    flush()
    return clauses


def retrieve_documents(paths: list):
    """Load and index every clause from all policy files; build an IDF table over all tokens."""
    clauses = []
    for path in paths:
        parsed = _parse_policy_file(path)
        if not parsed:
            raise ValueError(f"No clauses parsed from {path} — refusing to answer with a partial index.")
        clauses.extend(parsed)

    for clause in clauses:
        clause["tokens"] = _tokenize(clause["text"])

    doc_freq = defaultdict(int)
    for clause in clauses:
        for token in clause["tokens"]:
            doc_freq[token] += 1

    total_clauses = len(clauses)
    idf = {t: math.log(total_clauses / df) for t, df in doc_freq.items()}
    return clauses, idf


MIN_SHARED_TOKENS = 2  # a single shared word is too weak to trust as topical evidence


def _score(question_tokens: set, clause_tokens: set, idf: dict) -> float:
    """Score is 0 unless at least MIN_SHARED_TOKENS distinct words are shared — a lone
    coincidental match (e.g. "working" from an unrelated "10 working days" clause)
    must not be able to win on rarity alone."""
    shared = question_tokens & clause_tokens
    if len(shared) < MIN_SHARED_TOKENS:
        return 0.0
    return sum(idf.get(t, 0.0) for t in shared)


def answer_question(question: str, clauses: list, idf: dict) -> str:
    question_tokens = _tokenize(question)
    if not question_tokens:
        return REFUSAL_NOT_COVERED

    scored = [(_score(question_tokens, c["tokens"], idf), c) for c in clauses]
    scored = [(s, c) for s, c in scored if s > 0]
    if not scored:
        return REFUSAL_NOT_COVERED

    best_by_doc = defaultdict(float)
    for score, clause in scored:
        best_by_doc[clause["doc_name"]] = max(best_by_doc[clause["doc_name"]], score)

    top_score = max(best_by_doc.values())
    if top_score < MIN_SCORE:
        return REFUSAL_NOT_COVERED

    top_docs = [doc for doc, score in best_by_doc.items() if score == top_score]
    if len(top_docs) > 1:
        return (
            f"This question spans more than one policy document with no single authoritative "
            f"source ({', '.join(sorted(top_docs))}). Refusing rather than combining them into "
            f"one answer. Please contact the relevant department for guidance."
        )

    winning_doc = top_docs[0]
    doc_clauses = sorted(
        ((s, c) for s, c in scored if c["doc_name"] == winning_doc),
        key=lambda pair: pair[0],
        reverse=True,
    )[:3]

    doc_ref = doc_clauses[0][1]["doc_ref"]
    lines = [f"Source: {winning_doc} ({doc_ref})"]
    for _, clause in doc_clauses:
        lines.append(f"  [{clause['clause_number']}] {clause['text']}")
    return "\n".join(lines)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--docs-dir", default="../data/policy-documents",
        help="Directory containing the policy .txt files",
    )
    args = parser.parse_args()

    paths = sorted(glob.glob(os.path.join(args.docs_dir, "*.txt")))
    if not paths:
        raise SystemExit(f"No policy .txt files found in {args.docs_dir}")

    clauses, idf = retrieve_documents(paths)
    print(f"Loaded {len(clauses)} clauses from {len(paths)} policy documents. Ask a question ('exit' to quit).")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question or question.lower() in ("exit", "quit"):
            break
        print(answer_question(question, clauses, idf))
        print()


if __name__ == "__main__":
    main()
