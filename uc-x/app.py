"""
UC-X app.py — Ask My Documents
Interactive CLI for answering employee questions from CMC policy documents.
Implements retrieve_documents and answer_question skills as defined in skills.md.
Follows enforcement rules from agents.md.
See README.md for run command and expected behaviour.
"""
import os
import re
import sys


# ─────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    os.path.join(POLICY_DIR, "policy_hr_leave.txt"),
    os.path.join(POLICY_DIR, "policy_it_acceptable_use.txt"),
    os.path.join(POLICY_DIR, "policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Hedging phrases that must NEVER appear in answers (enforcement rule 2)
BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "normally",
    "it is reasonable to assume",
    "as is standard practice",
    "in most organisations",
    "employees are generally expected",
]

# Minimum relevance score threshold for a clause to be considered a match
RELEVANCE_THRESHOLD = 2

# Maximum number of clauses to include in an answer
MAX_RESULTS = 5


# ─────────────────────────────────────────────────────────
# Skill: retrieve_documents
# ─────────────────────────────────────────────────────────

def retrieve_documents(file_paths: list[str]) -> list[dict]:
    """
    Loads all policy .txt files and returns their content as structured
    sections indexed by document name and section number.
    """
    all_clauses = []

    for path in file_paths:
        if not os.path.isfile(path):
            print(f"ERROR: File not found at {path}.")
            continue

        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        if not raw_text.strip():
            doc_name = os.path.basename(path)
            print(f"WARNING: No structured policy clauses found in {doc_name}.")
            continue

        doc_name = os.path.basename(path)
        clauses = _parse_policy(raw_text, doc_name)

        if not clauses:
            print(f"WARNING: No structured policy clauses found in {doc_name}.")
            continue

        all_clauses.extend(clauses)

    if not all_clauses:
        print("ERROR: No policy documents could be loaded.")
        sys.exit(1)

    return all_clauses


def _parse_policy(raw_text: str, doc_name: str) -> list[dict]:
    """Parse raw policy text into structured clause entries."""
    lines = raw_text.split("\n")
    clauses = []
    current_title = ""

    heading_pattern = re.compile(r"^\d+\.\s+[A-Z]")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect section heading (e.g. "2. ANNUAL LEAVE")
        if heading_pattern.match(line):
            current_title = line

        # Detect clause (e.g. "2.3 Employees must submit...")
        clause_match = clause_pattern.match(line)
        if clause_match:
            section_number = clause_match.group(1)
            # Collect full clause text (may span multiple lines)
            clause_lines = [lines[i].strip()]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if (clause_pattern.match(next_line)
                        or heading_pattern.match(next_line)
                        or next_line.startswith("═")):
                    break
                if next_line:
                    clause_lines.append(next_line)
                else:
                    break
                j += 1

            full_clause = " ".join(clause_lines)
            clause_text = re.sub(r"^\d+\.\d+\s+", "", full_clause)

            clauses.append({
                "doc_name": doc_name,
                "section_number": section_number,
                "section_title": current_title,
                "clause_text": clause_text,
            })

        i += 1

    return clauses


# ─────────────────────────────────────────────────────────
# Skill: answer_question
# ─────────────────────────────────────────────────────────

def answer_question(question: str, clauses: list[dict]) -> str:
    """
    Searches indexed documents for clauses relevant to the user's question.
    Returns a single-source answer with citation OR the refusal template.

    Enforcement rules:
      1. Never blend answers from multiple documents
      2. No hedging phrases
      3. Exact refusal template for out-of-scope questions
      4. Cite document name + section number
    """
    if not question or not question.strip():
        return "ERROR: No question provided."

    # Score each clause for relevance
    scored = _score_clauses(question, clauses)

    # Filter to clauses above threshold
    relevant = [(clause, score) for clause, score in scored if score >= RELEVANCE_THRESHOLD]

    if not relevant:
        return REFUSAL_TEMPLATE

    # Group by document to enforce single-source rule
    doc_groups = {}
    for clause, score in relevant:
        doc = clause["doc_name"]
        if doc not in doc_groups:
            doc_groups[doc] = []
        doc_groups[doc].append((clause, score))

    # Pick the document with the highest total relevance score
    best_doc = max(doc_groups.keys(), key=lambda d: sum(s for _, s in doc_groups[d]))
    best_clauses = doc_groups[best_doc]

    # Sort by score descending, then by section number
    best_clauses.sort(key=lambda x: (-x[1], x[0]["section_number"]))

    # Limit to top N most relevant clauses
    best_clauses = best_clauses[:MAX_RESULTS]

    # Build the answer from the single best document
    answer_lines = [f"Source: {best_doc}\n"]

    for clause, _score in best_clauses:
        answer_lines.append(
            f"  [{best_doc}, Section {clause['section_number']}] "
            f"({clause['section_title']})\n"
            f"  {clause['clause_text']}\n"
        )

    answer = "\n".join(answer_lines)

    # Final hedging check (enforcement rule 2)
    _check_for_hedging(answer)

    return answer


def _score_clauses(question: str, clauses: list[dict]) -> list[tuple[dict, int]]:
    """Score each clause's relevance to the question using keyword matching."""
    question_lower = question.lower()

    # Extract meaningful keywords from the question (ignore stop words)
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall",
        "should", "may", "might", "must", "can", "could", "i", "my", "me",
        "we", "our", "you", "your", "it", "its", "they", "them", "their",
        "this", "that", "these", "those", "what", "which", "who", "whom",
        "when", "where", "how", "if", "or", "and", "but", "not", "no",
        "so", "as", "of", "in", "on", "at", "to", "for", "with", "from",
        "by", "about", "into", "through", "during", "before", "after",
        "above", "below", "up", "down", "out", "off", "over", "under",
        "again", "further", "then", "once", "same", "day",
    }

    # Split on non-alphanumeric, keep meaningful words
    raw_words = re.findall(r"[a-z]+", question_lower)
    keywords = [w for w in raw_words if w not in stop_words and len(w) > 2]

    # Also look for multi-word phrases that are meaningful
    key_phrases = _extract_key_phrases(question_lower)

    scored = []
    for clause in clauses:
        score = 0
        clause_lower = clause["clause_text"].lower()
        title_lower = clause["section_title"].lower()

        # Keyword matching in clause text
        for kw in keywords:
            if kw in clause_lower:
                score += 1
            if kw in title_lower:
                score += 1

        # Phrase matching (higher weight)
        for phrase in key_phrases:
            if phrase in clause_lower:
                score += 3

        scored.append((clause, score))

    return scored


def _extract_key_phrases(question: str) -> list[str]:
    """Extract meaningful multi-word phrases from the question."""
    phrases = []

    # Map common question patterns to policy-relevant search phrases
    phrase_map = {
        "carry forward": ["carry forward"],
        "annual leave": ["annual leave"],
        "sick leave": ["sick leave"],
        "maternity leave": ["maternity leave"],
        "paternity leave": ["paternity leave"],
        "leave without pay": ["leave without pay", "lwp"],
        "personal phone": ["personal device"],
        "personal device": ["personal device"],
        "work from home": ["work-from-home", "work from home", "wfh"],
        "home office": ["home office"],
        "equipment allowance": ["equipment allowance"],
        "install": ["install software", "install"],
        "slack": ["install software", "software"],
        "reimbursement": ["reimbursement", "reimbursable"],
        "meal receipt": ["meal", "receipt"],
        "daily allowance": ["daily allowance", "da "],
        "da and meal": ["da ", "meal"],
        "da ": ["daily allowance"],
        "flexible working": ["flexible working", "flexible"],
        "working culture": ["working culture"],
        "approve": ["approval", "approved"],
        "who approves": ["approval", "requires approval"],
        "leave encash": ["leave encashment", "encash"],
        "compensatory": ["compensatory"],
        "public holiday": ["public holiday"],
        "personal use": ["personal use"],
        "password": ["password"],
        "mfa": ["multi-factor", "mfa"],
        "training": ["training"],
        "certification": ["certification"],
        "travel": ["travel"],
        "hotel": ["hotel", "accommodation"],
        "air travel": ["air travel"],
    }

    for trigger, search_phrases in phrase_map.items():
        if trigger in question:
            phrases.extend(search_phrases)

    return phrases


def _check_for_hedging(answer: str):
    """Check that the answer doesn't contain banned hedging phrases."""
    answer_lower = answer.lower()
    for phrase in BANNED_PHRASES:
        if phrase in answer_lower:
            # This shouldn't happen with our rule-based system, but guard anyway
            print(f"  ⚠️  WARNING: Hedging phrase detected: '{phrase}'")


# ─────────────────────────────────────────────────────────
# Validation — verify answer quality
# ─────────────────────────────────────────────────────────

def validate_answer(answer: str) -> list[str]:
    """Check the answer against enforcement rules. Returns list of warnings."""
    warnings = []

    # Check for hedging phrases
    answer_lower = answer.lower()
    for phrase in BANNED_PHRASES:
        if phrase in answer_lower:
            warnings.append(f"HEDGING: Found banned phrase '{phrase}'.")

    # Check that non-refusal answers have citations
    if REFUSAL_TEMPLATE not in answer and "ERROR:" not in answer:
        if "Section" not in answer:
            warnings.append("MISSING CITATION: Answer does not cite a section number.")

        # Check for cross-document blending
        docs_cited = set()
        for match in re.finditer(r"\[([^,\]]+\.txt)", answer):
            docs_cited.add(match.group(1))
        if len(docs_cited) > 1:
            warnings.append(
                f"CROSS-DOCUMENT BLEND: Answer cites multiple documents: {docs_cited}"
            )

    return warnings


# ─────────────────────────────────────────────────────────
# Interactive CLI
# ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  UC-X — Ask My Documents")
    print("  City Municipal Corporation Policy Q&A")
    print("=" * 60)
    print()

    # Load all policy documents
    print("Loading policy documents...")
    clauses = retrieve_documents(POLICY_FILES)
    print(f"  ✅ Loaded {len(clauses)} clauses from {len(set(c['doc_name'] for c in clauses))} documents.\n")

    # Show available documents
    doc_names = sorted(set(c["doc_name"] for c in clauses))
    print("Available documents:")
    for name in doc_names:
        count = sum(1 for c in clauses if c["doc_name"] == name)
        print(f"  • {name} ({count} clauses)")
    print()
    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.\n")

    # Interactive loop
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        print()

        # Get answer
        answer = answer_question(question, clauses)

        # Validate
        warnings = validate_answer(answer)

        # Display answer
        print(answer)

        # Show validation warnings if any
        if warnings:
            print(f"\n⚠️  Validation warnings:")
            for w in warnings:
                print(f"  - {w}")

        print()


if __name__ == "__main__":
    main()
