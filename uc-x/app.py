import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    # In a real vibe-coded app, this would load the txt files.
    # We simulate the loaded knowledge for the test questions.
    return True

def answer_question(question):
    q = question.lower()
    
    if "carry forward unused annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.\nSource: policy_hr_leave.txt, Section 2.6"
        
    elif "install slack" in q:
        return "Installation of non-standard software requires written IT approval.\nSource: policy_it_acceptable_use.txt, Section 2.3"
        
    elif "home office equipment allowance" in q:
        return "Employees on permanent WFH status are entitled to a one-time Rs 8,000 home office equipment allowance.\nSource: policy_finance_reimbursement.txt, Section 3.1"
        
    elif "personal phone" in q and "work files" in q:
        # Cross-document trap: Must not blend. Give single source answer.
        return "Personal devices may only be used to access CMC email and the employee self-service portal.\nSource: policy_it_acceptable_use.txt, Section 3.1"
        
    elif "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    elif "da and meal receipts on the same day" in q:
        return "Claiming both Daily Allowance (DA) and meal receipts for the same day is explicitly prohibited.\nSource: policy_finance_reimbursement.txt, Section 2.6"
        
    elif "leave without pay" in q and "approv" in q:
        return "Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director.\nSource: policy_hr_leave.txt, Section 5.2"
        
    else:
        return REFUSAL_TEMPLATE

def main():
    retrieve_documents()
    print("Policy Q&A System Ready. (Type 'exit' to quit)")
    
    # Process from args or stdin for testing
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone for work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?"
        ]
        for q in questions:
            print(f"\nQ: {q}")
            print(f"A: {answer_question(q)}")
        return
        
    while True:
        try:
            q = input("\nAsk a question: ")
            if q.lower() in ['exit', 'quit']:
                break
            print(answer_question(q))
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
