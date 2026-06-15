"""
UC-X app.py — Multi-policy Q&A CLI agent.

Implements agents.md: single-source answers with section-level citation.
Skills implemented: retrieve_documents, answer_question (see skills.md).

Enforcement rules:
  - Never combine claims from two different documents.
  - No hedging phrases.
  - Every factual claim cites document name + section number.
  - Missing coverage returns the exact refusal template.
"""

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "data" / "policy-documents"

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "i", "my", "me",
    "we", "our", "you", "your", "it", "its", "this", "that", "these", "those",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "up",
    "about", "into", "through", "during", "what", "how", "when", "where",
    "who", "which", "if", "and", "or", "not", "but", "so", "as", "all",
    "any", "same", "per",
}

MIN_SCORE = 2          # minimum keyword hits to consider a section relevant
MAX_SECTIONS = 5       # max sections to include in one answer


# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents():
    """
    Load all three policy files and index by document name and section number.

    Returns:
        dict[str, list[tuple[str, str]]]: Maps doc filename to list of
        (section_id, section_text) tuples.

    Raises:
        FileNotFoundError: If any policy file is missing.
    """
    index = {}
    for filename in POLICY_FILES:
        path = BASE_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {path}")
        text = path.read_text(encoding="utf-8")
        index[filename] = _parse_sections(text)
    return index


def _parse_sections(text):
    """Parse policy text into (section_id, section_text) tuples."""
    section_re = re.compile(r"^(\d+\.?\d*)\s+\S")
    lines = text.splitlines()
    sections = []
    current_id = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("═"):
            continue
        match = section_re.match(stripped)
        if match:
            if current_id is not None:
                sections.append((current_id, " ".join(current_lines)))
            current_id = match.group(1).rstrip(".")
            current_lines = [stripped]
        elif current_id is not None:
            current_lines.append(stripped)

    if current_id is not None:
        sections.append((current_id, " ".join(current_lines)))

    return sections


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------

def answer_question(query, index):
    """
    Search indexed documents for a single-source answer.

    Enforcement:
      - Answers come from exactly one document.
      - Every factual claim includes doc name + section number.
      - Returns REFUSAL_TEMPLATE when coverage is absent.

    Args:
        query (str): Natural-language policy question.
        index (dict): Output of retrieve_documents().

    Returns:
        str: Cited answer or exact refusal template.
    """
    tokens = _tokenise(query)
    if not tokens:
        return REFUSAL_TEMPLATE

    # Score each section in each document independently
    doc_results = {}
    for doc_name, sections in index.items():
        scored = sorted(
            ((score, sec_id, sec_text)
             for sec_id, sec_text in sections
             for score in [_score(tokens, sec_text)]
             if True),
            reverse=True,
        )
        top_score = scored[0][0] if scored else 0
        doc_results[doc_name] = (top_score, scored)

    # Rank documents by their top-section score
    ranked = sorted(doc_results.items(), key=lambda x: x[1][0], reverse=True)
    best_doc, (best_score, best_sections) = ranked[0]

    if best_score < MIN_SCORE:
        return REFUSAL_TEMPLATE

    # Expand to all sub-sections of the same major section for completeness,
    # then also include any other sections from the same doc scoring near the top.
    top_major = best_sections[0][1].split(".")[0]
    seen = set()
    relevant = []
    for score, sec_id, sec_text in best_sections:
        major = sec_id.split(".")[0]
        in_same_group = major == top_major
        near_top = score >= max(MIN_SCORE, best_score - 1)
        if (in_same_group or near_top) and sec_id not in seen:
            relevant.append((sec_id, sec_text))
            seen.add(sec_id)
        if len(relevant) >= MAX_SECTIONS:
            break

    answer_parts = [f"[Section {sid}] {stxt}" for sid, stxt in relevant]
    section_ids = ", ".join(sid for sid, _ in relevant)
    citation = f"Source: {best_doc} — Section{'s' if ',' in section_ids else ''} {section_ids}"

    return "\n\n".join(answer_parts) + "\n\n" + citation


def _tokenise(text):
    return [
        w for w in re.findall(r"[a-z]+", text.lower())
        if w not in STOP_WORDS and len(w) > 2
    ]


def _score(tokens, section_text):
    lower = section_text.lower()
    return sum(1 for tok in tokens if tok in lower)


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("UC-X Policy Q&A")
    print("Type your question and press Enter. Type 'quit' to exit.\n")

    try:
        index = retrieve_documents()
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    total_sections = sum(len(v) for v in index.values())
    print(f"Loaded {total_sections} sections from {len(index)} documents.\n")

    while True:
        try:
            query = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        print()
        print(answer_question(query, index))
        print()


if __name__ == "__main__":
    main()
