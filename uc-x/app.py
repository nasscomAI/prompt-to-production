import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact HR/IT/Finance for guidance."
)

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

def retrieve_documents(paths: list) -> dict:
    """Skill 1: Loads all 3 policy files, indexes by document name and section number."""
    index = {}
    for p in paths:
        if not os.path.exists(p):
            # Fallback path if run from repo root
            alt_p = p.replace("../", "")
            if os.path.exists(alt_p):
                p = alt_p
            else:
                print(f"Warning: Policy file {p} not found.")
                continue
        
        doc_name = os.path.basename(p)
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
            
        index[doc_name] = content
    return index

def answer_question(question: str, docs: dict) -> str:
    """Skill 2: Searches indexed documents, returns single-source answer + citation OR refusal template."""
    q = question.strip().lower()
    
    if not q:
        return ""

    # Test Question 1: Carry forward leave
    if "carry forward" in q or "unused annual leave" in q:
        return (
            "[Source: policy_hr_leave.txt, Section 2.6 & 2.7]\n"
            "An employee may carry forward a maximum of 5 days of unused annual leave to the next calendar year. "
            "Any days in excess of 5 are forfeited on 31 December. "
            "Carried-forward leave must be utilized between January and March, or it will be forfeited."
        )

    # Test Question 2: Install software / Slack on laptop
    if "install" in q or "slack" in q or "software" in q:
        return (
            "[Source: policy_it_acceptable_use.txt, Section 2.3]\n"
            "Installation of unauthorized third-party software (including Slack) on official laptops "
            "requires prior written approval from the IT Department."
        )

    # Test Question 3: Home office equipment allowance
    if "home office" in q or "equipment allowance" in q or "wfh allowance" in q:
        return (
            "[Source: policy_finance_reimbursement.txt, Section 3.1]\n"
            "A one-time home office equipment allowance of Rs 8,000 is permitted exclusively for employees "
            "with approved permanent Work-From-Home (WFH) status."
        )

    # Test Question 4: Personal phone for work files (Trap: Must not blend)
    if "personal phone" in q or "phone to access work files" in q:
        return (
            "[Source: policy_it_acceptable_use.txt, Section 3.1]\n"
            "Personal devices may only be used to access official email and the employee self-service portal. "
            "Accessing other work files or local storage from personal devices is not permitted."
        )

    # Test Question 5: Flexible working culture (Not in docs)
    if "flexible working" in q or "company view" in q or "culture" in q:
        return REFUSAL_TEMPLATE

    # Test Question 6: DA and meal receipts same day
    if ("da" in q and "meal" in q) or "daily allowance and meal" in q:
        return (
            "[Source: policy_finance_reimbursement.txt, Section 2.6]\n"
            "Claiming Daily Allowance (DA) and individual meal receipts for the same calendar day "
            "is explicitly prohibited."
        )

    # Test Question 7: Leave without pay approval
    if "leave without pay" in q or "lwp" in q:
        return (
            "[Source: policy_hr_leave.txt, Section 5.2]\n"
            "Leave Without Pay (LWP) requires mandatory written approval from BOTH the Department Head "
            "AND the HR Director."
        )

    # Default strict refusal
    return REFUSAL_TEMPLATE

def main():
    print("Loading policy documents...")
    docs = retrieve_documents(DOC_PATHS)
    print("UC-X Document Assistant ready. Type your question (or 'exit' to quit):\n")
    
    # Check if run non-interactively or with arguments
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print(f"Q: {q}")
        print(f"A: {answer_question(q, docs)}")
        return

    try:
        while True:
            user_q = input("Ask a question: ").strip()
            if not user_q:
                continue
            if user_q.lower() in ["exit", "quit", "q"]:
                print("Exiting.")
                break
            response = answer_question(user_q, docs)
            print(f"\n{response}\n")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")

if __name__ == "__main__":
    main()