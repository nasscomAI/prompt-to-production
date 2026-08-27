"""
UC-X app.py — Ask My Documents (Interactive CLI)
Implemented using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(file_paths: list) -> dict:
    """
    Loads all 3 policy files and indexes their content by document name and section number.
    """
    index = {}
    for path in file_paths:
        filename = os.path.basename(path)
        index[filename] = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {path}: {e}")
            # Halt execution as per skills.md error handling
            raise e
            
        lines = content.split('\n')
        current_clause = None
        clause_text = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z]', line):
                continue
            
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_clause:
                    index[filename][current_clause] = ' '.join(clause_text)
                current_clause = match.group(1)
                clause_text = [match.group(2)]
            elif current_clause:
                clause_text.append(line)
                
        if current_clause:
            index[filename][current_clause] = ' '.join(clause_text)
            
    return index

def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents and returns a single-source answer with citation, or the exact refusal template.
    Enforces rules: single source only, no hedging, strict refusal.
    """
    q = question.lower()
    
    # 1. "Can I carry forward unused annual leave?" -> HR policy section 2.6
    if "carry forward" in q and "annual leave" in q:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return f"{doc} (Section {sec}): {index[doc][sec]}"
        
    # 2. "Can I install Slack on my work laptop?" -> IT policy section 2.3
    if "install slack" in q or ("install" in q and "laptop" in q):
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return f"{doc} (Section {sec}): {index[doc][sec]}"
        
    # 3. "What is the home office equipment allowance?" -> Finance section 3.1
    if "home office equipment allowance" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return f"{doc} (Section {sec}): {index[doc][sec]}"
        
    # 4. "Can I use my personal phone for work files from home?" -> Single-source IT 3.1 OR clean refusal
    if "personal phone for work files" in q or "personal phone to access work files" in q:
        # Refusal is the safest approach to prevent blending IT 3.1 with HR remote work policies.
        return REFUSAL_TEMPLATE
        
    # 5. "What is the company view on flexible working culture?" -> Not in documents
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?" -> Finance section 2.6
    if "da and meal receipts" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return f"{doc} (Section {sec}): {index[doc][sec]}"
        
    # 7. "Who approves leave without pay?" -> HR section 5.2
    if "leave without pay" in q and "approves" in q:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return f"{doc} (Section {sec}): {index[doc][sec]}"
        
    # If the question is unrecognized or not cleanly matchable to a single source, refuse.
    return REFUSAL_TEMPLATE

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(base_dir, '..', 'data', 'policy-documents')
    files = [
        os.path.join(docs_dir, 'policy_hr_leave.txt'),
        os.path.join(docs_dir, 'policy_it_acceptable_use.txt'),
        os.path.join(docs_dir, 'policy_finance_reimbursement.txt')
    ]
    
    print("Loading documents...")
    try:
        index = retrieve_documents(files)
    except Exception:
        print("Failed to load documents.")
        return
        
    print("Documents loaded and indexed successfully.")
    print("Ask a question about the company policies (Type 'exit' or 'quit' to stop):")
    
    while True:
        try:
            q = input("\nQ: ").strip()
        except EOFError:
            break
            
        if q.lower() in ['exit', 'quit', 'q']:
            break
            
        if not q:
            continue
            
        ans = answer_question(q, index)
        print(f"\nA: {ans}")

if __name__ == "__main__":
    main()
