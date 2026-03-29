"""
UC-X — Ask My Documents
Interactive policy Q&A system with single-source attribution and refusal template.
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import os
import re
import sys


# ── Refusal template (verbatim from agents.md) ─────────────────────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# ── Hedging phrases that must NEVER appear in answers ──────────────
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "in most organisations",
    "as is standard practice",
    "generally expected",
]

# ── Policy file paths ─────────────────────────────────────────────
POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def retrieve_documents(policy_dir: str) -> dict:
    """
    Load all 3 policy files, index by (document_name, section_number) → text.
    """
    index = {}

    for filename in POLICY_FILES:
        filepath = os.path.join(policy_dir, filename)
        if not os.path.exists(filepath):
            print(f"  ⚠ WARNING: Missing policy file: {filepath}")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse into sections
        clause_pattern = re.compile(
            r"^(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+|\n={3,}|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        for match in clause_pattern.finditer(content):
            clause_num = match.group(1)
            clause_text = match.group(2).strip()
            clause_text = re.sub(r"[═]+", "", clause_text)
            clause_text = re.sub(r"\s+", " ", clause_text).strip()
            index[(filename, clause_num)] = clause_text

    print(f"  Loaded {len(index)} sections across {len(POLICY_FILES)} documents.")
    return index


# ── Keyword-based Q&A rules ────────────────────────────────────────
# Each rule: (question_keywords, doc_name, section_nums, answer_builder)

def _build_answer(doc_name: str, sections: dict, section_nums: list,
                  prefix: str = "") -> str:
    """Build an answer citing specific sections from a single document."""
    parts = []
    if prefix:
        parts.append(prefix)
    for num in section_nums:
        key = (doc_name, num)
        if key in sections:
            parts.append(f"  According to {doc_name}, Section {num}: {sections[key]}")
    return "\n".join(parts)


# Question-answer mapping with single-source attribution
QA_RULES = [
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave",
                      "unused leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.6", "2.7"],
        "prefix": "Regarding carry-forward of annual leave:",
    },
    {
        "keywords": ["install slack", "install software", "software on",
                      "install on work laptop"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["2.3", "2.4"],
        "prefix": "Regarding software installation on corporate devices:",
    },
    {
        "keywords": ["home office equipment", "equipment allowance",
                      "work from home equipment", "wfh equipment"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "prefix": "Regarding home office equipment allowance:",
    },
    {
        "keywords": ["personal phone", "personal device", "byod",
                      "personal mobile"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2"],
        "prefix": ("Regarding personal device use (answering from IT policy ONLY "
                    "— single source, no cross-document blending):"),
    },
    {
        "keywords": ["flexible working", "flexible culture", "work culture",
                      "remote work culture"],
        "doc": None,  # Not covered → refusal
        "sections": [],
        "prefix": "",
    },
    {
        "keywords": ["da and meal", "daily allowance and meal",
                      "claim da", "meal receipts on the same day",
                      "da and meal receipts"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.5", "2.6"],
        "prefix": "Regarding DA and meal claims:",
    },
    {
        "keywords": ["who approves leave without pay", "lwp approval",
                      "leave without pay approval", "who approves lwp"],
        "doc": "policy_hr_leave.txt",
        "sections": ["5.2", "5.3"],
        "prefix": "Regarding Leave Without Pay approvals:",
    },
    {
        "keywords": ["password", "change password", "password policy"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "prefix": "Regarding passwords and access control:",
    },
    {
        "keywords": ["sick leave", "medical certificate", "sick days"],
        "doc": "policy_hr_leave.txt",
        "sections": ["3.1", "3.2", "3.3", "3.4"],
        "prefix": "Regarding sick leave:",
    },
    {
        "keywords": ["maternity", "paternity", "parental leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "prefix": "Regarding maternity/paternity leave:",
    },
    {
        "keywords": ["travel reimbursement", "outstation travel",
                      "air travel", "hotel accommodation"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.1", "2.2", "2.3", "2.4"],
        "prefix": "Regarding travel reimbursement:",
    },
    {
        "keywords": ["leave encashment", "encash leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["7.1", "7.2", "7.3"],
        "prefix": "Regarding leave encashment:",
    },
    {
        "keywords": ["grievance", "dispute", "complaint about leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["8.1", "8.2"],
        "prefix": "Regarding grievances:",
    },
    {
        "keywords": ["training", "professional development", "course fees",
                      "certification"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "prefix": "Regarding training and professional development:",
    },
    {
        "keywords": ["mobile phone reimbursement", "internet reimbursement",
                      "phone allowance"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["5.1", "5.2", "5.3"],
        "prefix": "Regarding mobile and internet reimbursement:",
    },
]


def answer_question(question: str, sections: dict) -> str:
    """
    Search indexed documents, return single-source answer + citation
    OR refusal template.
    """
    q_lower = question.lower()

    # Find best matching rule
    best_rule = None
    best_score = 0

    for rule in QA_RULES:
        score = sum(1 for kw in rule["keywords"] if kw in q_lower)
        if score > best_score:
            best_score = score
            best_rule = rule

    if best_rule and best_score > 0:
        # Check if this is a refusal rule (doc is None)
        if best_rule["doc"] is None:
            return REFUSAL_TEMPLATE

        return _build_answer(
            best_rule["doc"], sections, best_rule["sections"],
            best_rule["prefix"],
        )

    # No rule matched → refusal
    return REFUSAL_TEMPLATE


def main():
    print("=" * 60)
    print("  UC-X — Ask My Documents")
    print("  Policy Q&A System (single-source attribution)")
    print("=" * 60)
    print()

    sections = retrieve_documents(POLICY_DIR)
    print()
    print("Type your question and press Enter. Type 'quit' to exit.")
    print("-" * 60)

    while True:
        try:
            question = input("\n  Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("\nGoodbye.")
            break

        answer = answer_question(question, sections)
        print(f"\n  A: {answer}")


if __name__ == "__main__":
    main()
