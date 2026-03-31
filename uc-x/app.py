"""
UC-X app.py — Ask My Documents
City Municipal Corporation (CMC) Policy Q&A CLI.

Implements:
  - retrieve_documents  : loads and indexes all 3 policy files by section
  - answer_question     : single-source lookup with mandatory citation
                          or verbatim refusal template

Run:  python app.py
"""

import os
import re
import sys

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_DIR = os.path.join(SCRIPT_DIR, "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# ─────────────────────────────────────────────
# Refusal template (verbatim — must not be altered)
# ─────────────────────────────────────────────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt,\n"
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# ─────────────────────────────────────────────
# SKILL: retrieve_documents
# ─────────────────────────────────────────────
def retrieve_documents(policy_dir: str, filenames: list[str]) -> dict:
    """
    Load all policy files and index every section.

    Returns:
        dict keyed by (filename, section_number) → section_text (str)
    Raises:
        FileNotFoundError if any file cannot be opened.
    """
    index: dict[tuple[str, str], str] = {}

    for fname in filenames:
        fpath = os.path.join(policy_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                content = fh.read()
        except OSError as exc:
            raise FileNotFoundError(
                f"Policy document not found or unreadable: {fpath}"
            ) from exc

        # Split on section headings like "2.6", "3.1", etc.
        # Pattern captures the section number and everything until the next section.
        sections = re.split(r"(?m)^(\d+\.\d+)\s+", content)
        # sections = [preamble, sec_num, sec_body, sec_num, sec_body, ...]
        i = 1
        while i < len(sections) - 1:
            sec_num = sections[i].strip()
            sec_body = sections[i + 1].strip()
            index[(fname, sec_num)] = sec_body
            i += 2

    return index


# ─────────────────────────────────────────────
# Keyword table for single-source routing
#
# Maps question keywords → (document, section) candidates
# Ordered from most-specific to least-specific within each doc.
# The BYOD/personal-phone row deliberately points to IT only (trap guard).
# ─────────────────────────────────────────────
ROUTES = [
    # ── HR: Annual leave carry-forward ──────────────────────────────────
    {
        "keywords": ["carry forward", "carry-forward", "unused leave", "unused annual"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.6", "2.7"],
    },
    # ── HR: Leave Without Pay approval ──────────────────────────────────
    {
        "keywords": ["leave without pay", "lwp", "unpaid leave", "who approves leave without"],
        "doc": "policy_hr_leave.txt",
        "sections": ["5.2"],
    },
    # ── HR: Annual leave entitlement ────────────────────────────────────
    {
        "keywords": ["annual leave", "paid leave", "leave entitlement"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.1", "2.2", "2.3", "2.4", "2.5"],
    },
    # ── HR: Sick leave ──────────────────────────────────────────────────
    {
        "keywords": ["sick leave", "medical certificate", "sick day"],
        "doc": "policy_hr_leave.txt",
        "sections": ["3.1", "3.2", "3.3"],
    },
    # ── HR: Maternity / paternity ────────────────────────────────────────
    {
        "keywords": ["maternity", "paternity", "parental leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["4.1", "4.2", "4.3"],
    },
    # ── HR: Leave encashment ────────────────────────────────────────────
    {
        "keywords": ["encash", "encashment"],
        "doc": "policy_hr_leave.txt",
        "sections": ["7.1", "7.2"],
    },
    # ── HR: Public holiday / compensatory ───────────────────────────────
    {
        "keywords": ["public holiday", "compensatory", "comp off"],
        "doc": "policy_hr_leave.txt",
        "sections": ["6.1", "6.2", "6.3"],
    },

    # ── IT: Software installation (Slack, apps, software) ─────────────
    {
        "keywords": ["install", "slack", "software", "application", "app on"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["2.3", "2.4"],
    },
    # ── IT: Personal device / BYOD / phone for work files ─────────────
    #   CROSS-DOCUMENT TRAP GUARD: answer from IT only, never blend HR.
    {
        "keywords": [
            "personal phone", "personal device", "byod", "my phone",
            "personal mobile", "own phone", "own device",
            "work files", "work file", "access work",
        ],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2"],
    },
    # ── IT: Passwords / MFA ─────────────────────────────────────────────
    {
        "keywords": ["password", "mfa", "multi-factor", "authentication"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
    },
    # ── IT: Data handling / confidential ────────────────────────────────
    {
        "keywords": ["confidential", "classified", "data handling", "sensitive data"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["5.1", "5.2"],
    },

    # ── Finance: DA and meal receipts ───────────────────────────────────
    {
        "keywords": ["da and meal", "daily allowance", "meal receipt", "meal claim", "claim da"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.5", "2.6"],
    },
    # ── Finance: Home office equipment / WFH allowance ─────────────────
    {
        "keywords": ["home office", "wfh equipment", "work from home equipment",
                     "equipment allowance", "home equipment"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["3.1", "3.2", "3.3"],
    },
    # ── Finance: Travel reimbursement ───────────────────────────────────
    {
        "keywords": ["travel reimburs", "outstation", "air travel", "hotel", "accommodation"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.1", "2.2", "2.3", "2.4"],
    },
    # ── Finance: Training / professional development ─────────────────────
    {
        "keywords": ["training", "course fee", "certification", "professional development"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["4.1", "4.2", "4.3"],
    },
    # ── Finance: Mobile / internet reimbursement ─────────────────────────
    {
        "keywords": ["mobile reimburs", "internet reimburs", "phone bill", "mobile bill"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["5.1", "5.2"],
    },
]


# ─────────────────────────────────────────────
# SKILL: answer_question
# ─────────────────────────────────────────────
def answer_question(question: str, index: dict) -> str:
    """
    Route the question to a single policy document via keyword matching.

    Returns a cited answer string or the verbatim REFUSAL_TEMPLATE.

    Raises:
        ValueError if index is empty or None.
    """
    if not index:
        raise ValueError("Document index is empty — call retrieve_documents first.")

    q_lower = question.lower()

    matched_route = None
    for route in ROUTES:
        if any(kw in q_lower for kw in route["keywords"]):
            matched_route = route
            break  # first (most-specific) match wins → single-source guarantee

    if matched_route is None:
        return REFUSAL_TEMPLATE

    doc = matched_route["doc"]
    sections = matched_route["sections"]

    # Collect text from matched sections in this one document only
    hits = []
    for sec in sections:
        key = (doc, sec)
        if key in index:
            text = index[key].replace("\n", " ").strip()
            # Normalise whitespace
            text = re.sub(r"\s{2,}", " ", text)
            hits.append((sec, text))

    if not hits:
        return REFUSAL_TEMPLATE

    # Build single-source answer
    lines = []
    for sec_num, sec_text in hits:
        lines.append(f"According to {doc}, Section {sec_num}: {sec_text}")

    return "\n\n".join(lines)


# ─────────────────────────────────────────────
# Interactive CLI
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  CMC Policy Q&A — Ask My Documents")
    print("  Type your question, or 'exit' / 'quit' to stop.")
    print("=" * 60)

    # Load documents once at startup
    try:
        index = retrieve_documents(POLICY_DIR, POLICY_FILES)
    except FileNotFoundError as exc:
        print(f"\n[ERROR] {exc}")
        sys.exit(1)

    print(f"\n  Loaded {len(index)} policy sections from {len(POLICY_FILES)} documents.\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(question, index)
        print(f"\n{answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
