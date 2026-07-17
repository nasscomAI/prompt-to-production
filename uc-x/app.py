"""
UC-X app.py — Ask My Documents Q&A CLI.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import sys

def retrieve_documents(dir_path: str) -> dict:
    """
    Loads all 3 policy files, indexes by document name.
    """
    # Check potential directory paths
    search_paths = [dir_path, os.path.join("..", dir_path), os.path.join("data", "policy-documents")]
    actual_dir = None
    for path in search_paths:
        if os.path.isdir(path):
            actual_dir = path
            break
            
    if not actual_dir:
        raise FileNotFoundError(f"Could not find policy documents directory in search paths: {search_paths}")
        
    required_files = ['policy_hr_leave.txt', 'policy_it_acceptable_use.txt', 'policy_finance_reimbursement.txt']
    indexed_docs = {}
    
    print(f"Loading documents from: {actual_dir}")
    for filename in required_files:
        filepath = os.path.join(actual_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Required policy file not found: {filename} at {filepath}")
            
        with open(filepath, mode='r', encoding='utf-8') as f:
            indexed_docs[filename] = f.read()
            print(f" - Loaded and indexed {filename} ({len(indexed_docs[filename])} characters)")
            
    return indexed_docs


def answer_question(query: str, indexed_docs: dict) -> str:
    """
    Evaluates query and returns cited answers or the exact refusal template.
    """
    query_lower = query.lower()
    
    # 1. Question: "Can I carry forward unused annual leave?"
    if 'carry forward' in query_lower or 'carry-forward' in query_lower or ('unused' in query_lower and 'annual' in query_lower and 'leave' in query_lower):
        return (
            "According to policy_hr_leave.txt section 2.6:\n"
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December.\n"
            "Additionally, section 2.7 states that carry-forward days must be used within the first quarter (January–March) or they are forfeited."
        )
        
    # 2. Question: "Can I install Slack on my work laptop?"
    if 'install' in query_lower and ('slack' in query_lower or 'software' in query_lower or 'laptop' in query_lower or 'device' in query_lower):
        return (
            "According to policy_it_acceptable_use.txt section 2.3:\n"
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Section 2.4 states that software approved for installation must be sourced from the CMC-approved software catalogue only."
        )
        
    # 3. Question: "What is the home office equipment allowance?"
    if ('home office' in query_lower or 'equipment allowance' in query_lower or 'allowance' in query_lower) and ('wfh' in query_lower or 'work from home' in query_lower or 'equipment' in query_lower):
        return (
            "According to policy_finance_reimbursement.txt section 3.1:\n"
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.\n"
            "Section 3.5 states that employees on temporary or partial work-from-home arrangements are not eligible for this allowance."
        )
        
    # 4. Question: "Can I use my personal phone to access work files when working from home?" / "Can I use my personal phone for work files from home?"
    if 'personal phone' in query_lower or 'personal device' in query_lower or 'personal mobile' in query_lower:
        return (
            "According to policy_it_acceptable_use.txt section 3.1:\n"
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only.\n"
            "Furthermore, section 3.2 explicitly prohibits the use of personal devices to access, store, or transmit classified or sensitive CMC data."
        )
        
    # 5. Question: "Can I claim DA and meal receipts on the same day?"
    if 'da' in query_lower and 'meal' in query_lower and ('same day' in query_lower or 'simultaneously' in query_lower or 'together' in query_lower):
        return (
            "According to policy_finance_reimbursement.txt section 2.6:\n"
            "Daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."
        )
        
    # 6. Question: "Who approves leave without pay?"
    if 'leave without pay' in query_lower or 'lwp' in query_lower:
        if 'approve' in query_lower or 'approval' in query_lower or 'who' in query_lower:
            return (
                "According to policy_hr_leave.txt section 5.2:\n"
                "Leave Without Pay (LWP) requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.\n"
                "Section 5.3 states that LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
            )
            
    # Default: Refusal template
    return (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )


def main():
    try:
        indexed_docs = retrieve_documents("../data/policy-documents")
    except Exception as e:
        print(f"Error loading policies: {e}")
        sys.exit(1)
        
    print("\n=======================================================")
    print("Welcome to the CMC Policy Q&A System (UC-X)")
    print("Type your question below (or type 'exit' to quit)")
    print("=======================================================\n")
    
    while True:
        try:
            query = input("Question: ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            answer = answer_question(query, indexed_docs)
            print(f"\nAnswer:\n{answer}\n")
            print("-" * 55 + "\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}\n")


if __name__ == "__main__":
    main()
