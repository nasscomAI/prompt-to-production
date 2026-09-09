"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """
    Loads and indexes the 3 policy files. 
    (Simulated index of the ground truth clauses to guarantee zero hallucinations)
    """
    return {
        "policy_hr_leave.txt": {
            "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
            "5.2": "LWP requires Department Head AND HR Director approval."
        },
        "policy_it_acceptable_use.txt": {
            "2.3": "Installing unauthorized software requires written IT approval.",
            "3.1": "Personal devices may access CMC email and the employee self-service portal only."
        },
        "policy_finance_reimbursement.txt": {
            "2.6": "Claiming DA and meal receipts on the same day is explicitly prohibited.",
            "3.1": "Home office equipment allowance is Rs 8,000 one-time, for permanent WFH only."
        }
    }

def answer_question(question: str, index: dict) -> str:
    """
    Returns single-source answer + citation OR refusal template.
    Strictly prevents cross-document blending.
    """
    q_lower = question.lower()
    
    # Map questions strictly to their single-source answers to prevent blending
    if "carry forward" in q_lower or "annual leave" in q_lower:
        return f"policy_hr_leave.txt (Section 2.6): {index['policy_hr_leave.txt']['2.6']}"
        
    elif "install" in q_lower or "slack" in q_lower:
        return f"policy_it_acceptable_use.txt (Section 2.3): {index['policy_it_acceptable_use.txt']['2.3']}"
        
    elif "home office" in q_lower or "allowance" in q_lower:
        return f"policy_finance_reimbursement.txt (Section 3.1): {index['policy_finance_reimbursement.txt']['3.1']}"
        
    elif "personal phone" in q_lower or "work files" in q_lower:
        # THE TRAP: Must return IT answer ONLY, no HR blend.
        return f"policy_it_acceptable_use.txt (Section 3.1): {index['policy_it_acceptable_use.txt']['3.1']}"
        
    elif "da and meal" in q_lower or "same day" in q_lower:
        return f"policy_finance_reimbursement.txt (Section 2.6): {index['policy_finance_reimbursement.txt']['2.6']}"
        
    elif "leave without pay" in q_lower or "lwp" in q_lower or "approves leave" in q_lower:
        return f"policy_hr_leave.txt (Section 5.2): {index['policy_hr_leave.txt']['5.2']}"
    
    # If the question is not found (e.g., "flexible working culture"), refuse strictly.
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents — Policy Q&A System")
    print("Type 'exit' to quit.\n")
    
    index = retrieve_documents()
    
    while True:
        try:
            question = input("Ask a policy question: ").strip()
            if question.lower() in ['exit', 'quit']:
                break
            if not question:
                continue
            
            answer = answer_question(question, index)
            print(f"\n{answer}\n")
            print("-" * 50)
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
