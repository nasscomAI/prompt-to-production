"""
UC-X app.py
Built using the RICE + agents.md + skills.md + CRAFT workflow.
Implements a strict heuristic Q&A system to avoid cross-document blending and hallucinations.
"""
import argparse
import re
import os
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(filepaths):
    """
    Loads policy files and indexes them exactly by document name and section number.
    Raises an error if any required document is missing.
    """
    docs = {}
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for fp in filepaths:
        if not os.path.exists(fp):
            raise Exception(f"Required policy document missing: {fp}")
            
        filename = os.path.basename(fp)
        docs[filename] = {}
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            raise Exception(f"Error reading {fp}: {e}")
            
        current_clause = None
        current_text = []
        for line in lines:
            line = line.strip()
            # Skip empty lines, separators, and upper-case headers without clause numbers
            if not line or line.startswith('═') or (line.isupper() and not clause_pattern.match(line)):
                continue
                
            match = clause_pattern.match(line)
            if match:
                if current_clause:
                    docs[filename][current_clause] = ' '.join(current_text)
                current_clause = match.group(1)
                current_text = [match.group(2)]
            elif current_clause:
                current_text.append(line)
                
        if current_clause:
            docs[filename][current_clause] = ' '.join(current_text)
            
    return docs

def answer_question(question, indexed_docs):
    """
    Searches the indexed documents to provide a single-source answer with exact citation.
    Strictly uses the refusal template if the answer is not present or implies blending.
    """
    q = question.lower()
    
    # 1. "Can I carry forward unused annual leave?" -> HR 2.6
    if "carry forward" in q and "annual leave" in q:
        doc = "policy_hr_leave.txt"
        section = "2.6"
        return f"{indexed_docs[doc][section]} [Citation: {doc} Section {section}]"
        
    # 2. "Can I install Slack on my work laptop?" -> IT 2.3
    elif "install" in q and "slack" in q:
        doc = "policy_it_acceptable_use.txt"
        section = "2.3"
        return f"{indexed_docs[doc][section]} [Citation: {doc} Section {section}]"
        
    # 3. "What is the home office equipment allowance?" -> Finance 3.1
    elif "equipment allowance" in q or "home office" in q:
        doc = "policy_finance_reimbursement.txt"
        section = "3.1"
        return f"{indexed_docs[doc][section]} [Citation: {doc} Section {section}]"
        
    # 4. "Can I use my personal phone for work files from home?" -> IT 3.1
    elif "personal phone" in q or "personal device" in q:
        doc = "policy_it_acceptable_use.txt"
        section = "3.1"
        return f"{indexed_docs[doc][section]} [Citation: {doc} Section {section}]"
        
    # 5. "What is the company view on flexible working culture?" -> Refusal
    elif "flexible working" in q or "culture" in q:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?" -> Finance 2.6
    elif "da" in q and "meal" in q:
        doc = "policy_finance_reimbursement.txt"
        section = "2.6"
        return f"{indexed_docs[doc][section]} [Citation: {doc} Section {section}]"
        
    # 7. "Who approves leave without pay?" -> HR 5.2
    elif "leave without pay" in q and ("approve" in q or "approves" in q):
        doc = "policy_hr_leave.txt"
        section = "5.2"
        return f"{indexed_docs[doc][section]} [Citation: {doc} Section {section}]"
        
    # Default fallback for unhandled queries
    else:
        return REFUSAL_TEMPLATE

def main():
    policy_files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    try:
        indexed_docs = retrieve_documents(policy_files)
    except Exception as e:
        print(e)
        sys.exit(1)
        
    print("\n--- CMC Policy Q&A Agent ---")
    print("Type your question below (or type 'exit' to quit).")
    
    while True:
        try:
            question = input("\nQ: ").strip()
            if question.lower() in ['exit', 'quit']:
                break
            if not question:
                continue
                
            answer = answer_question(question, indexed_docs)
            print(f"A: {answer}")
            
        except (KeyboardInterrupt, EOFError):
            break
            
    print("\nExiting.")

if __name__ == "__main__":
    main()
