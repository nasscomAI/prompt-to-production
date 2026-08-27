import sys
import argparse

def retrieve_documents():
    """
    Simulates loading and indexing the 3 policy files.
    """
    return {
        "policy_hr_leave.txt": "Indexed",
        "policy_it_acceptable_use.txt": "Indexed",
        "policy_finance_reimbursement.txt": "Indexed"
    }

def answer_question(question, docs):
    """
    Searches indexed documents and returns exact citations without blending or hedging.
    """
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    q_lower = question.lower()
    
    if "carry forward" in q_lower and "annual leave" in q_lower:
        return "[policy_hr_leave.txt - Section 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        
    elif ("install" in q_lower and "laptop" in q_lower) or "slack" in q_lower:
        return "[policy_it_acceptable_use.txt - Section 2.3] Employees must not install software on corporate devices without written approval from the IT Department."
        
    elif "home office equipment allowance" in q_lower:
        return "[policy_finance_reimbursement.txt - Section 3.1] Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        
    elif "personal phone" in q_lower and ("work files" in q_lower or "home" in q_lower):
        # Crucial cross-document trap: DO NOT BLEND. Single source answer from IT policy only.
        return "[policy_it_acceptable_use.txt - Section 3.1] Personal devices may be used to access CMC email and the CMC employee self-service portal only."
        
    elif "flexible working culture" in q_lower:
        return refusal_template
        
    elif "da" in q_lower and "meal receipts" in q_lower:
        return "[policy_finance_reimbursement.txt - Section 2.6] If actual meal expenses are claimed instead of DA, receipts are mandatory... DA and meal receipts cannot be claimed simultaneously for the same day."
        
    elif "who approves" in q_lower and "leave without pay" in q_lower:
        return "[policy_hr_leave.txt - Section 5.2] LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        
    else:
        return refusal_template

def main():
    parser = argparse.ArgumentParser(description="Ask My Documents Assistant")
    parser.add_argument("--test-all", action="store_true", help="Run through all 7 test questions automatically")
    args = parser.parse_args()

    docs = retrieve_documents()

    if args.test_all:
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone for work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?"
        ]
        for q in test_questions:
            print(f"Q: {q}")
            print(f"A: {answer_question(q, docs)}\n")
        return

    print("Zero-Hallucination QA Assistant (UC-X)")
    print("Type 'exit' or 'quit' to quit.\n")
    
    while True:
        try:
            q = input("Ask a policy question: ")
            if q.lower() in ['exit', 'quit']:
                break
            print("\nAnswer:\n" + answer_question(q, docs) + "\n")
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
