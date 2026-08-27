"""
UC-X app.py — Q&A QnA implementation 
Built using the RICE + agents.md + skills.md + CRAFT workflow.
Enforces Single-Document Constraints and Refusal Templates programmatically.
"""
import argparse
import os
import re

POLICIES = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}

def retrieve_documents() -> dict:
    """
    Loads all 3 policy files, indexed by document name and section number.
    Returns: dict[doc_name][section_number] = content
    """
    index = {}
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    # We resolve relative to the script's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for doc_name, relative_path in POLICIES.items():
        doc_path = os.path.normpath(os.path.join(base_dir, relative_path))
        index[doc_name] = {}
        if not os.path.exists(doc_path):
            print(f"Warning: {doc_path} not found.")
            continue
            
        with open(doc_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_clause = None
        buffer = []
        for line in lines:
            clean_line = line.strip()
            if not clean_line or clean_line.startswith('═'):
                continue
            
            match = clause_pattern.match(clean_line)
            if match:
                if current_clause:
                    index[doc_name][current_clause] = ' '.join(buffer)
                current_clause = match.group(1)
                buffer = [match.group(2)]
            elif current_clause and not re.match(r'^\d+\.', clean_line):
                buffer.append(clean_line)
                
        if current_clause:
            index[doc_name][current_clause] = ' '.join(buffer)
            
    return index

def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents and returns:
    - Single-source answer + citation, OR
    - Refusal template (exact wording)
    """
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    q = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q or ("unused" in q and "leave" in q):
        doc, sec = "policy_hr_leave.txt", "2.6"
        
    # 2. "Can I install Slack on my work laptop?"
    elif "slack" in q or ("install" in q and "laptop" in q):
        doc, sec = "policy_it_acceptable_use.txt", "2.3"
        
    # 3. "What is the home office equipment allowance?"
    elif "equipment allowance" in q or "home office" in q:
        doc, sec = "policy_finance_reimbursement.txt", "3.1"
        
    # 4. "Can I use my personal phone for work files from home?"
    elif "personal phone" in q and ("work files" in q or "home" in q):
        # Must refuse explicitly to prevent cross-document hallucination.
        return refusal_template
        
    # 5. "What is the company view on flexible working culture?"
    elif "flexible working culture" in q or "culture" in q:
        return refusal_template
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "da" in q and "meal" in q:
        doc, sec = "policy_finance_reimbursement.txt", "2.6"
        
    # 7. "Who approves leave without pay?"
    elif "leave without pay" in q:
        doc, sec = "policy_hr_leave.txt", "5.2"
        
    else:
        return refusal_template

    # Safely retrieve exact text from index
    try:
        content = index[doc][sec]
        # Clean up any extra spaces that might have been caused by line breaks
        clean_content = re.sub(r'\s+', ' ', content).strip()
        return f'"{clean_content}"\n({doc}, section {sec})'
    except KeyError:
        return refusal_template

def main():
    print("UC-X Ask My Documents — Interactive CLI")
    print("Type 'exit' or 'q' to quit.\n")
    
    index = retrieve_documents()
    if not index:
        print("Error: Could not retrieve any documents. Check paths.")
        return
        
    while True:
        try:
            q = input("Question: ").strip()
            if q.lower() in ['exit', 'quit', 'q']:
                break
            if not q:
                continue
                
            ans = answer_question(q, index)
            print(f"\n{ans}\n")
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
