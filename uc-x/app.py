"""
UC-X app.py — Ask My Documents.
Built per agents.md (role/intent/context/enforcement) and skills.md
(retrieve_documents, answer_question). Interactive CLI over three policy
documents; never blends claims across documents, refuses when nothing
in the documents answers the question.
"""
import re
from collections import Counter

DOCS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z][A-Z \(\)]*$")
RULE_LINE_PATTERN = re.compile(r"^[═=\-]+$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "i", "my", "me", "you", "your", "he", "she", "it", "its", "we", "they",
    "this", "that", "these", "those", "and", "or", "but", "if", "then", "so",
    "of", "in", "on", "at", "to", "for", "with", "from", "by", "as",
    "can", "could", "will", "would", "should", "do", "does", "did", "no",
    "what", "which", "when", "where", "why", "how",
}

# Acronyms that are exact, unambiguous equivalences (LWP always means "leave
# without pay" in either a question or the document itself) — safe to expand
# on both sides.
SYMMETRIC_ALIASES = {
    "lwp": ["leave", "without", "pay"],
    "da": ["daily", "allowance"],
}

# Everyday words a QUESTION might use that the policy documents phrase more
# formally. Expanded only on the question side — expanding on the document
# side too would let an unrelated clause that happens to mention "phone"
# (e.g. a reimbursement clause) get tagged as if it were about device access
# policy, which is exactly the false-match risk this UC is testing for.
QUERY_ONLY_ALIASES = {
    "phone": ["device"],
    "laptop": ["device", "corporate"],
    "files": ["data"],
    "slack": ["software"],
    "wfh": ["work", "home"],
}

# Explicit inflection -> canonical form. A generic suffix-stripping stemmer
# mishandles words like "devices" (device) vs "device" itself inconsistently;
# an explicit table for the vocabulary these documents actually use is safer.
WORD_FORMS = {
    "devices": "device", "device": "device",
    "approves": "approve", "approval": "approve", "approved": "approve", "approvals": "approve",
    "installs": "install", "installed": "install", "installation": "install", "installing": "install",
    "receipts": "receipt", "receipt": "receipt",
    "days": "day", "day": "day",
    "claims": "claim", "claimed": "claim", "claim": "claim",
    "phones": "phone", "phone": "phone",
    "employees": "employee", "employee": "employee",
}


def _stem(word: str) -> str:
    return WORD_FORMS.get(word, word)

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

MIN_SCORE = 0.45


def retrieve_documents(doc_paths: list) -> list:
    """
    Loads all policy files and indexes every numbered clause across them.
    Returns: list of {doc_name, clause_number, clause_text}.
    """
    index = []
    for path in doc_paths:
        doc_name = path.rsplit("/", 1)[-1]
        with open(path, encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f]

        current = None
        for line in lines:
            stripped = line.strip()
            match = CLAUSE_PATTERN.match(stripped)
            if match:
                if current:
                    index.append(current)
                current = {
                    "doc_name": doc_name,
                    "clause_number": match.group(1),
                    "clause_text": match.group(2),
                }
            elif (
                current
                and stripped
                and not RULE_LINE_PATTERN.match(stripped)
                and not SECTION_HEADER_PATTERN.match(stripped)
            ):
                current["clause_text"] += " " + stripped
        if current:
            index.append(current)

    if not index:
        raise ValueError("No numbered clauses found across the given documents.")

    return index


def _keywords(text: str, is_query: bool = False) -> list:
    words = re.findall(r"[a-z0-9]+", text.lower())
    expanded = []
    for w in words:
        if w in STOPWORDS:
            continue
        expanded.append(_stem(w))
        for alias in SYMMETRIC_ALIASES.get(w, []):
            expanded.append(_stem(alias))
        if is_query:
            for alias in QUERY_ONLY_ALIASES.get(w, []):
                expanded.append(_stem(alias))
    return [w for w in expanded if len(w) >= 2]


def _bigrams(words: list) -> set:
    return {f"{a} {b}" for a, b in zip(words, words[1:])}


# Raw-text phrase equivalences that token-level matching can't see because
# the trigger word ("phone") sits between the two words that need to be
# adjacent for the bigram to form ("personal" ... "device"). Checked against
# the original, untokenized text on both sides.
PHRASE_ALIASES = [
    ("personal phone", "personal device"),
    ("personal laptop", "personal device"),
    ("my phone", "personal device"),
    ("my laptop", "personal device"),
]


def _phrase_bonus(question: str, clause_text: str) -> float:
    q_lower, c_lower = question.lower(), clause_text.lower()
    return 3.0 * sum(1 for qp, cp in PHRASE_ALIASES if qp in q_lower and cp in c_lower)


def _score_clauses(question: str, index: list):
    q_words_list = _keywords(question, is_query=True)
    q_words_unique = set(q_words_list)
    if not q_words_unique:
        return []

    clause_word_lists = [_keywords(clause["clause_text"]) for clause in index]
    doc_freq = Counter()
    for words in clause_word_lists:
        for w in q_words_unique & set(words):
            doc_freq[w] += 1

    idf = {w: 1.0 / (1 + doc_freq.get(w, 0)) for w in q_words_unique}
    q_bigrams = _bigrams(q_words_list)

    scored = []
    for clause, words in zip(index, clause_word_lists):
        word_set = set(words)
        unigram_score = sum(idf[w] for w in q_words_unique if w in word_set)
        clause_bigrams = _bigrams(words)
        bigram_score = 2.0 * len(q_bigrams & clause_bigrams)
        total = unigram_score + bigram_score + _phrase_bonus(question, clause["clause_text"])
        if total > 0:
            scored.append((total, clause))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored


def answer_question(question: str, index: list) -> str:
    """
    Returns a single-source cited answer for the best-matching section,
    or the exact refusal template if nothing clears the relevance bar.
    Never combines wording from more than one document's clause.
    """
    scored = _score_clauses(question, index)
    if not scored or scored[0][0] < MIN_SCORE:
        return REFUSAL_TEMPLATE

    top_score, top_clause = scored[0]
    doc_label = {
        "policy_hr_leave.txt": "HR policy",
        "policy_it_acceptable_use.txt": "IT policy",
        "policy_finance_reimbursement.txt": "Finance policy",
    }.get(top_clause["doc_name"], top_clause["doc_name"])

    return (
        f"{doc_label}, section {top_clause['clause_number']}: {top_clause['clause_text']}\n"
        f"(Source: {top_clause['doc_name']}, section {top_clause['clause_number']} — single source, no other document consulted for this answer.)"
    )


def main():
    index = retrieve_documents(DOCS)
    print("UC-X — Ask My Documents")
    print(f"Indexed {len(index)} clauses across {len(DOCS)} documents.")
    print("Type a question and press Enter. Type 'exit' to quit.\n")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question or question.lower() in ("exit", "quit"):
            break
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()
