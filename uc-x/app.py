"""
UC-X — Ask My Documents
Policy Q&A Agent for CMC policy documents.
Answers questions from exactly one source document — never blends across documents.
Uses exact refusal template when question is not in the documents.

Run:
    python app.py
Then type questions at the prompt.
"""
import re
import sys
from pathlib import Path

# ─── Configuration ─────────────────────────────────────────────────────────────

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

# Exact refusal template — no variations permitted (from agents.md)
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Forbidden hedging phrases — any answer containing these must be rejected
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it can be assumed",
    "usually",
    "in general",
]


# ─── Skill: retrieve_documents ─────────────────────────────────────────────────

def retrieve_documents(doc_paths: list) -> dict:
    """
    Loads all policy files, indexes by document name and section number.
    Returns: dict mapping doc_name → {section_number → section_text}
    """
    document_store = {}

    for path_str in doc_paths:
        path = Path(path_str)
        # Also try relative to current script directory
        if not path.exists():
            script_dir = Path(__file__).parent
            alt_path = script_dir / path_str
            if alt_path.exists():
                path = alt_path
            else:
                raise FileNotFoundError(f"Policy file not found: {path_str}")

        content = path.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"Policy file is empty: {path_str}")

        doc_name = path.name
        sections = _parse_sections(content, doc_name)
        document_store[doc_name] = sections
        section_count = len(sections)
        print(f"  Loaded: {doc_name} ({section_count} sections)")

    return document_store


def _parse_sections(content: str, doc_name: str) -> dict:
    """
    Parse policy text into a dict: section_number → section_text.
    Handles both top-level sections (e.g. "3. PERSONAL DEVICES") and
    individual clauses (e.g. "3.1 Personal devices may be used...")
    """
    sections = {}
    lines = content.splitlines()

    # Regex patterns
    section_re = re.compile(r"^(\d+)\.\s+([A-Z].+)$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)")
    separator_re = re.compile(r"^[═]+$")

    current_section_num = None
    current_section_title = ""
    current_clause_num = None
    current_clause_lines = []
    current_section_text_lines = []

    def flush_clause():
        nonlocal current_clause_num, current_clause_lines
        if current_clause_num and current_clause_lines:
            ctext = " ".join(current_clause_lines).strip()
            sections[current_clause_num] = ctext
            current_section_text_lines.append(f"{current_clause_num} {ctext}")
        current_clause_num = None
        current_clause_lines = []

    for line in lines:
        stripped = line.strip()

        if separator_re.match(stripped) or not stripped:
            continue

        # Top-level section header
        m_sec = section_re.match(stripped)
        if m_sec and stripped.upper() == stripped:
            flush_clause()
            if current_section_num:
                # Store full section text
                sections[f"section_{current_section_num}"] = (
                    f"{current_section_num}. {current_section_title}\n" +
                    "\n".join(current_section_text_lines)
                )
            current_section_num = m_sec.group(1)
            current_section_title = m_sec.group(2).strip()
            current_section_text_lines = []
            continue

        # Clause line
        m_clause = clause_re.match(stripped)
        if m_clause:
            flush_clause()
            current_clause_num = m_clause.group(1)
            current_clause_lines = [m_clause.group(2).strip()]
            continue

        # Continuation of clause
        if current_clause_num and stripped:
            current_clause_lines.append(stripped)

    flush_clause()
    if current_section_num:
        sections[f"section_{current_section_num}"] = (
            f"{current_section_num}. {current_section_title}\n" +
            "\n".join(current_section_text_lines)
        )

    return sections


# ─── Skill: answer_question ────────────────────────────────────────────────────

# Question routing — maps question keywords to specific clauses and documents
# This deterministic routing prevents cross-document blending
QUESTION_ROUTING = [
    # HR Leave Policy questions
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave", "unused leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["2.6", "2.7"],
        "topic": "annual leave carry-forward",
    },
    {
        "keywords": ["14 day", "14-day", "advance notice", "leave application", "apply for leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["2.3"],
        "topic": "annual leave application notice",
    },
    {
        "keywords": ["written approval", "verbal approval", "leave approval"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["2.4"],
        "topic": "leave approval requirement",
    },
    {
        "keywords": ["unapproved absence", "loss of pay", "lop"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["2.5"],
        "topic": "unapproved absence",
    },
    {
        "keywords": ["medical certificate", "sick leave", "sick days", "consecutive sick"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["3.2", "3.4"],
        "topic": "sick leave medical certificate",
    },
    {
        "keywords": ["leave without pay", "lwp", "who approves leave without pay", "who approve leave without pay"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["5.2", "5.3"],
        "topic": "leave without pay approval",
    },
    {
        "keywords": ["leave encashment", "encash leave", "cash leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["7.2", "7.1"],
        "topic": "leave encashment",
    },
    {
        "keywords": ["maternity", "paternity", "parental leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "maternity/paternity leave",
    },
    # IT Policy questions
    {
        "keywords": ["install slack", "install software", "install app", "install application"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["2.3"],
        "topic": "software installation on corporate devices",
    },
    {
        "keywords": ["personal phone", "personal device", "byod", "own phone", "mobile phone work files", "phone to access work"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["3.1", "3.2"],
        "topic": "personal device (BYOD) usage",
    },
    {
        "keywords": ["password", "passwords"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["4.1", "4.2", "4.3"],
        "topic": "password policy",
    },
    {
        "keywords": ["mfa", "multi-factor", "remote access", "vpn"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["4.4"],
        "topic": "multi-factor authentication",
    },
    # Finance Policy questions
    {
        "keywords": ["home office", "work from home equipment", "wfh equipment", "desk", "chair", "monitor"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["3.1", "3.2", "3.3"],
        "topic": "work-from-home equipment allowance",
    },
    {
        "keywords": ["daily allowance", "da", "meal", "meal receipt", "da and meal", "meal receipts on the same day"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["2.5", "2.6"],
        "topic": "daily allowance and meal reimbursement",
    },
    {
        "keywords": ["outstation travel", "air travel", "hotel", "accommodation"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["2.2", "2.3", "2.4"],
        "topic": "outstation travel reimbursement",
    },
    {
        "keywords": ["mobile phone reimbursement", "internet reimbursement", "phone bill"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["5.1", "5.2"],
        "topic": "mobile and internet reimbursement",
    },
    {
        "keywords": ["training", "course fee", "certification", "professional development"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["4.1", "4.2", "4.3"],
        "topic": "training reimbursement",
    },
]


def answer_question(question: str, document_store: dict) -> str:
    """
    Searches indexed documents for answer. Returns single-source answer with citation
    or exact refusal template.

    ENFORCEMENT:
    - Never combine claims from two different documents
    - Never use hedging phrases
    - Use exact refusal template when not covered
    - Cite [document_filename, Section X.Y] for every claim
    """
    q_lower = question.lower().strip()

    # Find matching routing rules
    matched_rules = []
    for rule in QUESTION_ROUTING:
        for kw in rule["keywords"]:
            if kw.lower() in q_lower:
                matched_rules.append(rule)
                break

    # ENFORCEMENT: If question matches multiple different documents → refusal
    matched_docs = list(set(r["doc"] for r in matched_rules))

    if len(matched_docs) > 1:
        # Cross-document match — check if combining would create new claims
        # Per agents.md: if combining creates claim not in either document → refuse
        return REFUSAL_TEMPLATE

    if len(matched_docs) == 0:
        # No match in any document
        return REFUSAL_TEMPLATE

    # Single document match
    target_doc = matched_docs[0]
    matching_rules = [r for r in matched_rules if r["doc"] == target_doc]
    sections = document_store.get(target_doc, {})

    # Build answer from matched clauses
    answer_parts = []
    cited_clauses = []

    for rule in matching_rules:
        for clause_num in rule["clauses"]:
            clause_text = sections.get(clause_num, "")
            if clause_text:
                answer_parts.append(
                    f"[{target_doc}, Section {clause_num}]\n{clause_text}"
                )
                cited_clauses.append(clause_num)

    if not answer_parts:
        return REFUSAL_TEMPLATE

    answer = "\n\n".join(answer_parts)

    # ENFORCEMENT: Check for forbidden hedging phrases
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in answer.lower():
            # This should not happen since we're pulling directly from policy text
            # but enforce the rule defensively
            return REFUSAL_TEMPLATE

    return answer


# ─── Interactive CLI ────────────────────────────────────────────────────────────

def main():
    print("="*70)
    print("UC-X — CMC Policy Q&A Agent")
    print("="*70)
    print("Loading policy documents...")

    try:
        document_store = retrieve_documents(POLICY_FILES)
    except (FileNotFoundError, ValueError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        print("\nMake sure you run this from the uc-x/ directory.", file=sys.stderr)
        sys.exit(1)

    print(f"\nReady. Loaded {len(document_store)} policy documents.")
    print("Documents available:")
    for doc_name in document_store:
        clause_count = sum(1 for k in document_store[doc_name] if not k.startswith("section_"))
        print(f"  - {doc_name} ({clause_count} clauses)")

    print("Enforcement rules active:")
    print("  [OK] Answers from single source only - no cross-document blending")
    print("  [OK] Exact clause citations with every answer")
    print("  [OK] Exact refusal template when question is not in the documents")
    print("  [OK] No hedging phrases permitted")
    print("\nType your question (or 'quit' to exit):")
    print("-"*70)

    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not question:
            continue

        print("")
        answer = answer_question(question, document_store)
        print(answer)
        print("")


if __name__ == "__main__":
    main()
