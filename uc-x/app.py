"""
UC-X — Ask My Documents
Interactive policy Q&A system that answers questions from three policy documents
with single-source attribution and refusal for uncovered topics.
Implements agents.md enforcement rules and skills.md skill definitions.
"""
import argparse
import re
import sys
import os


# Refusal template — exact wording, no variations
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Hedging phrases that must NEVER appear in answers
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard",
    "usually",
    "it is generally",
    "commonly",
    "in most organisations",
]


def retrieve_documents(document_paths: list) -> list:
    """
    Loads all policy files, parses them into structured sections indexed by
    document name and section number.
    Returns: list of dicts with document_name, section_number, section_title, content.
    """
    index = []

    for path in document_paths:
        if not os.path.exists(path):
            print(f"ERROR: Document not found: {path}", file=sys.stderr)
            sys.exit(1)

        doc_name = os.path.basename(path)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse into sections
        parts = re.split(r'═{3,}\n', content)
        current_title = ""

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check if section header
            header_match = re.match(r'^(\d+)\.\s+(.+)$', part)
            if header_match:
                current_title = part
                continue

            # Parse numbered clauses
            clauses = re.findall(r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)', part, re.DOTALL)
            if clauses:
                for clause_num, clause_body in clauses:
                    body = " ".join(clause_body.strip().split())
                    index.append({
                        "document_name": doc_name,
                        "section_number": clause_num,
                        "section_title": current_title,
                        "content": body
                    })

    if not index:
        print("ERROR: No sections parsed from documents.", file=sys.stderr)
        sys.exit(1)

    return index


def search_index(index: list, keywords: list, question_lower: str) -> list:
    """Search the document index for sections matching the keywords with relevance scoring."""
    matches = []

    # Build acronym expansion map for content matching
    acronym_expansions = {
        "lwp": "leave without pay",
        "lop": "loss of pay",
        "cmc": "city municipal corporation",
        "mfa": "multi-factor authentication",
        "da": "daily allowance",
    }

    for entry in index:
        content_lower = entry["content"].lower()

        # Expand acronyms in content for matching purposes
        expanded_content = content_lower
        for acronym, expansion in acronym_expansions.items():
            if acronym in content_lower:
                expanded_content += " " + expansion

        # Base score: keyword matches
        keyword_score = sum(1 for kw in keywords if kw.lower() in expanded_content)

        if keyword_score == 0:
            continue

        # Bonus: multi-word phrase matches from the question
        phrase_bonus = 0
        # Check for 2-3 word subsequences from keywords
        for i in range(len(keywords) - 1):
            bigram = f"{keywords[i]} {keywords[i+1]}"
            if bigram in expanded_content:
                phrase_bonus += 3
        for i in range(len(keywords) - 2):
            trigram = f"{keywords[i]} {keywords[i+1]} {keywords[i+2]}"
            if trigram in expanded_content:
                phrase_bonus += 5

        # Bonus: keyword density (more keywords relative to content length)
        density_bonus = keyword_score / max(len(content_lower.split()), 1) * 10

        total_score = keyword_score + phrase_bonus + density_bonus
        matches.append((total_score, entry))

    # Sort by relevance score (descending)
    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches]


def answer_question(question: str, index: list) -> str:
    """
    Searches indexed documents for content relevant to the question.
    Returns either a single-source answer with citation or the refusal template.

    Enforcement:
    - Never combine claims from two documents into one answer
    - Never use hedging phrases
    - Use refusal template for uncovered questions
    - Cite source document + section number
    """
    q_lower = question.lower()

    # Extract keywords from question
    stop_words = {"the", "a", "an", "is", "are", "can", "i", "my", "for", "to",
                  "of", "in", "on", "what", "how", "do", "does", "it", "be", "and",
                  "or", "this", "that", "with", "from", "when", "where", "who"}
    words = re.findall(r'\b[a-z]+\b', q_lower)
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    # Add simple stem variants (approves→approv, approval→approv, etc.)
    expanded_keywords = list(keywords)
    for kw in keywords:
        # Add partial stem (first 5+ chars) to catch variants
        if len(kw) > 5:
            expanded_keywords.append(kw[:len(kw)-2])
        if len(kw) > 4:
            expanded_keywords.append(kw[:len(kw)-1])

    # Add common acronym/synonym expansions
    if "leave" in q_lower and "without" in q_lower and "pay" in q_lower:
        expanded_keywords.append("lwp")
    if "work from home" in q_lower or "working from home" in q_lower:
        expanded_keywords.append("wfh")
        expanded_keywords.append("work-from-home")

    keywords = list(set(expanded_keywords))

    if not keywords:
        return REFUSAL_TEMPLATE

    # Search for matching sections
    matches = search_index(index, keywords, q_lower)

    if not matches:
        return REFUSAL_TEMPLATE

    # Group matches by document — only include documents with strong relevance
    doc_answers = {}
    doc_max_score = {}

    # Re-score with same logic as search_index for grouping
    stop_words_set = stop_words
    acronym_expansions = {
        "lwp": "leave without pay",
        "lop": "loss of pay",
        "cmc": "city municipal corporation",
        "mfa": "multi-factor authentication",
        "da": "daily allowance",
    }

    all_scored = []
    for entry in index:
        content_lower = entry["content"].lower()
        expanded_content = content_lower
        for acronym, expansion in acronym_expansions.items():
            if acronym in content_lower:
                expanded_content += " " + expansion

        keyword_score = sum(1 for kw in keywords if kw.lower() in expanded_content)
        if keyword_score == 0:
            continue
        phrase_bonus = 0
        orig_words = re.findall(r'\b[a-z]+\b', q_lower)
        orig_keywords = [w for w in orig_words if w not in stop_words and len(w) > 2]
        for i in range(len(orig_keywords) - 1):
            bigram = f"{orig_keywords[i]} {orig_keywords[i+1]}"
            if bigram in expanded_content:
                phrase_bonus += 3
        for i in range(len(orig_keywords) - 2):
            trigram = f"{orig_keywords[i]} {orig_keywords[i+1]} {orig_keywords[i+2]}"
            if trigram in expanded_content:
                phrase_bonus += 5
        density_bonus = keyword_score / max(len(content_lower.split()), 1) * 10
        total_score = keyword_score + phrase_bonus + density_bonus
        all_scored.append((total_score, entry))

    all_scored.sort(key=lambda x: x[0], reverse=True)

    # If the best match score is very low, the question likely isn't covered
    # A good match should have phrase bonus or multiple keyword hits
    if not all_scored or all_scored[0][0] < 3.0:
        return REFUSAL_TEMPLATE

    # Check if top matches are relevant: at least 2 non-stem keywords must match
    # for a truly relevant hit. Single-word matches on generic terms like "working"
    # are insufficient.
    orig_words = re.findall(r'\b[a-z]+\b', q_lower)
    orig_keywords_check = [w for w in orig_words if w not in stop_words and len(w) > 3]
    if len(orig_keywords_check) >= 2:
        # If question has multiple meaningful keywords, require top match to have
        # at least 2 of them in the content
        top_content = all_scored[0][1]["content"].lower()
        acronym_expansions_check = {"lwp": "leave without pay", "lop": "loss of pay",
                                    "da": "daily allowance", "cmc": "city municipal corporation"}
        expanded_top = top_content
        for acr, exp in acronym_expansions_check.items():
            if acr in top_content:
                expanded_top += " " + exp
        orig_matches = sum(1 for kw in orig_keywords_check if kw in expanded_top)
        if orig_matches < 2:
            return REFUSAL_TEMPLATE

    # Only include documents where top score >= 35% of the best overall score
    if all_scored:
        best_score = all_scored[0][0]
        threshold = best_score * 0.35

        for score, match in all_scored[:15]:
            if score < threshold:
                continue
            doc = match["document_name"]
            if doc not in doc_answers:
                doc_answers[doc] = []
                doc_max_score[doc] = score
            if len(doc_answers[doc]) < 3:
                doc_answers[doc].append(match)

    if not doc_answers:
        return REFUSAL_TEMPLATE

    # Build answer — separate by document (never blend)
    answer_parts = []

    for doc_name, sections in doc_answers.items():
        for section in sections:
            answer_parts.append(
                f"[Source: {doc_name}, Section {section['section_number']}]\n"
                f"  {section['content']}"
            )

    if not answer_parts:
        return REFUSAL_TEMPLATE

    # If only one document matched, give single-source answer
    if len(doc_answers) == 1:
        answer = "\n\n".join(answer_parts)
    else:
        # Multiple documents — present separately with clear attribution
        answer = (
            "[NOTE: Multiple documents address this topic — see each source independently]\n\n"
            + "\n\n".join(answer_parts)
        )

    # Final check: ensure no hedging phrases leaked in
    for phrase in FORBIDDEN_PHRASES:
        if phrase in answer.lower():
            answer = answer.replace(phrase, "[REMOVED — hedging language]")

    return answer


def main():
    # Determine data path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data", "policy-documents")

    document_paths = [
        os.path.join(data_dir, "policy_hr_leave.txt"),
        os.path.join(data_dir, "policy_it_acceptable_use.txt"),
        os.path.join(data_dir, "policy_finance_reimbursement.txt"),
    ]

    # Skill 1: Retrieve and index all documents
    print("Loading policy documents...")
    index = retrieve_documents(document_paths)
    print(f"Indexed {len(index)} sections across 3 documents.\n")

    print("="*60)
    print("ASK MY DOCUMENTS — Policy Q&A System")
    print("="*60)
    print("Type your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.\n")

    # Interactive Q&A loop
    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        # Skill 2: Answer question
        answer = answer_question(question, index)
        print(f"\nA: {answer}\n")
        print("-"*60)


if __name__ == "__main__":
    main()
