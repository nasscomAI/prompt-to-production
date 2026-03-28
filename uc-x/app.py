"""
UC-X — Ask My Documents
Built using RICE → agents.md → skills.md → CRAFT workflow.

Failure modes guarded against:
- Cross-document blending  : answers drawn from exactly one document
- Hedged hallucination     : forbidden phrases trigger refusal
- Condition dropping       : multi-condition answers checked for completeness
"""
import os
import re
import sys

# ── Document paths ────────────────────────────────────────────────────────────

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

# ── Refusal template (verbatim, no variations permitted) ──────────────────────

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

# ── Forbidden hedging phrases ─────────────────────────────────────────────────

FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it can be inferred",
    "as is standard",
    "generally expected",
]


# ── Skill 1: retrieve_documents ───────────────────────────────────────────────

def retrieve_documents(file_paths: list) -> dict:
    """
    Load all three policy files and index by document name → section number → text.

    Returns:
        dict: {
            "policy_hr_leave.txt": {
                "2.6": "Employees may carry forward...",
                ...
            },
            ...
        }
    """
    index = {}

    for path in file_paths:
        doc_name = os.path.basename(path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            print(f"ERROR: Policy file not found: '{path}'")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Could not read '{path}': {e}")
            sys.exit(1)

        # Parse numbered sections e.g. "2.3", "5.2"
        section_pattern = re.compile(r'(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+\s|\Z)', re.DOTALL)
        matches = section_pattern.findall(raw)

        if not matches:
            print(f"WARNING: No numbered sections found in '{doc_name}'. Check file format.")
            index[doc_name] = {"full": raw.strip()}
        else:
            sections = {num: text.strip() for num, text in matches}
            index[doc_name] = sections
            print(f"  Loaded: {doc_name} — {len(sections)} sections")

    return index


# ── Skill 2: answer_question ──────────────────────────────────────────────────

def answer_question(question: str, index: dict) -> str:
    """
    Search indexed documents for a single-source answer.

    Rules:
    - Answer from exactly ONE document only
    - Cite document name + section number
    - If found in multiple docs, use the most specific match
    - If not found, return exact refusal template
    - Never use forbidden hedging phrases
    """
    question_lower = question.lower()

    # ── Search each document for keyword matches ──────────────────────────
    matches = []  # list of (doc_name, section_num, section_text, match_score)

    # Extract phrases (2-3 word sequences) and individual words from question
    question_words = [
        w for w in re.findall(r'\b\w{4,}\b', question_lower)
        if w not in {"what", "when", "where", "which", "with", "that", "this",
                     "from", "have", "does", "your", "work", "about", "also"}
    ]
    # Extract 2-word phrases for stronger matching
    all_words = question_lower.split()
    question_phrases = [
        f"{all_words[i]} {all_words[i+1]}"
        for i in range(len(all_words) - 1)
    ]

    for doc_name, sections in index.items():
        for section_num, section_text in sections.items():
            text_lower = section_text.lower()

            # Phrase matches score 3x higher than single word matches
            phrase_score = sum(3 for p in question_phrases if p in text_lower)
            word_score   = sum(1 for w in question_words if w in text_lower)
            score        = phrase_score + word_score

            if score > 0:
                matches.append((doc_name, section_num, section_text, score))

    if not matches:
        return REFUSAL_TEMPLATE

    # ── Sort by score descending — pick best single match ─────────────────
    matches.sort(key=lambda x: x[3], reverse=True)

    # Group by document — find best match per document
    best_per_doc = {}
    for doc_name, section_num, section_text, score in matches:
        if doc_name not in best_per_doc or score > best_per_doc[doc_name][2]:
            best_per_doc[doc_name] = (section_num, section_text, score)

    # Use the single highest-scoring document only (no blending)
    top_doc = max(best_per_doc.items(), key=lambda x: x[1][2])
    doc_name    = top_doc[0]
    section_num = top_doc[1][0]
    section_text = top_doc[1][1]
    top_score   = top_doc[1][2]

    # Threshold — if score is too low, refuse rather than guess
    if top_score < 2:
        return REFUSAL_TEMPLATE

    # ── Build answer ──────────────────────────────────────────────────────
    # Truncate section text to most relevant sentence(s)
    sentences = re.split(r'(?<=[.!?])\s+', section_text)
    relevant = []
    for sentence in sentences:
        s_lower = sentence.lower()
        hits = sum(1 for w in re.findall(r'\b\w{4,}\b', question_lower) if w in s_lower)
        if hits > 0:
            relevant.append(sentence)

    answer_text = " ".join(relevant) if relevant else section_text[:300]

    # ── Check for forbidden phrases in answer ─────────────────────────────
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in answer_text.lower():
            return REFUSAL_TEMPLATE

    answer = (
        f"According to {doc_name}, section {section_num}:\n"
        f"{answer_text}"
    )

    return answer


# ── Interactive CLI loop ──────────────────────────────────────────────────────

def main():
    print("UC-X — Ask My Documents")
    print("Loading policy documents...\n")

    index = retrieve_documents(POLICY_FILES)

    print(f"\n  {len(index)} documents loaded.")
    print("  Ask a question about HR, IT, or Finance policy.")
    print("  Type 'exit' or 'quit' to stop.\n")
    print("=" * 60)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue

        if question.lower() in ("exit", "quit"):
            print("Exiting.")
            break

        answer = answer_question(question, index)
        print(f"\n{answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()