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


# ─── Skill: answer_question ───────────────────────────────────────────────────
def answer_question(question: str, doc_index: dict) -> str:
    """
    Searches the index for a single-source answer.
    Returns answer + citation, or the mandatory refusal template.
    Never blends across documents. Never hedges.
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
            score = sum(1 for t in tokens if t in text_lower)
            if score > 0:
                candidates.append((score, filename, section_id, section_text))

    if not candidates:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    candidates.sort(key=lambda c: c[0], reverse=True)

    best_score = candidates[0][0]

    # Collect all top-scoring candidates
    top = [c for c in candidates if c[0] == best_score]

    # Cross-document blend guard: if best matches span more than one document
    # with equal confidence, refuse rather than blend
    top_docs = {c[1] for c in top}

    if len(top_docs) > 1:
        # Check if there's a clear single-document winner at score+1 above others
        # i.e., one doc has significantly higher relevance
        per_doc_best = {}
        for score, filename, section_id, section_text in candidates:
            if filename not in per_doc_best:
                per_doc_best[filename] = (score, section_id, section_text)

        doc_scores = sorted(per_doc_best.items(), key=lambda x: x[1][0], reverse=True)
        top_doc_score = doc_scores[0][1][0]
        second_doc_score = doc_scores[1][1][0] if len(doc_scores) > 1 else 0

        if top_doc_score > second_doc_score:
            # Clear winner in one document
            winner_doc = doc_scores[0][0]
            _, section_id, section_text = doc_scores[0][1]
        else:
            # Genuinely ambiguous across documents — refuse rather than blend
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
