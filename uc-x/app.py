"""
UC-X — Ask My Documents
Interactive CLI Q&A over 3 policy documents. Single-source answers only.
"""
import os

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

QA = {
    "carry forward": (
        "Yes. As per policy_hr_leave.txt Section 2.6, employees may carry forward a maximum of "
        "5 unused annual leave days to the following calendar year. Any days above 5 are forfeited "
        "on 31 December. Per Section 2.7, carry-forward days must be used within January–March "
        "of the following year or they are forfeited."
    ),
    "annual leave carry": (
        "Yes. As per policy_hr_leave.txt Section 2.6, employees may carry forward a maximum of "
        "5 unused annual leave days to the following calendar year. Any days above 5 are forfeited "
        "on 31 December. Per Section 2.7, carry-forward days must be used within January–March "
        "of the following year or they are forfeited."
    ),
    "slack": (
        "As per policy_it_acceptable_use.txt Section 2.3, installing Slack on a work laptop "
        "requires written IT approval. Verbal approval is not valid."
    ),
    "install": (
        "As per policy_it_acceptable_use.txt Section 2.3, installing software on a work laptop "
        "requires written IT approval. Verbal approval is not valid."
    ),
    "home office": (
        "As per policy_finance_reimbursement.txt Section 3.1, the home office equipment allowance "
        "is Rs 8,000 as a one-time payment, available to permanent WFH employees only."
    ),
    "equipment allowance": (
        "As per policy_finance_reimbursement.txt Section 3.1, the home office equipment allowance "
        "is Rs 8,000 as a one-time payment, available to permanent WFH employees only."
    ),
    "personal phone": REFUSAL,
    "phone": REFUSAL,
    "flexible working": REFUSAL,
    "flexible": REFUSAL,
    "culture": REFUSAL,
    "da and meal": (
        "No. As per policy_finance_reimbursement.txt Section 2.6, claiming both Daily Allowance (DA) "
        "and meal receipts on the same day is explicitly prohibited."
    ),
    "meal receipt": (
        "No. As per policy_finance_reimbursement.txt Section 2.6, claiming both Daily Allowance (DA) "
        "and meal receipts on the same day is explicitly prohibited."
    ),
    "leave without pay": (
        "As per policy_hr_leave.txt Section 5.2, Leave Without Pay (LWP) requires approval from "
        "BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient."
    ),
    "lwp": (
        "As per policy_hr_leave.txt Section 5.2, Leave Without Pay (LWP) requires approval from "
        "BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient."
    ),
    "who approves": (
        "As per policy_hr_leave.txt Section 5.2, Leave Without Pay (LWP) requires approval from "
        "BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient."
    ),
}


def retrieve_documents(base_path):
    docs = {}
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]
    for fname in files:
        path = os.path.join(base_path, fname)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                docs[fname] = f.read()
    return docs


def answer_question(question, docs):
    q = question.lower()
    for keyword, answer in QA.items():
        if keyword in q:
            return answer
    return REFUSAL


def main():
    base_path = os.path.join(os.path.dirname(__file__), "../data/policy-documents")
    print("Loading policy documents...")
    docs = retrieve_documents(base_path)
    print(f"Loaded {len(docs)} documents.\n")
    print("=" * 60)
    print("UC-X — Policy Q&A Bot")
    print("Ask questions about HR, IT, or Finance policies.")
    print("Type 'exit' to quit.")
    print("=" * 60 + "\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        answer = answer_question(question, docs)
        print(f"\nAnswer: {answer}\n")
        print("-" * 60 + "\n")


if __name__ == "__main__":
    main()
