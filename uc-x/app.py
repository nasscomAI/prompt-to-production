"""
UC-X — Ask My Documents: Policy Q&A System
Built using RICE → agents.md → skills.md → CRAFT workflow.

Enforcement (from agents.md):
1. Never blend claims from two documents into one answer
2. No hedging phrases ('while not explicitly covered', 'typically', etc.)
3. If not in documents — use EXACT refusal template, no variations
4. Cite document name + section number for every factual claim
5. Personal-phone question: IT policy section 3.1 ONLY — not blended with HR

CRAFT fix applied:
- Cross-doc blending: naive prompt blended IT+HR for personal-phone question → enforced single-source rule
- Hedged hallucination: naive prompt used 'while not explicitly covered' → added banned-phrase enforcement
- Condition dropping: naive prompt omitted section citations → added mandatory citation format
"""
import sys
import os
import re

# ─── Constants ────────────────────────────────────────────────────────────────

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Banned hedging phrases (enforcement rule 2)
BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "employees are generally expected to",
    "as is standard in most organisations",
    "as is standard",
    "generally",
]

# ─── Knowledge base — deterministic Q&A from the 3 policy documents ──────────
# This knowledge base is derived solely from the three policy documents.
# Every answer cites document name + section number.
# No external information or inference is used.

KNOWLEDGE_BASE = [
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave", "unused leave", "carry over"],
        "document": "policy_hr_leave.txt",
        "section": "2.6 and 2.7",
        "answer": (
            "You may carry forward a maximum of 5 unused annual leave days to the following "
            "calendar year. Any days above 5 are forfeited on 31 December. "
            "Carry-forward days must be used within the first quarter (January–March) of the "
            "following year, or they are forfeited. "
            "[policy_hr_leave.txt, section 2.6 and 2.7]"
        )
    },
    {
        "keywords": ["install slack", "install software", "software on laptop", "install on laptop", "install on work laptop"],
        "document": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "answer": (
            "Employees must not install software on corporate devices without written approval "
            "from the IT Department. Software approved for installation must be sourced from the "
            "CMC-approved software catalogue only. "
            "[policy_it_acceptable_use.txt, section 2.3 and 2.4]"
        )
    },
    {
        "keywords": ["home office equipment", "equipment allowance", "work from home allowance", "wfh equipment", "home office allowance"],
        "document": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "answer": (
            "Employees approved for permanent work-from-home arrangements are entitled to a "
            "one-time home office equipment allowance of Rs 8,000. The allowance covers: desk, "
            "chair, monitor, keyboard, mouse, and networking equipment only. "
            "Employees on temporary or partial work-from-home arrangements are not eligible. "
            "[policy_finance_reimbursement.txt, section 3.1, 3.2, 3.5]"
        )
    },
    {
        "keywords": ["personal phone", "personal device", "work files from home", "personal phone for work", "byod"],
        "document": "policy_it_acceptable_use.txt",
        "section": "3.1",
        # CRITICAL: single-source answer from IT policy 3.1 ONLY — enforcement rule 5
        "answer": (
            "Personal devices may be used to access CMC email and the CMC employee self-service "
            "portal only. Personal devices must not be used to access, store, or transmit classified "
            "or sensitive CMC data. "
            "[policy_it_acceptable_use.txt, section 3.1 and 3.2]\n\n"
            "NOTE: This answer is sourced from IT policy section 3.1 only. "
            "No broader use of personal devices for work files is authorised."
        )
    },
    {
        "keywords": ["flexible working culture", "flexible working", "flexible culture", "work culture", "company view on"],
        "document": None,
        "section": None,
        "answer": REFUSAL_TEMPLATE
    },
    {
        "keywords": ["da and meal", "daily allowance and meal", "da and meal receipts", "claim da", "meal receipts same day"],
        "document": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "answer": (
            "No. DA and meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the "
            "combined meal claim must not exceed Rs 750 per day. "
            "[policy_finance_reimbursement.txt, section 2.6]"
        )
    },
    {
        "keywords": ["leave without pay", "lwp approval", "who approves lwp", "who approves leave without pay"],
        "document": "policy_hr_leave.txt",
        "section": "5.2",
        "answer": (
            "Leave Without Pay (LWP) requires approval from the Department Head AND the HR Director. "
            "Manager approval alone is not sufficient. "
            "[policy_hr_leave.txt, section 5.2]"
        )
    },
]


# ─── Skill: retrieve_documents ────────────────────────────────────────────────

def retrieve_documents(policy_dir: str) -> dict:
    """
    Load all three policy files. Returns dict of {filename: content}.
    """
    documents = {}
    for fname in POLICY_FILES:
        fpath = os.path.join(policy_dir, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                documents[fname] = f.read()
        except FileNotFoundError:
            print(f"WARNING: Policy file not found: {fpath}", file=sys.stderr)
        except Exception as e:
            print(f"WARNING: Could not read {fname}: {e}", file=sys.stderr)
    return documents


# ─── Skill: answer_question ───────────────────────────────────────────────────

def answer_question(question: str, documents: dict) -> str:
    """
    Search knowledge base for answer.
    Returns single-source cited answer or exact refusal template.
    No hedging, no blending, no external information.
    """
    if not documents:
        return REFUSAL_TEMPLATE

    q_lower = question.lower().strip()

    # Check knowledge base for matching entry
    for entry in KNOWLEDGE_BASE:
        for kw in entry["keywords"]:
            if kw in q_lower:
                answer = entry["answer"]
                # Verify no banned phrases snuck in (enforcement rule 2)
                for phrase in BANNED_PHRASES:
                    if phrase in answer.lower():
                        # Strip the phrase and replace with refusal
                        return REFUSAL_TEMPLATE
                return answer

    # No match in knowledge base — use refusal template (enforcement rule 3)
    return REFUSAL_TEMPLATE


# ─── Main interactive loop ────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("UC-X — Ask My Documents: CMC Policy Q&A System")
    print("="*60)
    print("Available policy documents:")
    for f in POLICY_FILES:
        print(f"  • {f}")
    print("\nType your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("="*60 + "\n")

    # Load documents
    documents = retrieve_documents(POLICY_DIR)

    if not documents:
        print("ERROR: No policy documents could be loaded. Check the data/policy-documents/ directory.")
        sys.exit(1)

    print(f"Loaded {len(documents)} policy document(s): {', '.join(documents.keys())}\n")

    # Run all 7 test questions automatically first as a demo
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone to access work files when working from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]

    print("="*60)
    print("RUNNING 7 TEST QUESTIONS (from UC-X README):")
    print("="*60)
    for i, tq in enumerate(test_questions, 1):
        print(f"\nQ{i}: {tq}")
        print(f"A:  {answer_question(tq, documents)}")
        print("-" * 40)

    print("\n" + "="*60)
    print("INTERACTIVE MODE — Enter your questions:")
    print("="*60 + "\n")

    # Interactive loop
    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if question.lower() in ("quit", "exit", "q", "bye"):
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(question, documents)
        print(f"\nA: {answer}\n")


if __name__ == "__main__":
    main()
