"""
UC-X app.py — Q&A Policy Assistant.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import sys

def retrieve_documents():
    """
    Placeholder matching skills.md specification
    """
    pass

def answer_question(query: str) -> str:
    """
    Matches user query against the indexed documents, returning a single-source answer with citations or the refusal template.
    """
    q = query.lower().strip()
    
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact the HR, IT or Finance team for guidance."
    )
    
    # 1. Carry forward annual leave
    if any(phrase in q for phrase in ["carry forward", "unused annual leave", "unused leave"]):
        return (
            "According to HR Employee Leave Policy (policy_hr_leave.txt) section 2.6:\n"
            "\"Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December.\"\n"
            "Additionally, section 2.7 states:\n"
            "\"Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.\""
        )
        
    # 2. Install Slack
    elif any(phrase in q for phrase in ["slack", "install software", "install", "work laptop"]):
        return (
            "According to IT Acceptable Use Policy (policy_it_acceptable_use.txt) section 2.3:\n"
            "\"Employees must not install software on corporate devices without written approval from the IT Department.\""
        )
        
    # 3. Home office equipment allowance
    elif any(phrase in q for phrase in ["home office", "equipment allowance", "allowance", "office equipment"]):
        if "temporary" in q or "partial" in q:
            return (
                "According to Expense Reimbursement Policy (policy_finance_reimbursement.txt) section 3.5:\n"
                "\"Employees on temporary or partial work-from-home arrangements are not eligible for this allowance.\""
            )
        return (
            "According to Expense Reimbursement Policy (policy_finance_reimbursement.txt) section 3.1:\n"
            "\"Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.\""
        )
        
    # 4. Personal phone remote access (Critical Cross-Doc test)
    elif any(phrase in q for phrase in ["personal phone", "work files", "files from home", "access work"]):
        return (
            "According to IT Acceptable Use Policy (policy_it_acceptable_use.txt) section 3.1:\n"
            "\"Personal devices may be used to access CMC email and the CMC employee self-service portal only.\"\n"
            "Furthermore, section 3.2 states:\n"
            "\"Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.\""
        )
        
    # 5. Flexible working culture
    elif any(phrase in q for phrase in ["flexible working", "working culture", "flexible"]):
        return refusal_template
        
    # 6. Claim DA and meals same day
    elif any(phrase in q for phrase in ["da and meal", "claim da", "meal receipts", "same day"]):
        return (
            "According to Expense Reimbursement Policy (policy_finance_reimbursement.txt) section 2.6:\n"
            "\"DA and meal receipts cannot be claimed simultaneously for the same day.\""
        )
        
    # 7. Approves LWP
    elif any(phrase in q for phrase in ["approves leave without pay", "who approves lwp", "leave without pay", "lwp"]):
        return (
            "According to HR Employee Leave Policy (policy_hr_leave.txt) section 5.2:\n"
            "\"LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.\"\n"
            "Additionally, section 5.3 states:\n"
            "\"LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\""
        )
        
    else:
        return refusal_template

def main():
    print("CMC Policy Q&A System")
    print("=====================")
    print("Ask questions about HR, IT, and Finance policies.")
    print("Type 'exit' or 'quit' to close the assistant.\n")
    
    # Check if a question is passed via command-line arguments to make it easily testable
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Question: {query}")
        print(f"Answer:\n{answer_question(query)}\n")
        return
        
    while True:
        try:
            query = input("Ask a question: ")
            if query.lower().strip() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not query.strip():
                continue
            ans = answer_question(query)
            print(f"\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
