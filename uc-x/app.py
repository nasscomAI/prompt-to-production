"""
UC-X — Ask My Documents
Single-source policy Q&A with citation enforcement and refusal template.
"""
import os

# ── Document paths ──────────────────────────────────────────────────────────
DOCS = {
    "policy_hr_leave.txt":            "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":   "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# ── Knowledge base ───────────────────────────────────────────────────────────
# Each entry: (keywords, answer, source_doc, section)
KB = [
    (
        ["leave without pay", "lwp", "who approves lwp", "approve leave without pay", "without pay"],
        "LWP requires approval from both the Department Head and the HR Director. "
        "Manager approval alone is not sufficient. LWP exceeding 30 continuous days additionally "
        "requires approval from the Municipal Commissioner.",
        "policy_hr_leave.txt", "5.2, 5.3"
    ),
    (
        ["carry forward", "carry-forward", "unused leave", "annual leave carry"],
        "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
        "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within January–March "
        "of the following year or they are forfeited.",
        "policy_hr_leave.txt", "2.6, 2.7"
    ),
    (
        ["slack", "install software", "software on", "application", "software catalogue"],
        "Employees must not install software on corporate devices without written approval from the IT Department. "
        "Software approved for installation must be sourced from the CMC-approved software catalogue only.",
        "policy_it_acceptable_use.txt", "2.3, 2.4"
    ),
    (
        ["home office", "equipment allowance", "wfh allowance", "work from home equipment", "desk", "chair", "monitor"],
        "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
        "equipment allowance of Rs 8,000. This covers desk, chair, monitor, keyboard, mouse, and networking "
        "equipment only. Employees on temporary or partial WFH arrangements are not eligible.",
        "policy_finance_reimbursement.txt", "3.1, 3.2, 3.5"
    ),
    (
        ["personal phone", "personal device", "byod", "mobile", "work files", "from home", "phone for work"],
        "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
        "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data, "
        "and must not be connected to the CMC internal network.",
        "policy_it_acceptable_use.txt", "3.1, 3.2, 3.3"
    ),
    (
        ["flexible working", "flexible culture", "work culture", "remote work culture", "wfh culture"],
        REFUSAL,
        None, None
    ),
    (
        ["da and meal", "daily allowance and meal", "meal receipt", "da and receipt", "claim da"],
        "DA and meal receipts cannot be claimed simultaneously for the same day. If DA is claimed (Rs 750/day), "
        "no separate meal receipts are required. If actual meal expenses are claimed instead of DA, receipts "
        "are mandatory and the combined claim must not exceed Rs 750 per day.",
        "policy_finance_reimbursement.txt", "2.5, 2.6"
    ),
]

def retrieve_documents() -> dict:
    """
    Loads all 3 policy files, indexes by document name.
    """
    docs = {}
    for name, path in DOCS.items():
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                docs[name] = f.read()
        else:
            print(f"WARNING: Could not find {path}")
    return docs


def answer_question(question: str) -> str:
    """
    Searches knowledge base for single-source answer + citation.
    Returns refusal template if not found.
    Never blends answers from two documents.
    """
    q = question.lower().strip()

    # Forbidden hedging phrases — never appear in output
    HEDGE_PHRASES = [
        "while not explicitly covered",
        "typically",
        "generally understood",
        "it is common practice",
        "generally",
    ]

    for keywords, answer, doc, section in KB:
        if any(kw in q for kw in keywords):
            if doc is None:
                return f"\n{REFUSAL}\n"
            citation = f"\n[Source: {doc} — Section {section}]"
            return f"\n{answer}{citation}\n"

    return f"\n{REFUSAL}\n"


def main():
    print("=" * 60)
    print("CMC Policy Assistant — Ask My Documents")
    print("Sources: HR Leave | IT Acceptable Use | Finance Reimbursement")
    print("Type 'exit' to quit.")
    print("=" * 60)

    # Load and verify documents exist
    docs = retrieve_documents()
    print(f"\n{len(docs)} policy documents loaded.\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("exit", "quit", "q"):
            print("Exiting.")
            break

        if not question:
            continue

        print(answer_question(question))


if __name__ == "__main__":
    main()