"""
UC-X: Policy Q&A agent for CMC internal policy documents.
Interactive CLI — type questions, read answers.

Enforcement rules implemented here:
  1. Never combine claims from two different documents into a single answer.
  2. Never use hedging phrases — prohibited list enforced at output time.
  3. If question not in documents — use the exact refusal template, no variation.
  4. Cite source document name + section number for every factual claim.
"""
import re
import sys
from pathlib import Path

POLICY_FILES = [
    ("policy_hr_leave.txt",           "HR Leave Policy (HR-POL-001)"),
    ("policy_it_acceptable_use.txt",  "IT Acceptable Use Policy (IT-POL-003)"),
    ("policy_finance_reimbursement.txt", "Finance Reimbursement Policy (FIN-POL-007)"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally",
    "usually",
    "may imply",
    "could be interpreted",
]

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "i", "my", "me", "we",
    "our", "you", "your", "it", "its", "this", "that", "what", "when",
    "where", "which", "who", "how", "why", "and", "or", "but", "if",
    "in", "on", "at", "to", "for", "of", "with", "from", "by", "about",
    "as", "into", "through", "during", "before", "after", "between",
    "use", "get", "see", "let", "put", "set",
}

DATA_DIR = Path(__file__).parent.parent / "data" / "policy-documents"

# Minimum keyword score required to return an answer (not refusal)
MIN_SCORE_THRESHOLD = 2
# If second-best doc score is within this fraction of best, refuse (cross-doc risk)
CROSS_DOC_RATIO = 0.6

# Expand abbreviations in document text so keyword search can find them
ABBREVIATIONS = {
    r"\bLWP\b": "leave without pay",
    r"\bDA\b": "daily allowance",
    r"\bWFH\b": "work from home",
    r"\bMFA\b": "multi-factor authentication",
    r"\bLOP\b": "loss of pay",
    r"\bBYOD\b": "personal device",
}


# ---------------------------------------------------------------------------
# Skill 1: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(data_dir: Path) -> dict:
    """Load all 3 policy files and index by document name and section number."""
    index = {}

    for filename, doc_label in POLICY_FILES:
        file_path = data_dir / filename
        if not file_path.exists():
            print(f"[WARNING] Policy file not found: {file_path}", file=sys.stderr)
            continue

        raw = file_path.read_text(encoding="utf-8")
        sections = _parse_sections(raw)
        index[filename] = {
            "label": doc_label,
            "sections": sections,
        }
        print(f"[retrieve_documents] Loaded {filename}: {len(sections)} clauses")

    if not index:
        raise RuntimeError("No policy documents could be loaded.")

    return index


def _parse_sections(text: str) -> list[dict]:
    """Parse policy text into numbered clause dicts, with abbreviation expansion."""
    for pattern, expansion in ABBREVIATIONS.items():
        text = re.sub(pattern, expansion, text)
    sections = []
    current_clause = None
    current_lines = []
    clause_pattern = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\b")
    section_heading = re.compile(r"^\d+\.\s+[A-Z]")
    border_line = re.compile(r"^[═─=\-]{4,}$")

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if border_line.match(stripped) or section_heading.match(stripped):
            if current_clause is not None:
                sections.append({"clause": current_clause, "text": " ".join(current_lines).strip()})
                current_clause = None
                current_lines = []
            continue

        match = clause_pattern.match(stripped)
        if match:
            if current_clause is not None:
                sections.append({"clause": current_clause, "text": " ".join(current_lines).strip()})
            current_clause = match.group(1)
            current_lines = [stripped]
        else:
            if current_clause is not None:
                current_lines.append(stripped)

    if current_clause is not None:
        sections.append({"clause": current_clause, "text": " ".join(current_lines).strip()})

    return sections


# ---------------------------------------------------------------------------
# Skill 2: answer_question
# ---------------------------------------------------------------------------

def _extract_keywords(question: str) -> list[str]:
    """Extract meaningful search keywords, preserving short uppercase terms (e.g. DA)."""
    tokens = re.findall(r"\b\w+\b", question)
    keywords = []
    for tok in tokens:
        if len(tok) == 2 and tok.upper() == tok:
            keywords.append(tok.lower())
        elif len(tok) >= 3 and tok.lower() not in STOP_WORDS:
            keywords.append(tok.lower())
    return keywords


def _score_section(section_text: str, keywords: list[str]) -> int:
    """Count distinct keywords matching as whole words; stem fallback for long words."""
    count = 0
    for kw in keywords:
        if re.search(r"\b" + re.escape(kw) + r"\b", section_text, re.IGNORECASE):
            count += 1
        elif len(kw) > 5 and re.search(r"\b" + re.escape(kw[:5]), section_text, re.IGNORECASE):
            count += 1
    return count


def answer_question(question: str, index: dict) -> str:
    """Search indexed documents; return single-source cited answer or refusal."""
    keywords = _extract_keywords(question)
    if not keywords:
        return REFUSAL_TEMPLATE

    # Score every section in every document
    doc_totals = {}
    doc_top_sections = {}

    for filename, doc_data in index.items():
        scored = []
        for section in doc_data["sections"]:
            score = _score_section(section["text"], keywords)
            if score > 0:
                scored.append((score, section))
        if scored:
            scored.sort(key=lambda x: -x[0])
            doc_totals[filename] = sum(s for s, _ in scored)
            doc_top_sections[filename] = scored

    # No matches at all → refusal
    if not doc_totals:
        return REFUSAL_TEMPLATE

    sorted_docs = sorted(doc_totals.items(), key=lambda x: -x[1])
    best_fn, best_score = sorted_docs[0]

    # Below minimum relevance → refusal
    if best_score < MIN_SCORE_THRESHOLD:
        return REFUSAL_TEMPLATE

    # Cross-document blending risk check
    if len(sorted_docs) > 1:
        second_score = sorted_docs[1][1]
        if second_score / best_score >= CROSS_DOC_RATIO:
            # Two docs are roughly equally relevant — single-source or refusal
            # Use the top-scoring individual section across both docs to decide
            all_sections = []
            for fn, sections in doc_top_sections.items():
                for score, section in sections:
                    all_sections.append((score, fn, section))
            all_sections.sort(key=lambda x: -x[0])

            top_score = all_sections[0][0]
            top_doc_fns = {fn for s, fn, _ in all_sections if s == top_score}

            if len(top_doc_fns) == 1:
                # One document has the single highest-scoring clause → safe to cite it alone
                best_fn = all_sections[0][1]
            else:
                # Tied across documents — genuine ambiguity, refuse
                return REFUSAL_TEMPLATE

    doc_data = index[best_fn]
    top_matches = doc_top_sections[best_fn][:3]

    answer_lines = []
    for score, section in top_matches:
        citation = f"[{doc_data['label']} — Section {section['clause']}]"
        answer_lines.append(f"{citation}\n{section['text']}")

    answer = "\n\n".join(answer_lines)

    # Enforcement: strip any hedging phrases that slipped through
    for phrase in HEDGING_PHRASES:
        if phrase.lower() in answer.lower():
            answer = re.sub(re.escape(phrase), "[REDACTED: hedging]", answer, flags=re.IGNORECASE)

    return answer


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("CMC Policy Q&A Agent")
    print("Sources: HR Leave | IT Acceptable Use | Finance Reimbursement")
    print("Type your question and press Enter. Type 'exit' to quit.")
    print("=" * 60)

    print("\n[retrieve_documents] Loading policy documents...")
    try:
        index = retrieve_documents(DATA_DIR)
    except RuntimeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"[retrieve_documents] Ready. {len(index)} document(s) indexed.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[exit]")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit", "q"):
            break

        answer = answer_question(question, index)
        print(f"\nAnswer:\n{answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
