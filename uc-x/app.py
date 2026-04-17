"""
UC-X — Ask My Documents
Implements the retrieve_documents and answer_question skills defined in skills.md,
enforcing every rule from agents.md.

Run:
  python app.py
Interactive CLI — type questions, read answers.
"""
import re
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("uc-x")

# ---------------------------------------------------------------------------
# Constants from agents.md enforcement rules
# ---------------------------------------------------------------------------

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Hedging phrases that must NEVER appear in answers (agents.md enforcement)
FORBIDDEN_HEDGES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard",
    "generally expected",
    "standard practice",
]


# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(
    file_paths: list[str],
) -> dict[str, list[dict]]:
    """
    Loads all policy files and indexes content by document name + section number.

    Returns: dict mapping document_name -> list of section dicts, each with:
      - section_number, heading, body
    """
    index: dict[str, list[dict]] = {}

    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)")
    heading_re = re.compile(r"^\d+\.\s+(.+)")
    separator_re = re.compile(r"^[═]+$")

    for fpath in file_paths:
        doc_name = os.path.basename(fpath)

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                raw = f.read()
        except Exception as exc:
            logger.warning(f"Could not read {fpath}: {exc} — skipping.")
            continue

        lines = raw.splitlines()
        sections: list[dict] = []
        current_heading = ""
        clause_buffer: list[str] = []
        current_clause_num = None

        def _flush():
            nonlocal current_clause_num, clause_buffer
            if current_clause_num and clause_buffer:
                body = " ".join(clause_buffer).strip()
                sections.append({
                    "section_number": current_clause_num,
                    "heading": current_heading,
                    "body": body,
                })
            current_clause_num = None
            clause_buffer = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if separator_re.match(line):
                _flush()
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    candidate = lines[i].strip()
                    h_match = heading_re.match(candidate)
                    if h_match and not clause_re.match(candidate):
                        current_heading = h_match.group(1).strip()
                        i += 1
                        while i < len(lines) and (
                            separator_re.match(lines[i].strip())
                            or not lines[i].strip()
                        ):
                            i += 1
                continue

            c_match = clause_re.match(line)
            if c_match:
                _flush()
                current_clause_num = c_match.group(1)
                clause_buffer = [c_match.group(2).strip()]
                i += 1
                continue

            if current_clause_num and line:
                clause_buffer.append(line)

            i += 1

        _flush()
        index[doc_name] = sections
        logger.info(f"Indexed {len(sections)} sections from {doc_name}")

    return index


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------

def answer_question(
    question: str,
    doc_index: dict[str, list[dict]],
) -> str:
    """
    Searches indexed documents for the most relevant section.
    Returns a single-source answer with citation, or the refusal template.

    Enforcement (agents.md):
      • Never combine claims from two different documents.
      • Never use hedging phrases.
      • Cite document name + section number for every factual claim.
      • Use refusal template exactly when question is not covered.
    """
    question_lower = question.lower().strip()

    # Score each section by keyword overlap with the question
    scored: list[tuple[float, str, dict]] = []

    # Extract meaningful words from question (>= 3 chars)
    q_words = set(
        w for w in re.findall(r"[a-z]+", question_lower)
        if len(w) >= 3 and w not in {
            "the", "and", "for", "can", "how", "what", "who", "when",
            "where", "does", "this", "that", "with", "from", "are",
            "was", "were", "been", "have", "has", "had", "will",
            "would", "could", "should", "about", "which", "their",
            "there", "they", "any", "all",
        }
    )

    for doc_name, sections in doc_index.items():
        for section in sections:
            body_lower = section["body"].lower()
            heading_lower = section["heading"].lower()

            # Count matching words
            score = 0
            for w in q_words:
                if w in body_lower:
                    score += 2
                if w in heading_lower:
                    score += 1

            if score > 0:
                scored.append((score, doc_name, section))

    if not scored:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    best_score = scored[0][0]
    best_doc = scored[0][1]
    best_section = scored[0][2]

    # Check for cross-document blending risk:
    # If top results come from different documents with similar scores,
    # answer from the single best only — never blend.
    top_docs = set()
    for score, doc, sec in scored:
        if score >= best_score * 0.7:  # Within 70% of best score
            top_docs.add(doc)

    # If the minimum score is too low, refuse
    if best_score < 2:
        return REFUSAL_TEMPLATE

    # Build answer from the single best document
    answer_parts: list[str] = []
    answer_parts.append(
        f"Per {best_doc} section {best_section['section_number']}:\n"
        f"  {best_section['body']}"
    )

    # Include closely related sections FROM THE SAME DOCUMENT only
    for score, doc, sec in scored[1:5]:
        if doc == best_doc and score >= best_score * 0.6:
            answer_parts.append(
                f"\nAlso per {doc} section {sec['section_number']}:\n"
                f"  {sec['body']}"
            )

    answer = "\n".join(answer_parts)

    # Final enforcement: verify no hedging phrases leaked in
    for hedge in FORBIDDEN_HEDGES:
        if hedge in answer.lower():
            logger.warning(f"Hedging phrase detected and removed: '{hedge}'")
            answer = answer.replace(hedge, "[REDACTED — hedging not permitted]")

    return answer


# ---------------------------------------------------------------------------
# CLI entry-point — Interactive Q&A
# ---------------------------------------------------------------------------

def main():
    # Determine base path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resolved_paths = [os.path.join(script_dir, fp) for fp in POLICY_FILES]

    # Skill 1: retrieve_documents
    print(f"\n{'='*60}")
    print("  UC-X — Ask My Documents")
    print(f"{'='*60}")
    print("  Loading policy documents...")

    doc_index = retrieve_documents(resolved_paths)

    if not doc_index:
        print("ERROR: No documents could be loaded. Exiting.")
        sys.exit(1)

    loaded_docs = list(doc_index.keys())
    total_sections = sum(len(secs) for secs in doc_index.values())
    print(f"  Loaded {len(loaded_docs)} documents, {total_sections} sections total.")
    for doc in loaded_docs:
        print(f"    • {doc} ({len(doc_index[doc])} sections)")

    missing = [
        os.path.basename(fp) for fp in resolved_paths
        if os.path.basename(fp) not in doc_index
    ]
    if missing:
        print(f"\n  ⚠ Could not load: {missing}")
        print(f"    Answers related to these documents may use refusal template.")

    print(f"\n{'='*60}")
    print("  Type your question and press Enter.")
    print("  Type 'quit' or 'exit' to stop.")
    print(f"{'='*60}\n")

    # Interactive loop
    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        # Skill 2: answer_question
        answer = answer_question(question, doc_index)
        print(f"\nA: {answer}\n")


if __name__ == "__main__":
    main()
