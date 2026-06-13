"""
UC-X app.py -- Policy Q&A Agent: Ask My Documents
Interactive CLI that answers employee questions from 3 CMC policy documents.

Skills:
  - retrieve_documents : loads & indexes all 3 policy .txt files by section
  - answer_question    : returns single-source cited answer OR exact refusal template

Enforcement (from agents.md):
  1. Never blend claims from two documents into one answer
  2. Never use hedging phrases
  3. Exact refusal template when question is not in any document
  4. Every answer cites document name + section number


Run:
  python app.py
"""

import re
import sys
import os
from pathlib import Path

# ---- Document paths (relative to this script) ----------------------------
POLICY_FILES = {
    "policy_hr_leave.txt":             "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":    "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt":"../data/policy-documents/policy_finance_reimbursement.txt",
}

# Exact refusal template from README / agents.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# ---- Document reference codes --------------------------------------------
DOC_REF = {
    "policy_hr_leave.txt":             "HR-POL-001",
    "policy_it_acceptable_use.txt":    "IT-POL-003",
    "policy_finance_reimbursement.txt":"FIN-POL-007",
}

# ---- Banned hedging phrases (enforcement rule 2) -------------------------
BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "often",
]


# ==========================================================================
# SKILL: retrieve_documents
# ==========================================================================
def retrieve_documents(file_map: dict) -> dict:
    """
    Loads all policy .txt files and indexes them by doc_name -> section_id -> text.

    Returns:
        {
          "policy_hr_leave.txt": {
            "ref": "HR-POL-001",
            "sections": { "2.3": {"section_id": "2.3", "text": "..."}, ... }
          }, ...
        }

    Raises:
        FileNotFoundError -- if any file is missing
        ValueError        -- if any file has no recognisable clause structure
    """
    index = {}

    heading_re = re.compile(r"^(\d+)\.\s+[A-Z]")
    clause_re  = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for doc_name, rel_path in file_map.items():
        script_dir = Path(__file__).parent
        full_path  = (script_dir / rel_path).resolve()

        if not full_path.exists():
            raise FileNotFoundError(
                f"[retrieve_documents] File not found: '{full_path}'\n"
                f"Expected at: {rel_path}"
            )
        try:
            content = full_path.read_text(encoding="utf-8")
        except Exception as e:
            raise FileNotFoundError(
                f"[retrieve_documents] Cannot read '{full_path}': {e}"
            ) from e

        if not content.strip():
            raise ValueError(
                f"[retrieve_documents] '{doc_name}' is empty."
            )

        sections = {}
        current_clause_id   = None
        current_clause_text = []

        def flush():
            if current_clause_id:
                sections[current_clause_id] = {
                    "section_id": current_clause_id,
                    "text": " ".join(current_clause_text).strip()
                }

        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or set(stripped) <= {"=", "-", chr(0x2550), " "}:
                continue
            if heading_re.match(stripped):
                flush()
                current_clause_id   = None
                current_clause_text = []
                continue
            m = clause_re.match(stripped)
            if m:
                flush()
                current_clause_id   = m.group(1)
                current_clause_text = [m.group(2).strip()]
            elif current_clause_id:
                current_clause_text.append(stripped)

        flush()

        if not sections:
            raise ValueError(
                f"[retrieve_documents] No clauses found in '{doc_name}'."
            )

        index[doc_name] = {
            "ref":      DOC_REF.get(doc_name, doc_name),
            "sections": sections
        }

    return index


# ==========================================================================
# SKILL: answer_question
# ==========================================================================

# Keyword map: maps keyword tokens -> (doc_name, [section_ids])
# Ordered from most-specific to least-specific
KEYWORD_RULES = [
    # HR Leave
    (["carry forward", "carry-forward", "carryforward", "annual leave", "unused leave"],
     "policy_hr_leave.txt", ["2.6", "2.7"]),

    (["leave without pay", "lwp", "unpaid leave"],
     "policy_hr_leave.txt", ["5.2", "5.3"]),

    (["sick leave", "medical certificate", "sick day"],
     "policy_hr_leave.txt", ["3.2", "3.4"]),

    (["annual leave", "paid leave", "leave entitlement", "leave days"],
     "policy_hr_leave.txt", ["2.1", "2.3", "2.4"]),

    (["maternity", "paternity"],
     "policy_hr_leave.txt", ["4.1", "4.2", "4.3", "4.4"]),

    (["encash", "encashment", "cash out leave"],
     "policy_hr_leave.txt", ["7.2"]),

    # IT Acceptable Use
    (["install", "software", "slack", "application", "app"],
     "policy_it_acceptable_use.txt", ["2.3", "2.4"]),

    (["personal phone", "personal device", "byod", "own phone", "own device",
      "personal mobile", "mobile phone"],
     "policy_it_acceptable_use.txt", ["3.1", "3.2", "3.3"]),

    (["password", "mfa", "multi-factor", "authentication"],
     "policy_it_acceptable_use.txt", ["4.1", "4.2", "4.3", "4.4"]),

    (["endpoint", "security agent", "antivirus"],
     "policy_it_acceptable_use.txt", ["2.6"]),

    (["email", "cmc email", "personal email", "forward email"],
     "policy_it_acceptable_use.txt", ["5.2", "6.2"]),

    # Finance
    (["home office", "equipment allowance", "wfh allowance", "work from home allowance",
      "work-from-home allowance"],
     "policy_finance_reimbursement.txt", ["3.1", "3.2", "3.3", "3.5"]),

    (["da", "daily allowance", "meal", "meal receipt", "meal claim"],
     "policy_finance_reimbursement.txt", ["2.5", "2.6"]),

    (["travel", "outstation", "hotel", "accommodation", "air travel", "flight"],
     "policy_finance_reimbursement.txt", ["2.1", "2.2", "2.3", "2.4"]),

    (["training", "course fee", "certification", "professional development"],
     "policy_finance_reimbursement.txt", ["4.1", "4.2", "4.3", "4.4"]),

    (["mobile reimbursement", "phone reimbursement", "internet reimbursement",
      "mobile allowance", "internet allowance"],
     "policy_finance_reimbursement.txt", ["5.1", "5.2"]),

    (["reimbursement", "claim", "expense", "receipt"],
     "policy_finance_reimbursement.txt", ["1.3", "6.1", "6.2", "6.3"]),
]

# Questions that cross documents and must NOT be blended -> use refusal
CROSS_DOC_TRAP_KEYWORDS = [
    # personal phone + work files from home -> IT 3.1 only (not HR blend)
    # handled by special logic below
]


def _matches(question_lower: str, keywords: list) -> bool:
    return any(kw in question_lower for kw in keywords)


def answer_question(question: str, doc_index: dict) -> dict:
    """
    Returns a single-source cited answer or the exact refusal template.

    Rules enforced:
      - ONE document per answer, no blending
      - Exact refusal template if not found
      - Every answer cites doc ref + section
    """
    if not doc_index:
        raise ValueError(
            "[answer_question] Document index is empty — retrieve_documents failed."
        )

    q = question.lower().strip()

    # ---- Special cross-document trap detection ---------------------------
    # "personal phone" + "work files" / "work from home" -> IT 3.1 ONLY (no HR blend)
    is_personal_phone = _matches(q, ["personal phone", "personal device", "own phone",
                                     "own mobile", "byod"])
    is_wfh_files      = _matches(q, ["work files", "work from home", "working from home",
                                     "wfh", "remote work", "access files"])

    if is_personal_phone and is_wfh_files:
        # Answer ONLY from IT-POL-003 section 3.1 — must not blend with HR
        doc  = doc_index["policy_it_acceptable_use.txt"]
        secs = [doc["sections"][s] for s in ["3.1", "3.2"] if s in doc["sections"]]
        answer_text = _format_answer(secs, doc["ref"], "policy_it_acceptable_use.txt")
        return {
            "answer":     answer_text,
            "source_doc": "policy_it_acceptable_use.txt",
            "section":    "3.1, 3.2",
            "is_refusal": False,
        }

    # ---- Keyword matching ------------------------------------------------
    for keywords, doc_name, section_ids in KEYWORD_RULES:
        if _matches(q, keywords):
            doc  = doc_index.get(doc_name, {})
            secs = [doc["sections"][s] for s in section_ids
                    if s in doc.get("sections", {})]
            if secs:
                cited_sections = ", ".join(section_ids)
                answer_text    = _format_answer(secs, doc["ref"], doc_name)
                return {
                    "answer":     answer_text,
                    "source_doc": doc_name,
                    "section":    cited_sections,
                    "is_refusal": False,
                }

    # ---- No match found -> exact refusal template -----------------------
    return {
        "answer":     REFUSAL_TEMPLATE,
        "source_doc": "REFUSAL",
        "section":    "",
        "is_refusal": True,
    }


def _format_answer(sections: list, doc_ref: str, doc_name: str) -> str:
    """Formats section text into a cited answer string."""
    lines = [f"Source: {doc_ref} ({doc_name})", ""]
    for s in sections:
        lines.append(f"Section {s['section_id']}: {s['text']}")
    return "\n".join(lines)


# ==========================================================================
# MAIN — Interactive CLI
# ==========================================================================
def main():
    # Configure stdout for UTF-8 on Windows
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 65)
    print("  UC-X: Ask My Documents -- CMC Policy Q&A Agent")
    print("  Loaded: HR-POL-001 | IT-POL-003 | FIN-POL-007")
    print("=" * 65)
    print("  Type your question and press Enter.")
    print("  Type 'test' to run all 7 README test questions.")
    print("  Type 'quit' or 'exit' to leave.")
    print("=" * 65)
    print()

    # Load documents
    print("[retrieve_documents] Loading policy documents...")
    try:
        doc_index = retrieve_documents(POLICY_FILES)
        for doc_name, data in doc_index.items():
            clause_count = len(data["sections"])
            print(f"  Loaded {doc_name} ({data['ref']}) -- {clause_count} clauses")
    except (FileNotFoundError, ValueError) as e:
        print(f"\nFATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print()

    # 7 README test questions
    TEST_QUESTIONS = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]

    def ask_and_print(question: str):
        print(f"Q: {question}")
        print("-" * 65)
        result = answer_question(question, doc_index)
        print(result["answer"])
        if result["is_refusal"]:
            print("\n[REFUSAL TEMPLATE USED -- no document covers this question]")
        print()

    # Interactive loop
    while True:
        try:
            user_input = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if user_input.lower() == "test":
            print()
            print("=" * 65)
            print("  Running all 7 README test questions")
            print("=" * 65)
            print()
            for i, q in enumerate(TEST_QUESTIONS, 1):
                print(f"[TEST {i}/7]")
                ask_and_print(q)
            print("=" * 65)
            print("  All 7 test questions complete.")
            print("=" * 65)
            print()
            continue

        print()
        ask_and_print(user_input)


if __name__ == "__main__":
    main()
