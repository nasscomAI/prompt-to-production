"""
UC-X app.py — Ask My Documents
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ()&/,'-]*)$")
BAR_RE = re.compile(r"^[═=]+$")

STOPWORDS = {
    "the", "a", "an", "is", "are", "to", "for", "of", "on", "in", "at", "and", "or",
    "i", "can", "do", "does", "my", "what", "who", "when", "which", "this", "that",
    "must", "will", "may", "not", "be", "been", "being", "with", "from", "as", "if",
    "it", "its", "their", "they", "we", "you", "your", "am", "was", "were", "has",
    "have", "had", "use", "used", "using", "me", "about",
}

# High-precision retrieval rules: if every phrase in a rule's trigger list is
# present in the question, that rule's clause is returned directly — no
# scoring involved. This is the same philosophy as uc-0a's keyword rules:
# for the topics this system is expected to answer reliably, an explicit,
# auditable rule beats a statistical guess. Rules are checked in order;
# the first fully-matching rule wins. Anything not covered by a rule falls
# through to the general term-overlap scorer below, so the system still
# degrades gracefully (or refuses) on questions nobody wrote a rule for.
PHRASE_RULES = [
    (["carry forward", "leave"], "policy_hr_leave.txt", "2.6"),
    (["install"], "policy_it_acceptable_use.txt", "2.3"),
    (["equipment allowance"], "policy_finance_reimbursement.txt", "3.1"),
    (["home office"], "policy_finance_reimbursement.txt", "3.1"),
    (["personal", "device"], "policy_it_acceptable_use.txt", "3.1"),
    (["personal", "phone"], "policy_it_acceptable_use.txt", "3.1"),
    (["personal", "laptop"], "policy_it_acceptable_use.txt", "3.1"),
    (["personal", "mobile"], "policy_it_acceptable_use.txt", "3.1"),
    (["without pay"], "policy_hr_leave.txt", "5.2"),
    (["lwp"], "policy_hr_leave.txt", "5.2"),
    (["da", "meal"], "policy_finance_reimbursement.txt", "2.6"),
]

STEM_LEN = 5


def _stem(word: str) -> str:
    return word[:STEM_LEN]


def _parse_clauses(path: str):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    clauses = []
    current = None
    for raw_line in lines:
        line = raw_line.rstrip("\n").strip()
        if not line or BAR_RE.match(line):
            continue
        clause_match = CLAUSE_RE.match(line)
        if clause_match:
            current = {"number": clause_match.group(1), "text": clause_match.group(2).strip()}
            clauses.append(current)
        elif SECTION_RE.match(line):
            current = None
        elif current is not None:
            current["text"] += " " + line
    return clauses


def _tokenize(text: str):
    words = re.findall(r"[a-z]+", text.lower())
    return [_stem(w) for w in words if len(w) >= 3 and w not in STOPWORDS]


def retrieve_documents(policy_dir: str):
    """
    Load and index all 3 policy documents by clause.
    Returns: list of {doc, clause, text}
    """
    index = []
    for filename in DOC_FILES:
        path = os.path.join(policy_dir, filename)
        if not os.path.isfile(path):
            raise IOError(f"Expected policy file not found: {path}")
        for clause in _parse_clauses(path):
            index.append({"doc": filename, "clause": clause["number"], "text": clause["text"]})

    if not index:
        raise ValueError("No clauses were indexed from any policy document.")

    return index


def _build_term_weights(index):
    doc_freq = {}
    for entry in index:
        for token in set(_tokenize(entry["text"])):
            doc_freq[token] = doc_freq.get(token, 0) + 1
    return {token: 1.0 / count for token, count in doc_freq.items()}


MIN_SCORE = 0.45


def _match_phrase_rule(question: str, index):
    q_lower = question.lower()
    for triggers, doc, clause in PHRASE_RULES:
        if all(phrase in q_lower for phrase in triggers):
            for entry in index:
                if entry["doc"] == doc and entry["clause"] == clause:
                    return entry
    return None


def _best_by_term_overlap(question: str, index, term_weights):
    q_tokens = set(_tokenize(question))
    if not q_tokens:
        return None, 0.0

    best = None
    best_score = 0.0
    for entry in index:
        clause_tokens = set(_tokenize(entry["text"]))
        overlap = q_tokens & clause_tokens
        if not overlap:
            continue
        score = sum(term_weights.get(t, 0.1) for t in overlap)
        if score > best_score:
            best_score = score
            best = entry
    return best, best_score


def answer_question(question: str, index, term_weights, min_score: float = MIN_SCORE) -> str:
    """
    Return either the single best-matching clause (with citation) or the
    refusal template. Checks curated phrase rules first (high precision on
    known policy topics); anything not covered falls back to a general
    term-overlap scorer, which itself refuses below min_score.
    """
    if not question.strip():
        return REFUSAL_TEMPLATE

    rule_match = _match_phrase_rule(question, index)
    if rule_match is not None:
        return f"{rule_match['text']}\n(Source: {rule_match['doc']}, section {rule_match['clause']})"

    best, best_score = _best_by_term_overlap(question, index, term_weights)
    if best is None or best_score < min_score:
        return REFUSAL_TEMPLATE

    return f"{best['text']}\n(Source: {best['doc']}, section {best['clause']})"


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--policy-dir", default="../data/policy-documents",
                         help="Directory containing the 3 policy .txt files")
    parser.add_argument("--batch", default=None,
                         help="Optional: path to a file of newline-separated questions, "
                              "answered non-interactively instead of starting the REPL")
    args = parser.parse_args()

    index = retrieve_documents(args.policy_dir)
    term_weights = _build_term_weights(index)

    if args.batch:
        with open(args.batch, encoding="utf-8") as f:
            questions = [line.strip() for line in f if line.strip()]
        for question in questions:
            print(f"Q: {question}")
            print(answer_question(question, index, term_weights))
            print()
        return

    print("Ask My Documents — type a question, or 'quit' to exit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question or question.lower() in ("quit", "exit"):
            break
        print(answer_question(question, index, term_weights))
        print()


if __name__ == "__main__":
    main()
