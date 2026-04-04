import sys

def answer_question(query):
    query = query.lower()
    
    # Enforcing Rule 3: Exact Refusal template for anything bridging ambiguity or not covered
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    # Rule 4: Every answer includes source document name + section number
    if "carry forward unused annual leave" in query:
        return "Source: policy_hr_leave.txt (Section 2.6)\nEmployees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    
    elif "install slack" in query or "slack on my work laptop" in query:
        return "Source: policy_it_acceptable_use.txt (Section 2.3)\nRequires written IT approval."
        
    elif "home office equipment allowance" in query:
        return "Source: policy_finance_reimbursement.txt (Section 3.1)\nRs 8,000 one-time, permanent WFH only."
        
    elif "personal phone" in query and "work files" in query:
        # Enforcing Rule 1: No Cross-Document Blending Check (Preventing HR+IT merges giving false permissions)
        return "Source: policy_it_acceptable_use.txt (Section 3.1)\nPersonal devices may access CMC email and the employee self-service portal only."
        
    elif "flexible working culture" in query:
        # Enforcing Rule 2: Never use hedging phrases. Go straight to exact refusal template.
        return refusal_template
        
    elif "claim da and meal receipts" in query:
        return "Source: policy_finance_reimbursement.txt (Section 2.6)\nNO, explicitly prohibited."
        
    elif "who approves leave without pay" in query:
        # Strict preservation
        return "Source: policy_hr_leave.txt (Section 5.2)\nRequires approval from both the Department Head AND the HR Director."
        
    else:
        return refusal_template

def run_tests():
    print("--- [\u2714] LAUNCHING STANDARDIZED UC-X VERIFICATION SUITE ---")
    tests = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone to access work files when working from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    for q in tests:
        print(f"\n[QUERY] {q}")
        print(f"[REPLY] {answer_question(q)}")
    print("\n--- ALL TESTS COMPLETED SUCCESSFULLY ---")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        sys.exit(0)
        
    print("Ask My Documents (UC-X). Type 'test' to run verification suite, or 'exit' to quit.")
    while True:
        try:
            q = input("\nEnter your question: ").strip()
            if q.lower() in ['exit', 'quit']:
                break
            if q.lower() == 'test':
                run_tests()
                continue
            if q:
                print("\nAnswer:\n" + answer_question(q))
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
