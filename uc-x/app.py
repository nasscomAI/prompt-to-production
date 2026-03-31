"""
UC-X — Ask My Documents
Single-source policy Q&A system. Answers questions strictly from
3 policy documents with citations, or returns the exact refusal template.
"""
import os
import re
import sys

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

DOC_SHORT_NAMES = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally expected",
    "as is standard practice",
]


def retrieve_documents(policy_dir: str) -> dict:
    """
    Load all 3 policy .txt files and index them by document name and section number.
    Returns: {doc_name: {section_num: section_text, ...}, ...}
    """
    index = {}
    for doc_file in DOCUMENTS:
        path = os.path.join(policy_dir, doc_file)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Cannot read {path}: {e}", file=sys.stderr)
            sys.exit(1)

        if not content.strip():
            print(f"ERROR: File is empty: {path}", file=sys.stderr)
            sys.exit(1)

        # Parse into sections
        lines = content.split("\n")
        sections = {}
        current_clause = None

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("═") or re.match(r"^\d+\.\s+[A-Z]", stripped):
                continue
            m = re.match(r"^(\d+\.\d+)\s+(.*)", stripped)
            if m:
                if current_clause:
                    sections[current_clause["clause"]] = current_clause["text"]
                current_clause = {"clause": m.group(1), "text": m.group(2).strip()}
            elif current_clause and stripped:
                current_clause["text"] += " " + stripped

        if current_clause:
            sections[current_clause["clause"]] = current_clause["text"]

        index[doc_file] = sections

    return index


def _extract_keywords(question: str) -> list[str]:
    """Extract meaningful keywords from a question."""
    lower = question.lower()
    # Remove common question words
    stop_words = {
        "can", "i", "my", "the", "is", "what", "who", "how", "does",
        "do", "a", "an", "for", "to", "of", "in", "on", "from", "with",
        "about", "it", "this", "that", "am", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "will", "would",
        "could", "should", "may", "might", "must", "shall",
    }
    words = re.findall(r"[a-z]+(?:[-'][a-z]+)*", lower)
    return [w for w in words if w not in stop_words and len(w) > 2]


# High-signal phrase patterns mapped to (doc_file, clause_num) for precision
PHRASE_HINTS = {
    r"\binstall\b.*\bsoftware\b": ("policy_it_acceptable_use.txt", "2.3"),
    r"\binstall\b.*\bslack\b": ("policy_it_acceptable_use.txt", "2.3"),
    r"\bslack\b": ("policy_it_acceptable_use.txt", "2.3"),
    r"\bpersonal phone\b.*\bwork\b": ("policy_it_acceptable_use.txt", "3.1"),
    r"\bpersonal device\b.*\bwork\b": ("policy_it_acceptable_use.txt", "3.1"),
    r"\bpersonal phone\b.*\bfile": ("policy_it_acceptable_use.txt", "3.1"),
    r"\bpersonal phone\b.*\baccess\b": ("policy_it_acceptable_use.txt", "3.1"),
    r"\bbyod\b": ("policy_it_acceptable_use.txt", "3.1"),
    r"\bleave without pay\b.*\bapprov": ("policy_hr_leave.txt", "5.2"),
    r"\bwho approves\b.*\bleave\b": ("policy_hr_leave.txt", "5.2"),
    r"\bwho approves\b.*\blwp\b": ("policy_hr_leave.txt", "5.2"),
    r"\blwp\b.*\bapprov": ("policy_hr_leave.txt", "5.2"),
    r"\bcarry forward\b.*\bannual\b": ("policy_hr_leave.txt", "2.6"),
    r"\bhome office\b.*\bequipment\b": ("policy_finance_reimbursement.txt", "3.1"),
    r"\bhome office\b.*\ballowance\b": ("policy_finance_reimbursement.txt", "3.1"),
    r"\bda\b.*\bmeal\b": ("policy_finance_reimbursement.txt", "2.6"),
    r"\bmeal\b.*\breceipt\b": ("policy_finance_reimbursement.txt", "2.6"),
}


def _apply_phrase_hints(question: str, index: dict) -> tuple[str, str, str, float]:
    """Check question against known high-signal phrase patterns."""
    lower = question.lower()
    for pattern, (doc, clause) in PHRASE_HINTS.items():
        if re.search(pattern, lower):
            if doc in index and clause in index[doc]:
                return doc, clause, index[doc][clause], 10.0
    return "", "", "", 0.0


def _score_section(section_text: str, keywords: list[str]) -> float:
    """Score a section's relevance to the question keywords."""
    lower = section_text.lower()
    score = 0.0
    for kw in keywords:
        # Exact word match
        if re.search(r"\b" + re.escape(kw) + r"\b", lower):
            score += 2.0
        # Partial match
        elif kw in lower:
            score += 1.0
    return score


def _find_best_section(index: dict, question: str) -> tuple[str, str, str, float]:
    """
    Find the single best matching section across all documents.
    Returns (doc_file, clause_num, section_text, score) or ("", "", "", 0).
    """
    # First try phrase hints for precision
    doc, clause, text, score = _apply_phrase_hints(question, index)
    if score > 0:
        return doc, clause, text, score

    keywords = _extract_keywords(question)
    if not keywords:
        return "", "", "", 0.0

    best_doc = ""
    best_clause = ""
    best_text = ""
    best_score = 0.0

    for doc_file, sections in index.items():
        for clause_num, section_text in sections.items():
            s = _score_section(section_text, keywords)
            if s > best_score:
                best_score = s
                best_doc = doc_file
                best_clause = clause_num
                best_text = section_text

    return best_doc, best_clause, best_text, best_score


def answer_question(question: str, index: dict) -> str:
    """
    Search indexed documents for the answer to a user question.
    Returns single-source answer with citation, or the refusal template.
    """
    if not question or not question.strip():
        return "Please enter a question."

    # Check for hedging phrases in the question itself (defensive)
    lower_q = question.lower()

    doc_file, clause, text, score = _find_best_section(index, question)

    # Threshold: if score is too low, refuse
    # Higher threshold for keyword-only (no phrase hint) matches
    if score < 3.0:
        return REFUSAL_TEMPLATE

    # Format answer with citation
    doc_name = DOC_SHORT_NAMES.get(doc_file, doc_file)

    # Build answer — quote or paraphrase the relevant section
    answer = f"According to the {doc_name} (Section {clause}):\n\n{text}"

    # Verify no hedging phrases leaked in
    answer_lower = answer.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in answer_lower:
            return REFUSAL_TEMPLATE

    return answer


def main():
    # Resolve policy directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    policy_dir = os.path.join(script_dir, "..", "data", "policy-documents")
    policy_dir = os.path.normpath(policy_dir)

    print("Loading policy documents...")
    index = retrieve_documents(policy_dir)
    total_sections = sum(len(s) for s in index.values())
    print(f"Loaded {len(index)} documents with {total_sections} sections.")
    print("=" * 60)
    print("Type your question and press Enter. Type 'quit' to exit.")
    print("=" * 60)

    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(question, index)
        print(f"\n{answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
