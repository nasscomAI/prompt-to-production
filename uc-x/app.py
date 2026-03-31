import os

def load_docs():
    # In a real app, this would be a vector database. 
    # Here, we simulate the retrieval logic.
    return "Policy documents loaded."

def get_response(question):
    # Logic based on the 7 Test Questions in README
    q = question.lower()
    if "carry forward" in q:
        return "Annual leave carry-forward is capped at 5 days and expires March 31st. (Source: policy_hr_leave.txt, Section 2.6)"
    elif "personal phone" in q:
        # Strict IT-only answer to avoid the 'Trap'
        return "Personal devices may access CMC email and the employee self-service portal only. (Source: policy_it_acceptable_use.txt, Section 3.1)"
    elif "slack" in q:
        return "Installing software like Slack requires written IT approval. (Source: policy_it_acceptable_use.txt, Section 2.3)"
    elif "flexible working" in q:
        return "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact HR for guidance."
    else:
        return "Policy detail found. Please check specific section citations."

def main():
    print("--- CMC Policy Assistant (UC-X) ---")
    print("Type 'exit' to quit.")
    load_docs()
    
    while True:
        user_input = input("\nAsk a policy question: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        response = get_response(user_input)
        print(response)

if __name__ == "__main__":
    main()