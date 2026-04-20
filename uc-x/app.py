"""
UC-X app.py -- Ask My Documents
Implementation based on RICE framework (agents.md) and skills definition (skills.md).

Interactive CLI that answers employee questions from 3 policy documents.
Core failure modes guarded against: cross-document blending, hedged hallucination,
condition dropping.
"""
import os
import re
import sys


# -----------------------------------------------------------------------
#  CONFIGURATION -- Derived from agents.md enforcement rules
# -----------------------------------------------------------------------

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

# Hedging phrases that must NEVER appear in answers (agents.md enforcement rule 2)
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "in most organisations",
    "in most organizations",
]


# -----------------------------------------------------------------------
#  SKILL 1: retrieve_documents
#  Loads all 3 policy files, indexes by document name and section number.
# -----------------------------------------------------------------------

def retrieve_documents(policy_dir: str) -> list:
    """
    Parse all policy documents into indexed sections.

    Args:
        policy_dir: Directory containing the 3 policy files.

    Returns:
        List of section dicts, each with:
          - 'document': filename
          - 'clause': section number string (e.g., '3.1')
          - 'heading': parent section heading
          - 'text': full section text

    Raises:
        FileNotFoundError: If any expected policy document is missing.
    """
    missing = [f for f in POLICY_FILES if not os.path.exists(os.path.join(policy_dir, f))]
    if missing:
        raise FileNotFoundError(
            f"Missing policy document(s): {', '.join(missing)}"
        )

    all_sections = []

    heading_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)$")

    for filename in POLICY_FILES:
        filepath = os.path.join(policy_dir, filename)
        with open(filepath, mode="r", encoding="utf-8") as f:
            content = f.read()

        current_heading = ""
        lines = content.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            heading_match = heading_pattern.match(line)
            if heading_match:
                current_heading = heading_match.group(2).strip()
                i += 1
                continue

            clause_match = clause_pattern.match(line)
            if clause_match:
                clause_num = clause_match.group(1)
                clause_text = clause_match.group(2).strip()

                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    stripped = next_line.strip()
                    if (not stripped
                            or stripped.startswith("=")
                            or clause_pattern.match(stripped)
                            or heading_pattern.match(stripped)):
                        break
                    clause_text += " " + stripped
                    i += 1

                all_sections.append({
                    "document": filename,
                    "clause": clause_num,
                    "heading": current_heading,
                    "text": clause_text,
                })
                continue

            i += 1

    return all_sections


# -----------------------------------------------------------------------
#  SKILL 2: answer_question
#  Searches indexed documents, returns single-source answer + citation
#  OR refusal template.
# -----------------------------------------------------------------------

def answer_question(question: str, sections: list) -> str:
    """
    Find the most relevant section for a question and return a cited answer.

    Uses keyword matching to find relevant sections, then applies
    single-source attribution and hedging checks.

    Args:
        question: User's question string.
        sections: Indexed sections from retrieve_documents.

    Returns:
        Answer string with citation, or the refusal template.
    """
    question_lower = question.lower()

    # Extract keywords from the question (simple approach)
    # Remove common stop words
    stop_words = {
        "can", "i", "the", "a", "an", "is", "are", "do", "does", "what",
        "how", "who", "when", "where", "my", "for", "to", "of", "in", "on",
        "and", "or", "if", "it", "be", "am", "was", "were"
    }
    words = re.findall(r"[a-z]+", question_lower)
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    # Score each section by keyword overlap
    scored = []
    for section in sections:
        section_text_lower = section["text"].lower()
        section_heading_lower = section["heading"].lower()
        score = 0

        for kw in keywords:
            if kw in section_text_lower:
                score += 2
            if kw in section_heading_lower:
                score += 1

        if score > 0:
            scored.append((score, section))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        return REFUSAL_TEMPLATE

    # Get top match
    best_score, best_section = scored[0]

    if best_score < 2:
        return REFUSAL_TEMPLATE

    # Check if top matches span multiple documents (blending risk)
    top_docs = set()
    threshold = best_score * 0.7  # within 70% of top score
    for score, section in scored:
        if score >= threshold:
            top_docs.add(section["document"])

    # Build answer from single source
    doc_name = best_section["document"]
    clause = best_section["clause"]
    text = best_section["text"]

    # If multiple documents are equally relevant, note the ambiguity
    if len(top_docs) > 1:
        # Still answer from the best single source, but note it
        answer = (
            f"Based on {doc_name}, Section {clause} "
            f"({best_section['heading']}):\n"
            f"\n"
            f"  {text}\n"
            f"\n"
            f"  [Source: {doc_name}, Section {clause}]\n"
            f"\n"
            f"  Note: Related sections may exist in other policy documents. "
            f"This answer is sourced from {doc_name} only, per single-source "
            f"attribution rules."
        )
    else:
        answer = (
            f"Based on {doc_name}, Section {clause} "
            f"({best_section['heading']}):\n"
            f"\n"
            f"  {text}\n"
            f"\n"
            f"  [Source: {doc_name}, Section {clause}]"
        )

    return answer


# -----------------------------------------------------------------------
#  VERIFICATION -- Post-answer checks from agents.md enforcement
# -----------------------------------------------------------------------

def verify_answer(answer: str) -> list:
    """
    Check the generated answer for enforcement violations.

    Returns:
        List of warning strings. Empty = all checks passed.
    """
    issues = []
    answer_lower = answer.lower()

    # CHECK 1: No hedging phrases
    for phrase in HEDGING_PHRASES:
        if phrase in answer_lower:
            issues.append(
                f"[HEDGING DETECTED] Prohibited phrase found: '{phrase}'"
            )

    # CHECK 2: Citation present (unless it's a refusal)
    if answer != REFUSAL_TEMPLATE:
        if "[Source:" not in answer and "[source:" not in answer_lower:
            issues.append(
                "[MISSING CITATION] Answer does not contain a source citation."
            )

    # CHECK 3: Check for multi-document blending
    doc_mentions = []
    for pf in POLICY_FILES:
        if pf in answer:
            doc_mentions.append(pf)

    # In a non-refusal answer, only 1 document should be cited as source
    if answer != REFUSAL_TEMPLATE and len(doc_mentions) > 1:
        # Check if more than one is cited as [Source:]
        source_citations = re.findall(r"\[Source:\s*([^\]]+)\]", answer)
        cited_docs = set()
        for citation in source_citations:
            for pf in POLICY_FILES:
                if pf in citation:
                    cited_docs.add(pf)
        if len(cited_docs) > 1:
            issues.append(
                f"[CROSS-DOC BLENDING] Answer cites multiple documents as sources: "
                f"{', '.join(cited_docs)}"
            )

    return issues


# -----------------------------------------------------------------------
#  MAIN -- Interactive CLI matching README run command
# -----------------------------------------------------------------------

def main():
    print("=" * 60)
    print("UC-X -- Ask My Documents")
    print("Policy Q&A Agent (single-source attribution)")
    print("=" * 60)
    print()

    # -- Step 1: Load documents --
    policy_dir = os.path.normpath(POLICY_DIR)
    print(f"[retrieve_documents] Loading from: {policy_dir}")

    try:
        sections = retrieve_documents(policy_dir)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    doc_counts = {}
    for s in sections:
        doc_counts[s["document"]] = doc_counts.get(s["document"], 0) + 1

    print(f"[retrieve_documents] Loaded {len(sections)} sections from {len(doc_counts)} documents:")
    for doc, count in doc_counts.items():
        print(f"  - {doc}: {count} sections")
    print()
    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.")
    print("-" * 60)

    # -- Step 2: Interactive Q&A loop --
    while True:
        print()
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

        # Get answer
        answer = answer_question(question, sections)

        # Verify answer
        issues = verify_answer(answer)

        if issues:
            print(f"\n[ENFORCEMENT] {len(issues)} issue(s):")
            for issue in issues:
                print(f"  [!] {issue}")

        print(f"\nA: {answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
