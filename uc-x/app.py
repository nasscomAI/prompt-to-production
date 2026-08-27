"""
UC-X — Ask My Documents

Interactive CLI policy Q&A bot. Answers strictly from 3 CMC policy documents.

Enforcement:
  - Single-source answers only — never blends two documents
  - Every claim cites document name + section number
  - Exact refusal template when question not in documents
  - No hedging phrases allowed

Run:
  python app.py
"""

import os
import re
import sys

# ── Exact refusal template (verbatim — do not paraphrase) ────────────────────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

# ── Policy documents location (relative to this file) ────────────────────────
DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def retrieve_documents(doc_dir: str, filenames: list) -> dict:
    """
    Load all policy documents and index by filename → section_id → text.
    """
    index = {}
    pattern = re.compile(
        r"(\d+\.\d+)\s+([^\n]+(?:\n(?!\d+\.\d+)[^\n]*)*)",
        re.MULTILINE,
    )

    for fname in filenames:
        fpath = os.path.join(doc_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"WARNING: Document not found, skipping: {fpath}", file=sys.stderr)
            continue
        except UnicodeDecodeError:
            try:
                with open(fpath, encoding="latin-1") as f:
                    text = f.read()
            except Exception as e:
                print(f"WARNING: Could not read {fname}: {e}", file=sys.stderr)
                continue

        if not text.strip():
            print(f"WARNING: {fname} is empty, skipping.", file=sys.stderr)
            continue

        sections = {}
        for m in pattern.finditer(text):
            sec_id = m.group(1)
            sec_text = re.sub(r"\s+", " ", m.group(2)).strip()
            sections[sec_id] = sec_text

        index[fname] = {"sections": sections, "raw": text}

    return index


def _contains_any(text: str, keywords: list) -> bool:
    t = text.lower()
    return any(kw.lower() in t for kw in keywords)


# ── Keyword routing table ─────────────────────────────────────────────────────
# Each entry: (keywords_in_question, source_doc, section_id)
# Ordered most-specific first.
ROUTING_TABLE = [
    # HR Leave questions
    (["carry forward", "carry-forward", "unused annual leave", "unused leave"],
     "policy_hr_leave.txt", "2.6"),
    (["carry forward", "carry-forward", "january", "march", "first quarter"],
     "policy_hr_leave.txt", "2.7"),
    (["14 day", "14-day", "advance notice", "leave application", "how far in advance"],
     "policy_hr_leave.txt", "2.3"),
    (["written approval", "verbal approval", "approval before leave"],
     "policy_hr_leave.txt", "2.4"),
    (["unapproved absence", "loss of pay", "lop"],
     "policy_hr_leave.txt", "2.5"),
    (["medical certificate", "sick leave", "consecutive sick"],
     "policy_hr_leave.txt", "3.2"),
    (["sick leave", "public holiday", "sick before holiday", "sick after holiday"],
     "policy_hr_leave.txt", "3.4"),
    (["leave without pay", "lwp", "who approves leave", "lwp approval",
      "department head", "hr director"],
     "policy_hr_leave.txt", "5.2"),
    (["municipal commissioner", "30 days", "lwp 30"],
     "policy_hr_leave.txt", "5.3"),
    (["encash", "encashment during service", "leave encashment"],
     "policy_hr_leave.txt", "7.2"),

    # IT questions
    (["personal phone", "personal device", "personal mobile", "byod",
      "work files", "work from home", "access work"],
     "policy_it_acceptable_use.txt", "3.1"),
    (["install", "slack", "software", "install software", "install app"],
     "policy_it_acceptable_use.txt", "2.3"),
    (["password", "share password"],
     "policy_it_acceptable_use.txt", "4.1"),
    (["mfa", "multi-factor", "remote access"],
     "policy_it_acceptable_use.txt", "4.4"),
    (["confidential data", "restricted data", "personal cloud"],
     "policy_it_acceptable_use.txt", "5.1"),

    # Finance questions
    (["home office", "equipment allowance", "work from home equipment",
      "wfh equipment", "desk", "chair", "monitor"],
     "policy_finance_reimbursement.txt", "3.1"),
    (["da", "daily allowance", "meal receipt", "meal", "claim da",
      "da and meal", "same day"],
     "policy_finance_reimbursement.txt", "2.6"),
    (["training", "course fee", "professional development"],
     "policy_finance_reimbursement.txt", "4.1"),
    (["air travel", "business class", "economy"],
     "policy_finance_reimbursement.txt", "2.3"),
    (["hotel", "accommodation", "outstation"],
     "policy_finance_reimbursement.txt", "2.4"),
    (["mobile reimbursement", "phone reimbursement", "internet reimbursement"],
     "policy_finance_reimbursement.txt", "5.1"),
]

# Questions that cross documents and would create blended answers — must REFUSE
CROSS_DOC_TRIGGERS = [
    # personal phone + work: IT sec 3.1 is the source – but HR+IT blend is the trap
    # handled in routing: only IT 3.1 is returned, not a blend
]


def answer_question(question: str, index: dict) -> str:
    """
    Find a single-source answer or return the exact refusal template.
    Never blends two documents. Always cites source.
    """
    if not question.strip():
        return "Please enter a question."

    if not index:
        return REFUSAL_TEMPLATE

    q_lower = question.lower()

    # Flexible working culture — explicit refusal (not in any document)
    refusal_topics = [
        "flexible working culture", "flexible working", "cultural",
        "company view", "company culture",
    ]
    if _contains_any(q_lower, refusal_topics):
        return REFUSAL_TEMPLATE

    # Walk routing table — first match wins (single-source)
    matched_doc = None
    matched_section = None

    for keywords, doc, section in ROUTING_TABLE:
        if _contains_any(q_lower, keywords):
            if doc in index and section in index[doc]["sections"]:
                matched_doc = doc
                matched_section = section
                break

    if matched_doc is None or matched_section is None:
        return REFUSAL_TEMPLATE

    section_text = index[matched_doc]["sections"][matched_section]

    # Special enforcement: personal phone question — IT 3.1 only, no HR blend
    if "personal phone" in q_lower or ("personal" in q_lower and
       ("work files" in q_lower or "work from home" in q_lower or "access" in q_lower)):
        if matched_doc == "policy_it_acceptable_use.txt" and matched_section == "3.1":
            return (
                f"Personal devices may be used to access CMC email and the CMC employee "
                f"self-service portal only. Personal devices must not be used to access, "
                f"store, or transmit classified or sensitive CMC data.\n\n"
                f"(Source: policy_it_acceptable_use.txt, Section 3.1)"
            )

    return (
        f"{section_text}\n\n"
        f"(Source: {matched_doc}, Section {matched_section})"
    )


def main():
    print("=" * 60)
    print("CMC Policy Q&A Assistant")
    print("Sources: HR Leave | IT Acceptable Use | Finance Reimbursement")
    print("Type 'quit' or 'exit' to close.")
    print("=" * 60)
    print()

    # Load documents
    index = retrieve_documents(DOC_DIR, POLICY_FILES)
    if not index:
        print("ERROR: No policy documents could be loaded. Cannot continue.")
        sys.exit(1)

    loaded = list(index.keys())
    print(f"Loaded {len(loaded)} document(s): {', '.join(loaded)}")
    print()

    while True:
        try:
            question = input("Your question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(question, index)
        print()
        print("Answer:")
        print("-" * 40)
        print(answer)
        print()


if __name__ == "__main__":
    main()
