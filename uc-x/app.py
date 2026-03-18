"""
UC-X app.py — Ask My Documents
Interactive CLI that answers questions from three CMC policy documents.
Enforces single-source answers and uses the exact refusal template for
questions not covered by the available documents.
"""
import os
import re

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
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

# Synonym / expansion map: question word → additional words to match in sections
SYNONYM_MAP = {
    "install": ["install", "installation", "software"],
    "laptop": ["laptop", "device", "devices", "corporate"],
    "phone": ["phone", "personal", "devices", "byod"],
    "personal": ["personal", "byod"],
    "approves": ["approval", "approve", "approves", "requires"],
    "approve": ["approval", "approve", "approves", "requires"],
    "approval": ["approval", "approve", "approves", "requires"],
    "sick": ["sick"],
    "carry": ["carry", "forward", "carryforward"],
    "forward": ["carry", "forward"],
    "unused": ["unused", "carry", "forward"],
    "claim": ["claim", "claims", "claimable", "reimbursable"],
    "reimbursement": ["reimburse", "reimbursement", "reimbursable", "claim"],
    "da": ["da", "daily", "allowance"],
    "meal": ["meal", "meals", "food", "receipts"],
    "lwp": ["lwp", "leave", "without", "pay"],
    "work": ["work", "official", "corporate"],
    "files": ["files", "data", "documents", "access"],
    "home": ["home", "wfh", "remote", "work-from-home"],
    "equipment": ["equipment", "allowance", "home"],
    "encash": ["encash", "encashment", "cash"],
    "flexible": ["flexible", "flexibility", "culture", "norms", "remote"],
}

STOPWORDS = {
    "i", "my", "the", "a", "an", "is", "are", "can", "do", "to",
    "for", "in", "on", "at", "of", "and", "or", "with", "from",
    "what", "when", "how", "who", "where", "which", "that", "be",
    "me", "it", "if", "same", "any",
}


def retrieve_documents(paths: list) -> tuple:
    """
    Load and index all policy documents.
    Returns (index, flat_entries).
    index: {filename: {section_number: section_text}}
    flat_entries: [(filename, section_number, section_text)]
    """
    index = {}
    flat_entries = []

    clause_pattern = re.compile(
        r'^\s*(\d+\.\d+)\s+(.+?)(?=\n\s*\d+\.\d+\s|\n\s*[═]+|\Z)',
        re.DOTALL | re.MULTILINE,
    )

    for path in paths:
        doc_name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            raw = f.read()

        sections = {}
        for match in clause_pattern.finditer(raw):
            num = match.group(1).strip()
            text = re.sub(r'\s+', ' ', match.group(2)).strip()
            sections[num] = text
            flat_entries.append((doc_name, num, text))

        index[doc_name] = sections

    return index, flat_entries


def _expand_keywords(words: set) -> set:
    """Expand question keywords using the synonym map."""
    expanded = set(words)
    for word in words:
        for synonym in SYNONYM_MAP.get(word.lower(), []):
            expanded.add(synonym.lower())
    return expanded


def _score_entry(question_keywords_expanded: set, section_text: str) -> int:
    """Keyword overlap score with expanded synonyms."""
    section_words = set(re.findall(r'\w+', section_text.lower()))
    return len(question_keywords_expanded & section_words)


def answer_question(question: str, flat_entries: list) -> str:
    """
    Search indexed documents for an answer.
    Returns a single-source cited answer or the refusal template.
    """
    q_lower = question.lower().strip()
    raw_words = set(re.findall(r'\w+', q_lower)) - STOPWORDS
    if not raw_words:
        return REFUSAL_TEMPLATE

    expanded = _expand_keywords(raw_words)

    # Score every section
    scored = [
        (doc_name, sec_num, sec_text, _score_entry(expanded, sec_text))
        for doc_name, sec_num, sec_text in flat_entries
    ]
    scored.sort(key=lambda x: x[3], reverse=True)

    top_score = scored[0][3] if scored else 0
    if top_score < 2:
        return REFUSAL_TEMPLATE

    # Collect all entries that tie at the top score
    top_entries = [e for e in scored if e[3] == top_score]

    # Check if multiple documents are represented at the top score
    top_docs = {e[0] for e in top_entries}

    if len(top_docs) > 1:
        # Multiple documents match equally — use refusal to avoid blending
        return REFUSAL_TEMPLATE

    # Single-source answer — pick the highest-scoring entry from that document
    best = top_entries[0]
    doc_name, sec_num, sec_text, _ = best
    return (
        f"According to {doc_name}, section {sec_num}:\n"
        f"{sec_text}"
    )


def main():
    paths = [os.path.join(POLICY_DIR, fn) for fn in POLICY_FILES]

    print("UC-X — Ask My Documents")
    print("Loading policy documents...")
    try:
        index, flat_entries = retrieve_documents(paths)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    loaded = list(index.keys())
    print(f"Loaded: {', '.join(loaded)}")
    print()
    print("Type your question and press Enter. Type 'quit' to exit.")
    print("-" * 60)

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(question, flat_entries)
        print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()
