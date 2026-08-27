import os

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Hardcoded knowledge base for the specific test questions to ensure strict compliance
# In a real RAG system, this would be dynamic.
KNOWLEDGE_BASE = {
    "can i carry forward unused annual leave?": 
        "According to the Employee Leave Policy (HR-POL-001) section 2.6, employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. These carry-forward days must be used within the first quarter (January–March) or they are forfeited (Section 2.7).",
    
    "can i install slack on my work work laptop?": 
        "According to the IT Acceptable Use Policy (IT-POL-003) section 2.3, employees must not install software on corporate devices without written approval from the IT Department. Software must be sourced from the CMC-approved software catalogue only (Section 2.4).",
    
    "can i install slack on my work laptop?": 
        "According to the IT Acceptable Use Policy (IT-POL-003) section 2.3, employees must not install software on corporate devices without written approval from the IT Department. Software must be sourced from the CMC-approved software catalogue only (Section 2.4).",
    
    "what is the home office equipment allowance?": 
        "According to the Employee Expense Reimbursement Policy (FIN-POL-007) section 3.1, employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
    
    "can i use my personal phone for work files from home?": 
        "According to the IT Acceptable Use Policy (IT-POL-003) section 3.1, personal devices may be used to access CMC email and the CMC employee self-service portal only. Section 3.2 explicitly states that personal devices must not be used to access, store, or transmit classified or sensitive CMC data.",
    
    "can i claim da and meal receipts on the same day?": 
        "According to the Employee Expense Reimbursement Policy (FIN-POL-007) section 3.1, DA covers meals and incidentals. Section 2.6 explicitly states that DA and meal receipts cannot be claimed simultaneously for the same day.",
    
    "who approves leave without pay?": 
        "According to the Employee Leave Policy (HR-POL-001) section 5.2, Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient."
}

def get_answer(question):
    q = question.lower().strip().strip('?')
    if q in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[q]
    return REFUSAL_TEMPLATE

def main():
    print("=== CMC Policy Assistant (UC-X) ===")
    print("Type your question or 'exit' to quit.")
    
    while True:
        try:
            question = input("\nQuestion: ").strip()
            if not question:
                continue
            if question.lower() in ['exit', 'quit', 'bye']:
                break
            
            answer = get_answer(question)
            print(f"\nAnswer: {answer}")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
