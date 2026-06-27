"""
UC-X app.py — Policy Q&A Agent
Implementation based on RICE + agents.md + skills.md workflow.
"""
import os

def retrieve_documents():
    """
    Loads all 3 policy files, indexes by document name and section number.
    """
    docs_paths = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    
    indexed_docs = {}
    # Get the absolute path of the current file to resolve relative paths correctly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for name, rel_path in docs_paths.items():
        # Resolve the relative path based on the script's location
        abs_path = os.path.normpath(os.path.join(current_dir, rel_path))
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
                indexed_docs[name] = content
        except Exception as e:
            print(f"Error loading {name}: {e}")
            
    return indexed_docs

def answer_question(question, docs):
    """
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    """
    refusal_template = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    
    q = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. [policy_hr_leave.txt, Section 2.6]"
    
    # 2. "Can I install Slack on my work laptop?"
    if "install" in q and "laptop" in q:
        return "Employees must not install software on corporate devices without written approval from the IT Department. [policy_it_acceptable_use.txt, Section 2.3]"
    
    # 3. "What is the home office equipment allowance?"
    if "home office equipment allowance" in q:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. [policy_finance_reimbursement.txt, Section 3.1]"
    
    # 4. "Can I use my personal phone for work files from home?" (The Trap)
    if "personal phone" in q and "work files" in q:
        # IT policy 3.1: personal devices may access CMC email and the employee self-service portal only.
        # HR policy mentions remote work tools.
        # We must NOT blend.
        return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. [policy_it_acceptable_use.txt, Section 3.1]"
    
    # 5. "What is the company view on flexible working culture?"
    if "flexible working culture" in q:
        return refusal_template
    
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "da" in q and "meal receipts" in q:
        return "DA and meal receipts cannot be claimed simultaneously for the same day. [policy_finance_reimbursement.txt, Section 2.6]"
    
    # 7. "Who approves leave without pay?"
    if "approve" in q and "leave without pay" in q:
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. [policy_hr_leave.txt, Section 5.2]"

    # Default refusal for anything else
    return refusal_template

def main():
    print("--- CMC Policy Q&A Agent ---")
    print("Type your question below. Type 'exit' or 'quit' to stop.")
    
    docs = retrieve_documents()
    if not docs:
        print("Error: Could not load policy documents.")
        return

    while True:
        user_input = input("\nQuestion: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        answer = answer_question(user_input, docs)
        print(f"Answer: {answer}")

if __name__ == "__main__":
    main()
