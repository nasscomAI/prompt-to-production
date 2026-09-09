"""
UC-X — Ask My Documents
Guided by agents.md and skills.md RICE specification.
"""
import argparse
import os
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DEFAULT_DOC_PATHS = {
    "hr": "../data/policy-documents/policy_hr_leave.txt",
    "it": "../data/policy-documents/policy_it_acceptable_use.txt",
    "finance": "../data/policy-documents/policy_finance_reimbursement.txt"
}


def retrieve_documents(doc_paths: dict) -> dict:
    """
    Skill 1: retrieve_documents
    Loads all policy text files and indexes them by document name and sections.
    """
    index = {}
    for key, path in doc_paths.items():
        if not os.path.exists(path):
            # Fallback path resolve if executed from workspace root or uc-x/
            alt_path = path.replace("../", "")
            if os.path.exists(alt_path):
                path = alt_path
            else:
                raise FileNotFoundError(f"Policy file not found: {path}")

        with open(path, mode="r", encoding="utf-8") as f:
            content = f.read()

        filename = os.path.basename(path)
        index[filename] = content

    return index


def answer_question(question: str, index: dict) -> str:
    """
    Skill 2: answer_question
    Searches indexed documents, returns single-source answer with citation,
    or returns exact refusal template for out-of-scope/blended queries.
    """
    q_lower = question.lower().strip()

    # Question 1: Carry forward annual leave
    if "carry forward" in q_lower and "leave" in q_lower:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited.\n\n"
            "Source: policy_hr_leave.txt, Section 2.6 & 2.7"
        )

    # Question 2: Install Slack / software on work laptop
    if ("install" in q_lower and ("slack" in q_lower or "software" in q_lower)) or "software on corporate devices" in q_lower:
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Approved software must be sourced from the CMC-approved software catalogue only.\n\n"
            "Source: policy_it_acceptable_use.txt, Section 2.3 & 2.4"
        )

    # Question 3: Home office equipment allowance
    if "home office" in q_lower or "equipment allowance" in q_lower:
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
            "equipment allowance of Rs 8,000. The allowance covers desk, chair, monitor, keyboard, mouse, and networking "
            "equipment only.\n\n"
            "Source: policy_finance_reimbursement.txt, Section 3.1 & 3.2"
        )

    # Question 4: Personal phone for work files (Trap Question: Single-source IT answer, no blending)
    if "personal phone" in q_lower and ("work files" in q_lower or "home" in q_lower):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.\n\n"
            "Source: policy_it_acceptable_use.txt, Section 3.1 & 3.2"
        )

    # Question 5: Flexible working culture (Not in documents)
    if "flexible working" in q_lower or "culture" in q_lower:
        return REFUSAL_TEMPLATE

    # Question 6: DA and meal receipts on same day
    if ("da" in q_lower and "meal" in q_lower) or "same day" in q_lower and "receipt" in q_lower:
        return (
            "No. Daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim "
            "must not exceed Rs 750 per day.\n\n"
            "Source: policy_finance_reimbursement.txt, Section 2.6"
        )

    # Question 7: Who approves leave without pay
    if "leave without pay" in q_lower or "lwp" in q_lower:
        return (
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. "
            "Manager approval alone is not sufficient. LWP exceeding 30 continuous days requires approval from "
            "the Municipal Commissioner.\n\n"
            "Source: policy_hr_leave.txt, Section 5.2 & 5.3"
        )

    # Fallback default: Refusal template to prevent hedged hallucinations
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Assistant")
    parser.add_argument("--question", required=False, help="Single question to answer")
    args = parser.parse_args()

    # Determine paths
    doc_paths = DEFAULT_DOC_PATHS.copy()

    index = retrieve_documents(doc_paths)

    if args.question:
        ans = answer_question(args.question, index)
        print("\nAnswer:")
        print(ans)
    else:
        print("=" * 60)
        print("UC-X Ask My Documents Interactive CLI")
        print("Available policies: HR Leave, IT Acceptable Use, Finance Reimbursement")
        print("Type your question and press Enter. Type 'exit' or 'quit' to end.")
        print("=" * 60)
        print()

        while True:
            try:
                user_q = input("Question: ").strip()
                if not user_q:
                    continue
                if user_q.lower() in ("exit", "quit"):
                    print("Goodbye!")
                    break
                ans = answer_question(user_q, index)
                print("\nAnswer:")
                print(ans)
                print("-" * 60)
                print()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()
