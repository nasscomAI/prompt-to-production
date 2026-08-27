"""
UC-X — Ask My Documents

Interactive CLI that answers employee questions from three policy documents.
Single-source answers only — never blends across documents, never hedges,
uses refusal template when answer is not in the documents.

Usage:
    python app.py

Then type questions at the prompt. Type 'quit' or 'exit' to stop.
"""
import os
import re
import sys


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
    "it is reasonable to assume",
]

# Document paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_DIR = os.path.join(SCRIPT_DIR, "..", "data", "policy-documents")
DOCUMENT_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def retrieve_documents() -> dict:
    """
    Load all 3 policy files and index by document name and section/clause.
    Returns dict: {doc_name: {clause_num: clause_text, ...}, ...}
    Also stores '_full_text' key with the raw content.
    """
    index = {}

    for filename in DOCUMENT_FILES:
        filepath = os.path.join(POLICY_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"ERROR: Document not found: {filepath}", file=sys.stderr)
            sys.exit(1)

        doc_index = {"_full_text": content, "_clauses": {}}

        # Parse clauses
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            clause_match = re.match(r"^(\d+\.\d+)\s+(.+)", line)
            if clause_match:
                clause_num = clause_match.group(1)
                clause_text = clause_match.group(2)
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if re.match(r"^(\d+\.\d+)\s+", next_line):
                        break
                    if re.match(r"^(\d+)\.\s+[A-Z][A-Z\s()]+$", next_line):
                        break
                    if next_line.startswith("═"):
                        break
                    if next_line:
                        clause_text += " " + next_line
                    i += 1
                doc_index["_clauses"][clause_num] = clause_text.strip()
            else:
                i += 1

        index[filename] = doc_index

    return index


# Keyword mapping: question keywords → (document, relevant clauses)
QUESTION_RULES = [
    # HR Leave topics
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave", "unused leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["2.6", "2.7"],
        "topic": "annual leave carry-forward"
    },
    {
        "keywords": ["leave without pay", "lwp", "who approves lwp", "approves leave without pay"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["5.1", "5.2", "5.3"],
        "topic": "leave without pay"
    },
    {
        "keywords": ["sick leave", "medical certificate", "sick days"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["3.1", "3.2", "3.3", "3.4"],
        "topic": "sick leave"
    },
    {
        "keywords": ["leave encashment", "encash leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["7.1", "7.2", "7.3"],
        "topic": "leave encashment"
    },
    {
        "keywords": ["annual leave", "leave entitlement", "paid leave", "advance notice"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["2.1", "2.2", "2.3", "2.4", "2.5"],
        "topic": "annual leave"
    },
    {
        "keywords": ["maternity", "paternity"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "maternity/paternity leave"
    },
    # IT topics
    {
        "keywords": ["install", "software", "slack", "application"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["2.3", "2.4"],
        "topic": "software installation"
    },
    {
        "keywords": ["personal phone", "personal device", "byod", "personal mobile"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["3.1", "3.2", "3.3", "3.4"],
        "topic": "personal device (BYOD) use"
    },
    {
        "keywords": ["password", "mfa", "multi-factor", "access control"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "passwords and access control"
    },
    {
        "keywords": ["data handling", "confidential", "restricted data"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["5.1", "5.2", "5.3"],
        "topic": "data handling"
    },
    # Finance topics
    {
        "keywords": ["home office", "wfh equipment", "work from home equipment", "equipment allowance"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "topic": "home office equipment allowance"
    },
    {
        "keywords": ["da", "daily allowance", "meal", "meal receipts", "da and meal"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["2.5", "2.6"],
        "topic": "daily allowance and meal claims"
    },
    {
        "keywords": ["travel", "outstation", "air travel", "hotel"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["2.1", "2.2", "2.3", "2.4"],
        "topic": "travel reimbursement"
    },
    {
        "keywords": ["training", "course", "certification", "professional development"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "training reimbursement"
    },
    {
        "keywords": ["mobile phone reimbursement", "internet reimbursement", "phone bill"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["5.1", "5.2", "5.3"],
        "topic": "mobile/internet reimbursement"
    },
]

# Topics that should trigger refusal (not in any document)
REFUSAL_KEYWORDS = [
    "flexible working culture", "work-life balance", "remote work policy",
    "dress code", "office timings", "promotion criteria", "salary structure",
    "bonus", "appraisal", "performance review"
]


def answer_question(question: str, doc_index: dict) -> str:
    """
    Search indexed documents and return single-source answer + citation
    or refusal template.
    """
    q_lower = question.lower().strip()

    if not q_lower:
        return "Please ask a question."

    # Check for refusal topics first
    for keyword in REFUSAL_KEYWORDS:
        if keyword in q_lower:
            return REFUSAL_TEMPLATE

    # Find matching rule
    best_match = None
    best_score = 0

    for rule in QUESTION_RULES:
        score = 0
        for kw in rule["keywords"]:
            if kw in q_lower:
                score += 1
        if score > best_score:
            best_score = score
            best_match = rule

    if best_match is None or best_score == 0:
        # Try a broader search across all documents
        result = _broad_search(q_lower, doc_index)
        if result:
            return result
        return REFUSAL_TEMPLATE

    # Build answer from single source
    doc_name = best_match["doc"]
    clauses = best_match["clauses"]
    doc_data = doc_index[doc_name]

    answer_parts = []
    answer_parts.append(f"Based on {doc_name} (topic: {best_match['topic']}):\n")

    for clause_num in clauses:
        clause_text = doc_data["_clauses"].get(clause_num, "")
        if clause_text:
            answer_parts.append(f"  Section {clause_num}: {clause_text}")

    answer_parts.append(f"\n[Source: {doc_name}, Sections {', '.join(clauses)}]")

    return "\n".join(answer_parts)


def _broad_search(question: str, doc_index: dict) -> str:
    """
    Fallback: search all clauses for keyword matches.
    Returns answer from a single document only, or None.
    """
    # Extract significant words from question (skip stop words)
    stop_words = {"can", "i", "the", "a", "an", "my", "is", "what", "how",
                  "do", "does", "to", "for", "on", "in", "of", "and", "or",
                  "be", "are", "it", "this", "that", "from", "when", "who"}
    words = [w for w in re.findall(r"\b\w+\b", question) if w not in stop_words and len(w) > 2]

    if not words:
        return None

    # Score each document's clauses
    doc_scores = {}
    doc_matches = {}

    for doc_name, doc_data in doc_index.items():
        score = 0
        matched_clauses = []
        for clause_num, clause_text in doc_data["_clauses"].items():
            clause_lower = clause_text.lower()
            clause_score = sum(1 for w in words if w in clause_lower)
            if clause_score > 0:
                score += clause_score
                matched_clauses.append((clause_num, clause_text, clause_score))

        if score > 0:
            doc_scores[doc_name] = score
            # Sort by relevance
            matched_clauses.sort(key=lambda x: x[2], reverse=True)
            doc_matches[doc_name] = matched_clauses[:3]  # Top 3 clauses

    if not doc_scores:
        return None

    # Pick single best document (no blending)
    best_doc = max(doc_scores, key=doc_scores.get)
    matches = doc_matches[best_doc]

    answer_parts = []
    answer_parts.append(f"Based on {best_doc}:\n")
    clause_nums = []
    for clause_num, clause_text, _ in matches:
        answer_parts.append(f"  Section {clause_num}: {clause_text}")
        clause_nums.append(clause_num)

    answer_parts.append(f"\n[Source: {best_doc}, Sections {', '.join(clause_nums)}]")

    return "\n".join(answer_parts)


def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("=" * 60)
    print("Loaded policies:")
    print("  - policy_hr_leave.txt")
    print("  - policy_it_acceptable_use.txt")
    print("  - policy_finance_reimbursement.txt")
    print()
    print("Type your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()

    # Load documents
    doc_index = retrieve_documents()
    total_clauses = sum(len(d["_clauses"]) for d in doc_index.values())
    print(f"Indexed {total_clauses} clauses across {len(doc_index)} documents.\n")

    # Interactive loop
    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ["quit", "exit", "q"]:
            print("Exiting.")
            break

        if not question:
            continue

        answer = answer_question(question, doc_index)
        print(f"\nA: {answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
