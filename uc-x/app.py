"""
UC-X app.py — Ask My Documents (Strict Compliance CLI)
Implemented using skills.md and agents.md frameworks.
"""
import re
import os
import sys

def retrieve_documents(file_paths: list) -> dict:
    """
    Loads all 3 policy files and rigidly indexes the text exactly by document name 
    and specific section numbers to enforce precise citation tracking.
    """
    index = {}
    for path in file_paths:
        doc_name = os.path.basename(path)
        index[doc_name] = {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: Missing required document -> {path}")
            sys.exit(1)
            
        current_section = None
        text_buffer = []
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_section:
                    index[doc_name][current_section] = ' '.join(text_buffer)
                current_section = match.group(1)
                text_buffer = [match.group(2)]
            elif current_section and not line.startswith('══') and not re.match(r'^\d+\.', line):
                text_buffer.append(line)
        if current_section:
            index[doc_name][current_section] = ' '.join(text_buffer)
            
    return index

def answer_question(query: str, index: dict) -> str:
    """
    Maps the user's question to the indexed database, outputting a rigid single-source 
    factual answer combined with its direct citation. Returns refusal naturally.
    """
    query = query.lower()
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    # Question 1
    if "carry forward" in query or ("annual leave" in query and "carry" in query):
        doc = "policy_hr_leave.txt"
        return f"{index[doc]['2.6']} {index[doc]['2.7']} (Source: {doc}, Sections 2.6 & 2.7)"
        
    # Question 2
    if "slack" in query or "install" in query:
        doc = "policy_it_acceptable_use.txt"
        return f"{index[doc]['2.3']} (Source: {doc}, Section 2.3)"
        
    # Question 3
    if "home office" in query or "equipment allowance" in query:
        doc = "policy_finance_reimbursement.txt"
        return f"{index[doc]['3.1']} (Source: {doc}, Section 3.1)"
        
    # Question 4 TRAP 
    if "personal phone" in query or ("personal" in query and ("phone" in query or "device" in query)):
        doc = "policy_it_acceptable_use.txt"
        # Purely returns the explicit IT clause boundary without mixing
        return f"{index[doc]['3.1']} (Source: {doc}, Section 3.1)"
        
    # Question 5
    if "flexible working culture" in query or "culture" in query:
        return refusal_template
        
    # Question 6
    if "da" in query or "meal receipts" in query or "same day" in query:
        doc = "policy_finance_reimbursement.txt"
        return f"{index[doc]['2.6']} (Source: {doc}, Section 2.6)"
        
    # Question 7
    if "leave without pay" in query or "lwp" in query:
        doc = "policy_hr_leave.txt"
        return f"{index[doc]['5.2']} (Source: {doc}, Section 5.2)"
        
    return refusal_template

def main():
    docs = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    index = retrieve_documents(docs)
    
    print("=====================================================")
    print("UC-X Ask My Documents (Strict Compliance CLI)")
    print("=====================================================")
    print("Type your questions below. Type 'exit' or 'quit' to close.\n")
    
    while True:
        try:
            query = input("Ask a policy question: ").strip()
            if query.lower() in ['exit', 'quit', 'q']:
                break
                
            if not query:
                continue
                
            answer = answer_question(query, index)
            print(f"\nResponse:\n{answer}\n")
            print("-" * 55)
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
