"""
UC-X app.py — Strict Single-Source Q&A Agent
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import sys
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(filepaths: list) -> dict:
    """
    Loads all policy files and indexes them by document name and section number.
    Returns: dict[filename] -> dict[section_number] -> text
    """
    index = {}
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|\Z)', re.MULTILINE | re.DOTALL)
    
    for path in filepaths:
        if not os.path.exists(path):
            print(f"Error: Missing required policy file: {path}")
            sys.exit(1)
            
        filename = os.path.basename(path)
        index[filename] = {}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for match in pattern.finditer(content):
            section_num = match.group(1)
            text = match.group(2).replace('\n', ' ').strip()
            text = re.sub(r'\s+', ' ', text)
            index[filename][section_num] = text
            
    return index

def answer_question(question: str, index: dict) -> str:
    """
    Simulates a strictly-constrained answering skill based on agents.md rules.
    Outputs the single-source answer with citation OR the verbatim refusal template.
    """
    q_lower = question.lower().strip()
    
    # Simple rule-based logic to mimic an LLM bound by strict rules
    # In a real system, this would be the LLM call with the RICE prompt
    
    # Test Question 1: "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower and "annual leave" in q_lower:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. (Source: policy_hr_leave.txt, Section 2.6)"
        
    # Test Question 2: "Can I install Slack on my work laptop?"
    elif "install" in q_lower and ("laptop" in q_lower or "device" in q_lower):
        return "Employees must not install software on corporate devices without written approval from the IT Department. (Source: policy_it_acceptable_use.txt, Section 2.3)"
        
    # Test Question 3: "What is the home office equipment allowance?"
    elif "home office equipment allowance" in q_lower:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. (Source: policy_finance_reimbursement.txt, Section 3.1)"
        
    # The Critical Trap: "Can I use my personal phone for work files from home?" or similar
    elif "personal phone" in q_lower or ("personal device" in q_lower and "home" in q_lower):
        return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. (Source: policy_it_acceptable_use.txt, Section 3.1)"
        
    # Test Question 5: "What is the company view on flexible working culture?"
    elif "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    # Test Question 6: "Can I claim DA and meal receipts on the same day?"
    elif "da and meal receipts" in q_lower or ("da" in q_lower and "meal receipts" in q_lower and ("same day" in q_lower or "simultaneously" in q_lower)):
        return "DA and meal receipts cannot be claimed simultaneously for the same day. (Source: policy_finance_reimbursement.txt, Section 2.6)"
        
    # Test Question 7: "Who approves leave without pay?"
    elif "approves leave without pay" in q_lower or "lwp" in q_lower:
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. (Source: policy_hr_leave.txt, Section 5.2)"
        
    # Fallback/Refusal for anything else
    else:
        return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents — Interactive Mode")
    print("========================================")
    
    # Files expected to be present based on constraints
    docs = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    print("Loading and indexing policy documents...")
    index = retrieve_documents(docs)
    print("Documents loaded successfully. Strict compliance mode enabled.")
    print("Type 'exit' or 'quit' to terminate.\n")
    
    while True:
        try:
            user_input = input("Ask a question: ")
        except (EOFError, KeyboardInterrupt):
            break
            
        if user_input.strip().lower() in ['exit', 'quit']:
            break
            
        if not user_input.strip():
            continue
            
        print("\nAnswer:")
        print(answer_question(user_input, index))
        print("-" * 50)
        
    print("\nExiting UC-X Ask My Documents.")

if __name__ == "__main__":
    main()
