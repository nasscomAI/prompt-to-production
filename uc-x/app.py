"""
UC-X — Ask My Documents: Policy Q&A CLI
Interactive CLI that answers employee questions from three CMC policy documents.

Enforcement rules from agents.md:
1. Never blend answers from two different documents.
2. No hedging phrases — cite document + section or refuse.
3. Use exact refusal template when question is not covered.
4. Cite document name and section number for every factual claim.

Run command:
    python app.py

Policy documents are expected at:
    ../data/policy-documents/policy_hr_leave.txt
    ../data/policy-documents/policy_it_acceptable_use.txt
    ../data/policy-documents/policy_finance_reimbursement.txt
"""
import os
import re
import sys

# --- Exact refusal template (from agents.md) — no variations permitted ---
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# --- Banned hedging phrases ---
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually in government",
]

POLICY_FILES = [
    ("policy_hr_leave.txt",           "../data/policy-documents/policy_hr_leave.txt"),
    ("policy_it_acceptable_use.txt",  "../data/policy-documents/policy_it_acceptable_use.txt"),
    ("policy_finance_reimbursement.txt", "../data/policy-documents/policy_finance_reimbursement.txt"),
]


def retrieve_documents(document_paths: list[tuple[str, str]]) -> tuple[dict, list]:
    """
    Load all policy .txt files. Build:
      documents: {doc_name: {section_id: section_text}}
      index: [(doc_name, section_id, section_text), ...]
    """
    documents = {}
    index = []

    for doc_name, file_path in document_paths:
        # Resolve relative to this script's location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.normpath(os.path.join(base_dir, file_path))

        if not os.path.exists(abs_path):
            print(f"[WARN] File not found, skipping: {abs_path}", file=sys.stderr)
            continue

        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            print(f"[WARN] File is empty, skipping: {abs_path}", file=sys.stderr)
            continue

        sections = {}
        current_clause = None
        current_lines = []

        for line in content.splitlines():
            stripped = line.strip()
            clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', stripped)
            if clause_match:
                if current_clause:
                    sections[current_clause] = " ".join(current_lines).strip()
                current_clause = clause_match.group(1)
                current_lines = [clause_match.group(2)]
            elif current_clause and stripped and not stripped.startswith("═"):
                current_lines.append(stripped)

        if current_clause:
            sections[current_clause] = " ".join(current_lines).strip()

        documents[doc_name] = sections
        for sec_id, text in sections.items():
            index.append((doc_name, sec_id, text))

    if not index:
        raise RuntimeError(
            "No documents loaded — cannot answer questions. "
            "Check that policy files exist in ../data/policy-documents/"
        )

    return documents, index


# Synonym map: expand query words to policy vocabulary
# e.g. 'slack', 'teams', 'zoom' → 'software' (what the IT policy actually says)
SYNONYMS: dict[str, list[str]] = {
    # App names → generic policy term
    "slack": ["software", "install"],
    "teams": ["software", "install"],
    "zoom": ["software", "install"],
    "whatsapp": ["software", "personal"],
    "chrome": ["software", "browser"],
    # Device synonyms
    "phone": ["personal", "device", "byod"],
    "mobile": ["personal", "device"],
    "laptop": ["device", "corporate", "software"],
    "computer": ["device", "corporate"],
    # Action synonyms
    "install": ["software", "install"],
    "add": ["install", "software"],
    "download": ["software", "install"],
    # Leave synonyms
    "lwp": ["leave", "without", "pay", "approval"],
    "unpaid": ["leave", "without", "pay"],
    # Finance synonyms
    "da": ["daily", "allowance"],
    "meal": ["meal", "food", "receipt"],
    "reimburse": ["reimburs", "claim"],
    "claim": ["claim", "reimburs"],
    "wfh": ["work", "home", "remote"],
}


def _expand_words(words: list[str]) -> list[str]:
    """Expand query words using synonym map."""
    expanded = list(words)
    for w in words:
        if w in SYNONYMS:
            expanded.extend(SYNONYMS[w])
    return expanded


def _stem(word: str) -> str:
    """Very lightweight stemmer: strip common suffixes to get root."""
    for suffix in ("ing", "tion", "ves", "es", "ed", "al", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def _keyword_score(text: str, question_words: list[str]) -> int:
    """Return count of question words found in text using stem matching."""
    text_lower = text.lower()
    score = 0
    for w in question_words:
        w_stem = _stem(w.lower())
        if w_stem in text_lower or w.lower() in text_lower:
            score += 1
    return score


def answer_question(question: str, index: list, documents: dict) -> str:
    """
    Search indexed policy sections for the best single-source answer.
    Returns a cited answer or the exact refusal template.
    Never blends two documents.
    """
    # Tokenize and filter stopwords
    stopwords = {
        "i", "can", "a", "the", "my", "is", "are", "for", "on", "in",
        "of", "to", "do", "be", "and", "or", "what", "how", "who",
        "when", "any", "with", "at", "from", "it", "that", "this",
        "have", "has", "was", "will", "use",
    }
    q_words = [
        w.strip("?,.'\"").lower()
        for w in question.split()
        if w.strip("?,.'\"").lower() not in stopwords and len(w) > 1
    ]

    if not q_words:
        return REFUSAL_TEMPLATE

    # Expand with synonyms (e.g. 'slack' → ['software', 'install'])
    q_words_expanded = _expand_words(q_words)

    # Score all sections using expanded query words
    scored = []
    for doc_name, sec_id, text in index:
        score = _keyword_score(text, q_words_expanded)
        if score > 0:
            scored.append((score, doc_name, sec_id, text))

    scored.sort(key=lambda x: -x[0])  # highest score first

    # Require at least 2 keyword hits to avoid spurious single-word matches
    if not scored or scored[0][0] < 2:
        return REFUSAL_TEMPLATE

    top_score = scored[0][0]
    top_matches = [s for s in scored if s[0] == top_score]

    # Check for cross-document blending risk
    top_docs = set(m[1] for m in top_matches)
    if len(top_docs) > 1:
        # Multiple documents tie for top score — blending risk → refuse
        return REFUSAL_TEMPLATE

    # Single-source answer
    _, doc_name, sec_id, text = top_matches[0]
    # Collect sections from same doc with the top score only (no tolerance — avoids noise)
    same_doc_sections = [
        (m[2], m[3]) for m in scored
        if m[1] == doc_name and m[0] == top_score
    ]
    # Sort by section number so output is in logical document order
    same_doc_sections.sort(key=lambda t: [int(x) for x in t[0].split(".") if x.isdigit()])

    # Build answer
    citations = []
    for s_id, s_text in same_doc_sections[:4]:  # up to 4 best matching sections
        citations.append(f"  [{doc_name}, Section {s_id}] {s_text}")

    answer = f"Based on {doc_name}:\n" + "\n".join(citations)
    return answer


def main():
    print("UC-X — CMC Policy Q&A")
    print("Loading policy documents...")

    try:
        documents, index = retrieve_documents(POLICY_FILES)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    doc_count = len(documents)
    section_count = len(index)
    print(f"Loaded {doc_count} documents, {section_count} sections indexed.")
    print("-" * 60)
    print("Type your question and press Enter. Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("exit", "quit", "q"):
            print("Exiting.")
            break

        if not question:
            continue

        answer = answer_question(question, index, documents)

        # --- Enforcement: self-check for hedging phrases ---
        for phrase in HEDGING_PHRASES:
            if phrase.lower() in answer.lower():
                # This should never happen with our implementation, but defence in depth
                answer = REFUSAL_TEMPLATE
                break

        print(f"\nAnswer:\n{answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
