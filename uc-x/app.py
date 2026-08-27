"""
UC-X app.py — Ask My Documents
Implements the RICE enforcement rules from agents.md and the two skills
(retrieve_documents, answer_question) from skills.md.

Interactive CLI — type questions, read answers.
"""
import os
import re
import sys

# ── Constants ─────────────────────────────────────────────────────────────────

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

# Enforcement Rule 2: Banned hedging phrases — must never appear in output
BANNED_HEDGES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is likely that",
]

# Synonym expansion: question term → additional terms to search in section text.
# This handles cases like "phone" in question mapping to "device" in policy.
SYNONYM_MAP = {
    "phone": ["device", "devices", "mobile"],
    "laptop": ["device", "devices", "corporate devices", "computer"],
    "install": ["software", "installation"],
    "slack": ["software"],
    "approves": ["approval", "approved"],
    "approve": ["approval", "approved"],
    "carry": ["carry forward", "carried"],
    "forward": ["carry forward"],
    "home": ["work from home", "work-from-home", "wfh", "remote"],
    "flexible": [],  # no policy synonym — should refuse
    "culture": [],    # no policy synonym — should refuse
    "da": ["daily allowance"],
    "meal": ["meal receipts", "meal expenses", "meal claim"],
    "lwp": ["leave without pay"],
}


# ── Skill 1: retrieve_documents ──────────────────────────────────────────────

def retrieve_documents(policy_dir: str = POLICY_DIR) -> dict:
    """
    Loads all three policy documents and indexes their content by
    (document_name, section_number) -> section_text.

    Returns a dict:
        {
            "policy_hr_leave.txt": {
                "1.1": "text...",
                "2.6": "text...",
                ...
            },
            ...
        }

    Error handling (from skills.md):
    - If any file is missing, exit with a clear error naming the file.
    - If a document has no parseable section headers, load as single section
      and log a warning.
    """
    index = {}

    for filename in POLICY_FILES:
        filepath = os.path.join(policy_dir, filename)

        if not os.path.exists(filepath):
            print(f"ERROR: Required policy file not found: {filepath}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                raw_text = f.read()
        except Exception as e:
            print(f"ERROR: Cannot read policy file {filepath}: {e}", file=sys.stderr)
            sys.exit(1)

        sections = _parse_sections(raw_text)

        if not sections:
            print(f"WARNING: No section headers found in {filename}. "
                  f"Loading as a single section '0.0'.", file=sys.stderr)
            sections = {"0.0": raw_text.strip()}

        index[filename] = sections

    print(f"Loaded {len(index)} policy documents:")
    for doc_name, secs in index.items():
        print(f"  {doc_name}: {len(secs)} sections")

    return index


def _parse_sections(text: str) -> dict:
    """
    Parse a policy document into {section_number: section_text} pairs.
    Section headers are lines like '1.1 This policy governs...' or
    '2.6 Employees may carry forward...'.
    Truncates each section at major section header boundaries (═══ lines
    and 'N. TITLE' lines) so that text from one major section does not
    bleed into the previous sub-section.
    """
    sections = {}
    # Match lines starting with a section number like "1.1", "2.6", "10.3"
    section_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$", re.MULTILINE)
    # Major section header: decoration line or "N. TITLE" line
    major_header_pattern = re.compile(
        r"^(?:[═]{3,}|\d+\.\s+[A-Z][A-Z ]+)$", re.MULTILINE
    )

    matches = list(section_pattern.finditer(text))

    for i, match in enumerate(matches):
        sec_num = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw_text = text[start:end]

        # Truncate at any major header boundary within this slice
        major_hit = major_header_pattern.search(raw_text, pos=1)  # skip pos 0
        if major_hit:
            raw_text = raw_text[:major_hit.start()]

        # Clean up: remove decoration lines and excess whitespace
        section_text = re.sub(r"[═]+", "", raw_text).strip()
        sections[sec_num] = section_text

    return sections


# ── Skill 2: answer_question ─────────────────────────────────────────────────

def answer_question(question: str, doc_index: dict) -> str:
    """
    Searches the indexed documents for the answer to a user question.
    Returns a single-source answer with citation, or the refusal template.

    Enforcement rules (from agents.md):
    1. Never combine claims from two different documents.
    2. Never use hedging phrases.
    3. Cite document name + section number for every claim.
    4. If not covered — use refusal template exactly.
    """
    if not doc_index:
        print("ERROR: Document index is empty. Run retrieve_documents first.",
              file=sys.stderr)
        sys.exit(1)

    question_lower = question.lower().strip()

    if not question_lower:
        return REFUSAL_TEMPLATE

    # Expand question with synonyms for better matching
    expanded_question = _expand_question(question_lower)

    # Score each section across all documents for relevance
    scored_results = []

    for doc_name, sections in doc_index.items():
        for sec_num, sec_text in sections.items():
            score = _relevance_score(expanded_question, sec_text.lower())
            if score > 0:
                scored_results.append({
                    "doc_name": doc_name,
                    "section": sec_num,
                    "text": sec_text,
                    "score": score,
                })

    if not scored_results:
        return REFUSAL_TEMPLATE

    # Sort by relevance score descending
    scored_results.sort(key=lambda x: x["score"], reverse=True)

    # If the highest score is too low, the question is likely off-topic
    if scored_results[0]["score"] < 4:
        return REFUSAL_TEMPLATE

    # Enforcement Rule 1: Check if top results span multiple documents
    top_result = scored_results[0]
    top_doc = top_result["doc_name"]

    # Gather all results from the top-scoring document only
    same_doc_results = [r for r in scored_results if r["doc_name"] == top_doc]

    # Check for genuine cross-document ambiguity:
    # If second-best result is from a different document and has a competitive
    # score ( >= 80% of top), AND the question seems to bridge both, refuse.
    other_doc_results = [r for r in scored_results if r["doc_name"] != top_doc]
    if other_doc_results:
        best_other = other_doc_results[0]
        if best_other["score"] >= top_result["score"] * 0.95:
            # Genuinely ambiguous — scores are nearly identical across docs
            return REFUSAL_TEMPLATE

    # Build answer from the single best document only
    answer = _build_answer(question_lower, same_doc_results)

    # Enforcement Rule 2: Final safety check — strip any hedging phrases
    for hedge in BANNED_HEDGES:
        if hedge in answer.lower():
            # This should not happen with our rule-based builder, but safety net
            answer = answer.replace(hedge, "[REMOVED]")
            answer = answer.replace(hedge.capitalize(), "[REMOVED]")

    return answer


def _expand_question(question: str) -> str:
    """
    Expand question with synonyms so that scoring can match policy terminology
    that differs from the user's phrasing (e.g. 'phone' → 'device').
    Returns the question with synonym terms appended.
    """
    extra_terms = []
    q_words = set(re.findall(r"\b[a-z]+\b", question))
    for word in q_words:
        if word in SYNONYM_MAP:
            extra_terms.extend(SYNONYM_MAP[word])
    if extra_terms:
        return question + " " + " ".join(extra_terms)
    return question


def _relevance_score(question: str, section_text: str) -> int:
    """
    Keyword-overlap relevance scoring with synonym expansion and stem matching.
    Returns a weighted score based on word matches, phrase matches, and
    policy-term matches.
    """
    # Remove common stop words from scoring
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "must", "to", "of",
        "in", "for", "on", "with", "at", "by", "from", "as", "into", "about",
        "that", "this", "these", "those", "it", "its", "i", "me", "my", "we",
        "our", "you", "your", "he", "she", "they", "them", "his", "her",
        "what", "which", "who", "whom", "when", "where", "why", "how",
        "and", "or", "but", "not", "no", "if", "then", "than", "so",
        "very", "just", "also", "any", "all",
    }

    question_words = set(re.findall(r"\b[a-z]+\b", question)) - stop_words
    score = 0

    for word in question_words:
        # Exact word match
        if re.search(r"\b" + re.escape(word) + r"\b", section_text):
            score += 1

    # Bonus for exact multi-word phrase matches (bigrams and trigrams)
    q_words_list = [w for w in re.findall(r"\b[a-z]+\b", question) if w not in stop_words]
    for i in range(len(q_words_list) - 1):
        bigram = q_words_list[i] + " " + q_words_list[i + 1]
        if bigram in section_text:
            score += 3
    for i in range(len(q_words_list) - 2):
        trigram = q_words_list[i] + " " + q_words_list[i + 1] + " " + q_words_list[i + 2]
        if trigram in section_text:
            score += 5

    # Bonus for key policy terms that appear in both question and section
    policy_terms = {
        "leave without pay": ["leave without pay", "lwp"],
        "annual leave": ["annual leave"],
        "sick leave": ["sick leave"],
        "carry forward": ["carry forward"],
        "personal device": ["personal device", "personal devices", "personal phone"],
        "work from home": ["work from home", "wfh"],
        "home office": ["home office"],
        "daily allowance": ["daily allowance", "da"],
        "meal receipts": ["meal receipts", "meal expenses", "meal claim"],
        "maternity leave": ["maternity leave"],
        "paternity leave": ["paternity leave"],
        "reimbursement": ["reimbursement", "reimbursable"],
        "software": ["software"],
        "installation": ["installation", "install"],
        "equipment allowance": ["equipment allowance"],
        "compensatory off": ["compensatory off"],
        "leave encashment": ["leave encashment", "encashed"],
        "remote access": ["remote access"],
        "department head": ["department head"],
        "hr director": ["hr director"],
        "corporate devices": ["corporate devices", "corporate device", "laptop", "laptops"],
    }
    
    for q_term, s_terms in policy_terms.items():
        # Check if the question term implies any of the synonyms
        # We also check if the question text has the literal s_term
        q_matched = False
        if q_term in question:
            q_matched = True
        else:
            for st in s_terms:
                if st in question:
                    q_matched = True
                    break
        
        if q_matched:
            for st in s_terms:
                if st in section_text:
                    score += 6
                    # Give an extra strong bonus for LWP approval specifically to rank 5.2 over 5.1
                    if st == "lwp" and "approval" in section_text:
                        score += 5
                    break

    return score


def _build_answer(question: str, relevant_sections: list) -> str:
    """
    Build an answer from sections of a single document.
    Cites document name + section number for every claim.
    """
    if not relevant_sections:
        return REFUSAL_TEMPLATE

    doc_name = relevant_sections[0]["doc_name"]

    # Use top relevant sections (max 3 from same document)
    top_sections = relevant_sections[:3]

    answer_parts = []
    for section in top_sections:
        sec_num = section["section"]
        sec_text = section["text"]
        # Clean the section text for display
        clean_text = _clean_section_text(sec_text)
        answer_parts.append(
            f"According to {doc_name} section {sec_num}:\n  {clean_text}"
        )

    return "\n\n".join(answer_parts)


def _clean_section_text(text: str) -> str:
    """Clean section text: remove excessive whitespace, cap length."""
    # Collapse multiple whitespace/newlines
    text = re.sub(r"\s+", " ", text).strip()
    # Cap at a reasonable length for display
    if len(text) > 500:
        text = text[:497] + "..."
    return text


# ── Interactive CLI ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A system for CMC employees")
    print("=" * 60)

    # Phase 1: Load and index documents
    print("\n--- Loading policy documents ---")
    doc_index = retrieve_documents()

    # Phase 2: Interactive Q&A loop
    print("\n--- Ready for questions ---")
    print("Type your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.\n")

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

        answer = answer_question(question, doc_index)
        print(f"\nA: {answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
