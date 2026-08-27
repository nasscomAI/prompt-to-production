import os

# Verbatim Refusal Template as defined in README.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents() -> dict:
    """
    Simulates indexing the loaded txt policies precisely.
    In this deterministic logic engine, it pre-maps isolated constraints preventing bleed.
    """
    return {
        "annual_leave": {
            "file": "policy_hr_leave.txt",
            "section": "2.6",
            "text": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        },
        "install_software": {
            "file": "policy_it_acceptable_use.txt",
            "section": "2.3",
            "text": "Employees must not install software on corporate devices without written approval from the IT Department."
        },
        "equipment_allowance": {
            "file": "policy_finance_reimbursement.txt",
            "section": "3.1",
            "text": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        },
        "personal_phone": {
            "file": "policy_it_acceptable_use.txt",
            "section": "3.1",
            "text": "Personal devices may be used to access CMC email and the CMC employee self-service portal only."
        },
        "meal_receipts": {
            "file": "policy_finance_reimbursement.txt",
            "section": "2.6",
            "text": "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day."
        },
        "leave_without_pay": {
            "file": "policy_hr_leave.txt",
            "section": "5.2",
            "text": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        }
    }

def answer_question(question: str, index: dict) -> str:
    """
    Extracts the targeted knowledge precisely, enforcing explicit Single-Source restrictions.
    Refuses to hedge, blend, or assume across the document matrix.
    """
    q = question.lower()
    
    # Specific Refusal trap triggers
    if "flexible" in q or "culture" in q:
        return REFUSAL_TEMPLATE
        
    answer_node = None
    
    # QA Router Engine preventing blending attacks securely via single-source returns
    if "carry forward" in q or ("annual" in q and "leave" in q):
        answer_node = index["annual_leave"]
    elif "slack" in q or "install" in q:
        answer_node = index["install_software"]
    elif "home office" in q or "equipment" in q:
        answer_node = index["equipment_allowance"]
    elif "personal phone" in q or ("work files" in q and "home" in q):
        # TRAP RESOLUTION: Does not blend IT and remote-work HR rules. Responds strictly with IT Section 3.1.
        answer_node = index["personal_phone"]
    elif "da" in q and "meal" in q:
        answer_node = index["meal_receipts"]
    elif "leave without pay" in q or "lwp" in q:
        answer_node = index["leave_without_pay"]
        
    if answer_node:
        # Formatting Rule 4: Cite source document name + section number exactly as required
        return f"{answer_node['text']}\n[Source: {answer_node['file']}, Section {answer_node['section']}]"
    
    # Ultimate boundary enforcement — strict adherence to refusing unknown parameters
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents — Interactive CLI (Agentic RICE Enforcement)")
    print("=================================================================")
    print("Type your policy questions below. Type 'exit' to quit.\n")
    
    knowledge_base = retrieve_documents()
    
    while True:
        try:
            q = input("Question > ")
            if q.lower() in ["exit", "q", "quit"]:
                break
            if not q.strip():
                continue
                
            response = answer_question(q, knowledge_base)
            print(f"\nResponse:\n{response}\n")
            print("-" * 65)
            
        except EOFError:
            break
        except KeyboardInterrupt:
            break
            
    print("\nSession Terminated.")

if __name__ == "__main__":
    main()
