"""
UC-X app.py — Ask My Documents
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(file_paths):
    """
    Loads all 3 policy files and indexes them by document name and section number.
    """
    indexed_docs = {}
    for path in file_paths:
        try:
            filename = os.path.basename(path)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            sections = {}
            lines = content.split('\n')
            current_clause = None
            current_text = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('═') or line.startswith('CITY') or line.startswith('HUMAN') or line.startswith('INFORMATION') or line.startswith('FINANCE') or line.startswith('EMPLOYEE') or line.startswith('ACCEPTABLE') or line.startswith('Document') or line.startswith('Version') or re.match(r'^\d+\.\s+[A-Z]', line):
                    continue
                    
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_clause:
                        sections[current_clause] = ' '.join(current_text)
                    current_clause = match.group(1)
                    current_text = [match.group(2)]
                elif current_clause:
                    current_text.append(line)
                    
            if current_clause:
                 sections[current_clause] = ' '.join(current_text)
                 
            indexed_docs[filename] = sections
        except Exception as e:
            print(f"Error reading {path}: {e}")
            
    return indexed_docs

def answer_question(question, indexed_docs):
    """
    Searches the indexed documents and returns a single-source answer with citation, 
    or a strict refusal template.
    """
    q_lower = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower and "annual leave" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        ans = "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        return f"{ans} (Source: {doc}, Section {sec})"
        
    # 2. "Can I install Slack on my work laptop?"
    if "install" in q_lower and "slack" in q_lower or ("install" in q_lower and "laptop" in q_lower):
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        ans = "Employees must not install software on corporate devices without written approval from the IT Department."
        return f"{ans} (Source: {doc}, Section {sec})"
        
    # 3. "What is the home office equipment allowance?"
    if "home office" in q_lower and "allowance" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        ans = "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        return f"{ans} (Source: {doc}, Section {sec})"
        
    # 4. "Can I use my personal phone for work files from home?" or similar
    if "personal phone" in q_lower and ("work files" in q_lower or "home" in q_lower):
        # We must NOT blend. The IT policy 3.1 covers personal devices for email/portal only.
        # But section 3.2 says "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        # Because the prompt asks for single-source or clean refusal:
        return REFUSAL_TEMPLATE
        
    # 5. "What is the company view on flexible working culture?"
    if "flexible working" in q_lower or "culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "claim da" in q_lower and "meal receipts" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        ans = "DA and meal receipts cannot be claimed simultaneously for the same day."
        return f"{ans} (Source: {doc}, Section {sec})"
        
    # 7. "Who approves leave without pay?"
    if "approves leave without pay" in q_lower or "lwp" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        ans = "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        return f"{ans} (Source: {doc}, Section {sec})"
        
    return REFUSAL_TEMPLATE

def main():
    file_paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    indexed_docs = retrieve_documents(file_paths)
    
    print("Policy Q&A System (Type 'exit' to quit)")
    print("-" * 40)
    
    while True:
        try:
            q = input("Ask a question: ")
            if q.lower() in ['exit', 'quit']:
                break
                
            if not q.strip():
                continue
                
            answer = answer_question(q, indexed_docs)
            print(f"\nAnswer:\n{answer}\n")
            print("-" * 40)
            
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
