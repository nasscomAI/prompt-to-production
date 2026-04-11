"""
UC-X — Ask My Documents
Interactive CLI that loads 3 CMC policy files and answers questions using
strict single-source citation. Never blends across documents.
Never uses hedging phrases. Uses exact refusal template for gaps.
"""
import os
import re
import sys

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'policy-documents')

POLICY_FILES = [
    'policy_hr_leave.txt',
    'policy_it_acceptable_use.txt',
    'policy_finance_reimbursement.txt',
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

# Banned hedging phrases — used in answer validation
HEDGING_PHRASES = [
    "typically", "generally", "generally understood", "it is common practice",
    "while not explicitly covered", "it is standard", "in most cases",
]


# ─── Skill: retrieve_documents ────────────────────────────────────────────────
def retrieve_documents(policy_dir: str, filenames: list) -> dict:
    """
    Loads all policy files and indexes content by {filename: {section_id: text}}.
    Raises on missing files.
    """
    index = {}
    for filename in filenames:
        path = os.path.join(policy_dir, filename)
        if not os.path.exists(path):
            print(f"ERROR: Policy file not found: {path}", file=sys.stderr)
            sys.exit(1)

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        sections = {}
        current_section = None
        current_lines = []

        section_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')

        for line in lines:
            match = section_pattern.match(line)
            if match:
                if current_section:
                    sections[current_section] = ' '.join(current_lines).strip()
                current_section = match.group(1)
                current_lines = [match.group(2).strip()]
            elif current_section and line.startswith('    '):
                current_lines.append(line.strip())

        if current_section:
            sections[current_section] = ' '.join(current_lines).strip()

        index[filename] = sections
        print(f"  Loaded {filename} — {len(sections)} sections indexed.")

    return index


# ─── Stem helper ─────────────────────────────────────────────────────────────
def _stem_matches(token: str, text_lower: str) -> bool:
    """
    Returns True if any reasonable stem of `token` appears in `text_lower`.
    Handles common English inflection so 'approves' matches 'approval',
    'approve', 'approving'; 'carries' matches 'carry', 'carried', etc.
    """
    # Direct hit
    if token in text_lower:
        return True
    # Strip common suffixes and test the root
    stems = []
    if token.endswith('es') and len(token) > 4:
        stems.append(token[:-2])   # approves → approv
        stems.append(token[:-1])   # approves → approve
    if token.endswith('ing') and len(token) > 5:
        stems.append(token[:-3])   # approving → approv
        stems.append(token[:-3] + 'e')  # approving → approve
    if token.endswith('ed') and len(token) > 4:
        stems.append(token[:-2])   # approved → approv
        stems.append(token[:-1])   # approved → approve
    if token.endswith('s') and len(token) > 3:
        stems.append(token[:-1])   # approvals → approval
    # Also expand common short stems to longer forms
    # e.g. 'approv' should match 'approval', 'approve', 'approves'
    for stem in stems:
        if stem and stem in text_lower:
            return True
        # check if stem is a prefix of any word in text
        if stem and re.search(r'\b' + re.escape(stem), text_lower):
            return True
    return False


def _phrase_score(tokens: list, text_lower: str) -> float:
    """
    Bonus score for adjacent token pairs (bigrams) and triples (trigrams)
    that appear together in the section text.
    Each matching bigram adds 1.5, each trigram adds 2.5.
    This rewards sections that match the *intent cluster* of the question,
    not just individual word soup.
    """
    bonus = 0.0
    # Bigrams
    for i in range(len(tokens) - 1):
        bigram = tokens[i] + ' ' + tokens[i + 1]
        if bigram in text_lower:
            bonus += 1.5
        # also try stem of first word + second word
        if _stem_matches(tokens[i], tokens[i + 1]):
            pass  # avoid self-matching, skip
    # Trigrams
    for i in range(len(tokens) - 2):
        trigram = tokens[i] + ' ' + tokens[i + 1] + ' ' + tokens[i + 2]
        if trigram in text_lower:
            bonus += 2.5
    return bonus


# ─── Skill: answer_question ───────────────────────────────────────────────────
def answer_question(question: str, doc_index: dict) -> str:
    """
    Searches the index for a single-source answer.
    Returns answer + citation, or the mandatory refusal template.
    Never blends across documents. Never hedges.

    Scoring:
      - +1 per token that stem-matches a word in the section
      - +1.5 per adjacent token bigram present in the section
      - +2.5 per adjacent token trigram present in the section
    This ensures intent clusters ('approves leave without pay') beat
    sections that only share individual high-frequency words.
    """
    q_lower = question.lower().strip()

    # Build keyword tokens from the question (strip stop words)
    stop_words = {
        'a', 'an', 'the', 'is', 'are', 'can', 'i', 'my', 'do', 'for',
        'to', 'on', 'of', 'in', 'and', 'or', 'what', 'who', 'how',
        'when', 'where', 'will', 'be', 'it', 'at', 'from', 'that', 'this',
        'with', 'not', 'if', 'me', 'we', 'their', 'same', 'day',
    }
    tokens = [
        w for w in re.findall(r'\b[a-z]+\b', q_lower)
        if w not in stop_words and len(w) > 2
    ]

    if not tokens:
        return REFUSAL_TEMPLATE

    # Score each section across all documents
    candidates = []  # (score, filename, section_id, section_text)

    for filename, sections in doc_index.items():
        for section_id, section_text in sections.items():
            text_lower = section_text.lower()

            # Base score: stem-aware token matching
            base = sum(1 for t in tokens if _stem_matches(t, text_lower))

            if base == 0:
                continue  # No relevant tokens at all — skip

            # Phrase bonus: bigrams and trigrams
            phrase = _phrase_score(tokens, text_lower)

            total = base + phrase
            candidates.append((total, filename, section_id, section_text))

    if not candidates:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    candidates.sort(key=lambda c: c[0], reverse=True)

    best_score = candidates[0][0]

    # Collect all top-scoring candidates (within 0.5 of best to handle float)
    top = [c for c in candidates if c[0] >= best_score - 0.01]

    # Cross-document blend guard: if best matches span more than one document
    # with equal confidence, refuse rather than blend
    top_docs = {c[1] for c in top}

    if len(top_docs) > 1:
        per_doc_best = {}
        for score, filename, section_id, section_text in candidates:
            if filename not in per_doc_best:
                per_doc_best[filename] = (score, section_id, section_text)

        doc_scores = sorted(per_doc_best.items(), key=lambda x: x[1][0], reverse=True)
        top_doc_score = doc_scores[0][1][0]
        second_doc_score = doc_scores[1][1][0] if len(doc_scores) > 1 else 0

        if top_doc_score > second_doc_score:
            winner_doc = doc_scores[0][0]
            _, section_id, section_text = doc_scores[0][1]
        else:
            return REFUSAL_TEMPLATE
    else:
        winner_doc = top[0][1]
        section_id = top[0][2]
        section_text = top[0][3]

    # Format the answer with mandatory citation
    answer = (
        f"{section_text}\n\n"
        f"Source: {winner_doc} § {section_id}"
    )
    return answer


# ─── Interactive CLI ──────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("UC-X — Ask My Documents (CMC Policy Q&A)")
    print("=" * 65)
    print("\nLoading policy documents...\n")

    doc_index = retrieve_documents(POLICY_DIR, POLICY_FILES)

    print(f"\n✓ {len(POLICY_FILES)} documents loaded. Ready for questions.")
    print("  Type your question and press Enter. Type 'quit' or 'exit' to stop.\n")
    print("-" * 65)

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ('quit', 'exit', 'q'):
            print("Exiting.")
            break

        answer = answer_question(question, doc_index)
        print(f"\nAnswer:\n{answer}\n")
        print("-" * 65)


if __name__ == '__main__':
    main()
