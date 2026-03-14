"""
UC-X — Ask My Documents
Interactive CLI that answers employee questions strictly from the three CMC policy documents.

Skills implemented (per skills.md):
  - retrieve_documents : loads all 3 policy files, parses into section-indexed corpus
  - answer_question    : single-source search → cited answer OR verbatim refusal template

Enforcement rules (per agents.md):
  1. Never combine claims from two different documents into one answer.
  2. Never use hedging language ("typically", "generally", "while not explicitly covered", etc.).
  3. Questions not in any document → exact refusal template, no variation.
  4. Every factual answer cites document name + section number.

Run:
    python app.py
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# ---------------------------------------------------------------------------
# Refusal template — verbatim as specified in README and agents.md
# ---------------------------------------------------------------------------
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Banned hedging phrases (enforcement rule 2)
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally",
    "may be",
    "might be",
    "could be",
]

# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------
def retrieve_documents(policy_dir: str) -> dict:
    """
    Loads all three policy text files and parses them into a section-indexed corpus.

    Returns:
        corpus: {
            "policy_hr_leave.txt": {
                "1.1": "This policy governs ...",
                "2.6": "Employees may carry forward ...",
                ...
            },
            "policy_it_acceptable_use.txt": { ... },
            "policy_finance_reimbursement.txt": { ... },
        }

    Raises:
        FileNotFoundError: if any required policy file is missing.
        ValueError:        if a file is empty or cannot be parsed.
    """
    corpus = {}

    for filename in POLICY_FILES:
        filepath = os.path.join(policy_dir, filename)

        if not os.path.isfile(filepath):
            raise FileNotFoundError(
                f"Required policy file not found: {filepath}\n"
                "Ensure data/policy-documents/ contains all three policy files."
            )

        with open(filepath, "r", encoding="utf-8") as fh:
            raw = fh.read()

        if not raw.strip():
            raise ValueError(f"Policy file is empty: {filepath}")

        sections = _parse_sections(raw, filename)
        if not sections:
            raise ValueError(
                f"Could not parse any sections from: {filename}\n"
                "Expected numbered sections like '2.6 ...'."
            )

        corpus[filename] = sections

    return corpus


def _parse_sections(text: str, filename: str) -> dict:
    """
    Parses a policy document into a dict keyed by section number string.
    Section numbers follow the pattern N.N (e.g. 2.6, 3.1).

    Strategy: split on lines that start with a section number, collect
    all text until the next section header as the section body.
    """
    # Match lines beginning with a section number like "2.6 ..."
    section_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)", re.MULTILINE)

    sections = {}
    lines = text.splitlines()

    current_num = None
    current_lines = []

    for line in lines:
        m = section_pattern.match(line.strip())
        if m:
            # Save the previous section if any
            if current_num is not None:
                sections[current_num] = " ".join(current_lines).strip()
            current_num = m.group(1)
            current_lines = [m.group(2).strip()]
        else:
            if current_num is not None:
                stripped = line.strip()
                if stripped and not set(stripped) <= set("═ "):
                    current_lines.append(stripped)

    # Save the last section
    if current_num is not None:
        sections[current_num] = " ".join(current_lines).strip()

    return sections


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------
def answer_question(question: str, corpus: dict) -> str:
    """
    Searches the indexed corpus for a single-source, single-section answer.

    Returns:
        - The answer text with citation "[doc_name §section_number]", OR
        - The verbatim REFUSAL_TEMPLATE if no single-source answer exists.

    Raises:
        ValueError: if corpus is empty/None, or question is blank.
    """
    if not corpus:
        raise ValueError("Corpus is empty. Call retrieve_documents() first.")

    question = question.strip()
    if not question:
        return "Please enter a valid question."

    q_lower = question.lower()

    # Score each section in each document for relevance to the question
    hits = []  # list of (score, doc_name, section_num, section_text)

    question_keywords = _extract_keywords(q_lower)

    for doc_name, sections in corpus.items():
        for sec_num, sec_text in sections.items():
            score = _score_section(question_keywords, sec_text.lower())
            if score > 0:
                hits.append((score, doc_name, sec_num, sec_text))

    if not hits:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    hits.sort(key=lambda x: x[0], reverse=True)

    # Single-source enforcement: collect only hits from the top-scoring document
    top_score = hits[0][0]
    # Accept candidates within 60% of the top score
    threshold = top_score * 0.60
    strong_hits = [h for h in hits if h[0] >= threshold]

    # Determine which documents are represented in the strong hits
    docs_in_hits = {h[1] for h in strong_hits}

    if len(docs_in_hits) > 1:
        # Multi-document ambiguity — must refuse (enforcement rule 1)
        return REFUSAL_TEMPLATE

    # All strong hits are from one document — pick the top section
    best = hits[0]
    _, doc_name, sec_num, sec_text = best

    answer = f"{sec_text}\n\n[Source: {doc_name} §{sec_num}]"
    return answer


# Known abbreviations present in policy documents → expand so keyword scoring can hit them
_ABBREV_EXPANSIONS = {
    "lwp": "leave without pay",
    "lop": "loss of pay",
    "mfa": "multi-factor authentication",
    "da":  "daily allowance",
    "byod": "personal device",
    "cmc": "city municipal corporation",
}


def _expand_abbreviations(text: str) -> str:
    """Replace known abbreviations in text with their expanded forms."""
    for abbr, expansion in _ABBREV_EXPANSIONS.items():
        # Match whole-word abbreviations (case-insensitive already since text is lower)
        text = re.sub(rf"\b{re.escape(abbr)}\b", expansion, text)
    return text


def _extract_keywords(q_lower: str) -> list:
    """Return meaningful words from the question for keyword matching."""
    # Remove common stop words — intentionally keep domain words like 'without', 'pay'
    stop = {
        "can", "i", "my", "the", "a", "an", "is", "are", "what", "how",
        "when", "who", "which", "on", "in", "at", "for", "to", "of", "do",
        "does", "it", "be", "will", "was", "and", "or", "from", "with",
        "about", "use", "used", "their", "this", "that", "any",
    }
    words = re.findall(r"[a-z]+", q_lower)
    return [w for w in words if w not in stop and len(w) > 2]


def _score_section(keywords: list, section_lower: str) -> int:
    """
    Score a section by counting keyword matches.
    Uses prefix matching (first 5 chars) to handle morphological variants:
      - "approves" matches "approval"  (appro)
      - "install" matches "installation" (insta)
      - "carry" matches "carry-forward" (carry)
    An exact match scores 2; a prefix match scores 1.
    """
    score = 0
    expanded = _expand_abbreviations(section_lower)
    for kw in keywords:
        if kw in expanded:
            score += 2          # exact match — higher confidence
        elif len(kw) >= 5 and kw[:5] in expanded:
            score += 1          # prefix/stem match
    return score


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------
def main():
    print("=" * 65)
    print("  UC-X — Ask My Documents")
    print("  CMC Policy Q&A (HR · IT · Finance)")
    print("=" * 65)
    print("Loading policy documents...", end=" ", flush=True)

    try:
        corpus = retrieve_documents(POLICY_DIR)
        total_sections = sum(len(s) for s in corpus.values())
        print(f"OK  ({len(corpus)} documents, {total_sections} sections indexed)")
    except (FileNotFoundError, ValueError) as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)

    print("\nType your question and press Enter.  Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break

        try:
            result = answer_question(question, corpus)
        except ValueError as exc:
            print(f"Error: {exc}\n")
            continue

        print()
        print("-" * 65)
        print(result)
        print("-" * 65)
        print()


if __name__ == "__main__":
    main()
