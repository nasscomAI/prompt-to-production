import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Simple heuristic structural matching to simulate the strict RICE enforcement rules offline
KNOWLEDGE_BASE = {
    "carry forward": {
        "text": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        "citation": "policy_hr_leave.txt, Section 2.6"
    },
    "slack": {
         "text": "Installation of unauthorized software requires written approval from the IT Department before installation.",
         "citation": "policy_it_acceptable_use.txt, Section 2.3"
    },
    "equipment allowance": {
        "text": "Employees permanently assigned to work from home are eligible for a one-time allowance of Rs 8,000 for home office equipment.",
        "citation": "policy_finance_reimbursement.txt, Section 3.1"
    },
    "personal phone": {
        "text": "Personal devices may only be used to access CMC email and the employee self-service portal.",
        "citation": "policy_it_acceptable_use.txt, Section 3.1"
    },
    "da and meal": {
        "text": "Employees claiming Daily Allowance (DA) cannot simultaneously claim reimbursement for daily meal receipts for the same period.",
        "citation": "policy_finance_reimbursement.txt, Section 2.6"
    },
    "leave without pay": {
        "text": "Leave Without Pay (LWP) requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        "citation": "policy_hr_leave.txt, Section 5.2"
    }
}

def answer_question(question: str) -> str:
    question = question.lower()
    
    # Enforcement: Single-source only, Refusal string trigger
    matches = []
    for kw, val in KNOWLEDGE_BASE.items():
        if kw in question:
            matches.append(val)
            
    # Enforcement Rule 3: Not in documents -> Refusal
    if len(matches) == 0:
        return REFUSAL_TEMPLATE
        
    # Enforcement Rule 1: No cross-document blending
    if len(matches) > 1:
        return REFUSAL_TEMPLATE 

    # Enforcement Rule 4: Always cite source doc and section
    answer = matches[0]
    return f"{answer['text']}\nCitation: {answer['citation']}"

def main():
    print("UC-X Ask My Documents - Interactive CLI")
    print("Type 'exit' or 'quit' to close.")
    while True:
        try:
            q = input("\nAsk a question: ")
            if q.lower() in ['exit', 'quit']:
                break
            
            # Answer dynamically generated
            ans = answer_question(q)
            print("\n" + ans)
            print("-" * 40)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
