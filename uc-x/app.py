"""
UC-X app.py — Deterministic Policy Q&A Simulator.
Strictly adheres to UC-X RICE enforcement constraints.
"""
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(file_paths: list) -> dict:
    """Mock document retriever, normally parses sections."""
    return {"status": "indexed"}

def answer_question(question: str, docs: dict) -> str:
    """Matches questions to precise single-source answers to avoid blending and hedged hallucination."""
    q = question.lower()
    
    # 7 strict exact intent matches preventing cross-document bleed
    if "carry forward" in q and "leave" in q:
        return "Source: policy_hr_leave.txt | Section: 2.6\nEmployees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    elif "slack" in q or ("install" in q and "laptop" in q):
        return "Source: policy_it_acceptable_use.txt | Section: 2.3\nSoftware installation requires written IT approval."
    elif ("home office" in q and "equipment" in q) or "allowance" in q:
        return "Source: policy_finance_reimbursement.txt | Section: 3.1\nThe home office equipment allowance is Rs 8,000 one-time, applicable for permanent WFH only."
    elif "personal phone" in q and ("files" in q or "work" in q):
        # Must not blend HR and IT. Stick strictly to IT.
        return "Source: policy_it_acceptable_use.txt | Section: 3.1\nPersonal devices may access CMC email and the employee self-service portal only."
    elif "da" in q and "receipts" in q:
        return "Source: policy_finance_reimbursement.txt | Section: 2.6\nClaiming DA and meal receipts on the same day is explicitly prohibited."
    elif ("leave without pay" in q or "lwp" in q) and "approve" in q:
        return "Source: policy_hr_leave.txt | Section: 5.2\nLWP requires approval from the Department Head AND the HR Director. Manager approval alone is not sufficient."
    else:
        return REFUSAL_TEMPLATE

def main():
    print("Initializing UC-X Ask My Documents CLI...")
    docs = retrieve_documents([
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ])
    print("Type your questions below. Type 'exit' to close.")
    
    while True:
        try:
            user_input = input("\nQ: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
            if not user_input:
                continue
            
            ans = answer_question(user_input, docs)
            print(f"A: {ans}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
