"""
UC-X app.py — Ask My Documents
Interactive CLI that answers questions from CMC policy documents.

Skills implemented:
  - retrieve_documents: loads all 3 policy files, indexes by (doc_name, section_number)
  - answer_question: single-source answer + citation OR exact refusal template

Agent enforcement (from agents.md):
  1. Never combine claims from two different documents into a single answer.
  2. Never use hedging phrases.
  3. If question is not covered — use refusal template exactly, no variations.
  4. Cite source document name + section number for every factual claim.

Run: python app.py
"""

import os
import re

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

POLICY_FILES = {
    "policy_hr_leave.txt": os.path.join(
        os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt"
    ),
    "policy_it_acceptable_use.txt": os.path.join(
        os.path.dirname(__file__), "..", "data", "policy-documents", "policy_it_acceptable_use.txt"
    ),
    "policy_finance_reimbursement.txt": os.path.join(
        os.path.dirname(__file__), "..", "data", "policy-documents", "policy_finance_reimbursement.txt"
    ),
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact HR team for guidance."
)

# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(policy_files: dict = None) -> dict:
    """
    Loads all 3 policy files and indexes them by (document_name, section_number)
    to the raw text content of that section.

    Args:
        policy_files: Optional dict mapping filename -> filepath. Defaults to POLICY_FILES.

    Returns:
        A dict keyed by (doc_name, section_number) -> section text string.

    Raises:
        FileNotFoundError: If any of the target files are missing.
        ValueError: If any document cannot be parsed into sections.
    """
    if policy_files is None:
        policy_files = POLICY_FILES

    index = {}
    section_pattern = re.compile(r"^\s*([0-9]+\.[0-9]+)\s+(.*)")

    for doc_name, filepath in policy_files.items():
        abs_path = os.path.abspath(filepath)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(
                f"Policy file not found: {abs_path}\n"
                f"Expected document: {doc_name}"
            )

        current_section = None
        parsed_any = False

        with open(abs_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.rstrip("\n")
                match = section_pattern.match(line_str)
                if match:
                    current_section = match.group(1)
                    text = match.group(2).strip()
                    index[(doc_name, current_section)] = text
                    parsed_any = True
                elif current_section is not None:
                    # Continuation line (indented) or blank
                    stripped = line_str.strip()
                    if line_str.startswith(" ") or line_str.startswith("\t"):
                        index[(doc_name, current_section)] += " " + stripped
                    elif not stripped:
                        continue
                    else:
                        # Non-indented, non-empty, non-section line → heading/separator, reset
                        current_section = None

        if not parsed_any:
            raise ValueError(
                f"Could not parse any sections from document: {doc_name}\n"
                f"Ensure the file contains numbered sections in X.Y format."
            )

    # Normalise whitespace in all values
    for key in index:
        index[key] = re.sub(r"\s+", " ", index[key]).strip()

    return index


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------

# Keyword mapping from topic phrases to (doc_name, section_numbers) hints.
# This guides the single-source search. Sections listed first are preferred.
KEYWORD_MAP = [
    # HR Leave policy
    (["carry forward", "carry-forward", "unused annual leave", "unused leave"],
     "policy_hr_leave.txt", ["2.6", "2.7"]),
    (["annual leave", "paid leave", "accrues", "18 days"],
     "policy_hr_leave.txt", ["2.1", "2.2"]),
    (["leave application", "apply for leave", "submit a leave"],
     "policy_hr_leave.txt", ["2.3"]),
    (["written approval", "verbal approval", "leave approval", "manager approval"],
     "policy_hr_leave.txt", ["2.4"]),
    (["unapproved absence", "loss of pay", "lop"],
     "policy_hr_leave.txt", ["2.5"]),
    (["sick leave", "medical certificate", "sick"],
     "policy_hr_leave.txt", ["3.1", "3.2", "3.3", "3.4"]),
    (["maternity", "paternity"],
     "policy_hr_leave.txt", ["4.1", "4.2", "4.3", "4.4"]),
    (["leave without pay", "lwp", "who approves leave without pay"],
     "policy_hr_leave.txt", ["5.1", "5.2", "5.3"]),
    (["encash", "encashment"],
     "policy_hr_leave.txt", ["7.1", "7.2", "7.3"]),
    (["grievance", "grievances"],
     "policy_hr_leave.txt", ["8.1", "8.2"]),

    # IT policy
    (["install", "software", "slack", "work laptop", "corporate device"],
     "policy_it_acceptable_use.txt", ["2.3", "2.4"]),
    (["personal phone", "personal device", "byod", "work files from home",
      "phone to access", "phone for work"],
     "policy_it_acceptable_use.txt", ["3.1", "3.2", "3.3"]),
    (["password", "mfa", "multi-factor"],
     "policy_it_acceptable_use.txt", ["4.1", "4.2", "4.3", "4.4"]),
    (["confidential data", "data handling", "restricted data"],
     "policy_it_acceptable_use.txt", ["5.1", "5.2", "5.3"]),
    (["internet use", "email use", "cmc email"],
     "policy_it_acceptable_use.txt", ["6.1", "6.2", "6.3"]),
    (["violation", "disciplinary", "consequence"],
     "policy_it_acceptable_use.txt", ["7.1", "7.2", "7.3"]),

    # Finance policy
    (["home office", "equipment allowance", "work from home equipment", "wfh allowance"],
     "policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.4", "3.5"]),
    (["da", "daily allowance", "meal receipt", "meal claim", "meal expenses"],
     "policy_finance_reimbursement.txt", ["2.5", "2.6"]),
    (["travel", "outstation", "air travel", "hotel"],
     "policy_finance_reimbursement.txt", ["2.1", "2.2", "2.3", "2.4"]),
    (["training", "professional development", "certification", "course fee"],
     "policy_finance_reimbursement.txt", ["4.1", "4.2", "4.3", "4.4"]),
    (["mobile phone", "mobile reimbursement", "internet reimbursement"],
     "policy_finance_reimbursement.txt", ["5.1", "5.2", "5.3"]),
    (["submit", "submission", "reimbursement claim", "portal", "fin-exp1"],
     "policy_finance_reimbursement.txt", ["6.1", "6.2", "6.3", "6.4"]),
]


def _score_query(query_lower: str, keywords: list) -> int:
    """Returns the number of keyword matches for a given query string."""
    return sum(1 for kw in keywords if kw in query_lower)


def answer_question(indexed_documents: dict, query: str) -> str:
    """
    Searches indexed documents for the best single-source answer to the query.

    Enforcement (from agents.md):
    - Returns answer from ONE document only (no cross-document blending).
    - Every answer cites document name + section number.
    - Returns REFUSAL_TEMPLATE if no match found or if the answer requires blending.

    Args:
        indexed_documents: dict of (doc_name, section_number) -> section text.
        query: The user's question string.

    Returns:
        A string — either a cited single-source answer or the exact REFUSAL_TEMPLATE.
    """
    query_lower = query.lower()

    # Score each keyword group against the query
    candidates = []
    for entry in KEYWORD_MAP:
        keywords, doc_name, sections = entry
        score = _score_query(query_lower, keywords)
        if score > 0:
            candidates.append((score, doc_name, sections))

    if not candidates:
        return REFUSAL_TEMPLATE

    # Sort by descending score; take the best match
    candidates.sort(key=lambda x: -x[0])
    best_score = candidates[0][0]

    # Collect all top-scoring candidate docs
    top_candidates = [c for c in candidates if c[0] == best_score]
    top_docs = set(c[1] for c in top_candidates)

    # ENFORCEMENT: If the best matches span multiple documents — refuse (cross-document blend risk)
    if len(top_docs) > 1:
        return REFUSAL_TEMPLATE

    # Single best-matching document
    _, best_doc, best_sections = candidates[0]

    # Build answer from the relevant sections of that one document
    answer_parts = []
    for section in best_sections:
        key = (best_doc, section)
        if key in indexed_documents:
            answer_parts.append((section, indexed_documents[key]))

    if not answer_parts:
        return REFUSAL_TEMPLATE

    # Format output with citations
    lines = [f"Source: {best_doc}\n"]
    for section_num, text in answer_parts:
        lines.append(f"Section {section_num}: {text}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("=" * 62)
    print("  UC-X — Ask My Documents (CMC Policy Q&A)")
    print("=" * 62)
    print("Documents loaded:")
    for doc in POLICY_FILES:
        print(f"  • {doc}")
    print()
    print("Type your question and press Enter.")
    print("Type 'exit' or 'quit' to leave.")
    print("-" * 62)

    # Load documents once at startup
    try:
        indexed = retrieve_documents()
    except (FileNotFoundError, ValueError) as e:
        print(f"\n[ERROR] Failed to load policy documents:\n{e}")
        return

    print(f"[OK] Indexed {len(indexed)} sections across {len(POLICY_FILES)} documents.\n")

    while True:
        try:
            query = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.")
            break

        if not query:
            continue

        if query.lower() in ("exit", "quit"):
            print("Exiting. Goodbye.")
            break

        print()
        response = answer_question(indexed, query)
        print(response)
        print("-" * 62)


if __name__ == "__main__":
    main()
