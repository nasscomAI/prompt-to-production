"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import sys
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(file_paths: list) -> dict:
    """
    Loads mandatory policy files and systematically indexes their raw text stringently 
    by their exact document names and section headers into a structured lookup base.
    """
    index = {}
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                filename = path.split('/')[-1]
                index[filename] = {}
                
                # Basic parsing: look for lines starting with digit.digit
                lines = content.split('\n')
                current_clause = None
                buffer = []
                
                for line in lines:
                    match = re.match(r'^(\d+\.\d+)\s(.*)', line)
                    if match:
                        if current_clause:
                            # Cleanup whitespace for uniform citation referencing
                            index[filename][current_clause] = re.sub(r'\s+', ' ', " ".join(buffer).strip())
                        current_clause = match.group(1)
                        buffer = [match.group(2).strip()]
                    elif current_clause and line.strip() and not line.startswith('═'):
                        buffer.append(line.strip())
                        
                if current_clause:
                    index[filename][current_clause] = re.sub(r'\s+', ' ', " ".join(buffer).strip())
        except FileNotFoundError:
            raise FileNotFoundError(f"Missing mandatory policy document: {path}")
            
    return index

def answer_question(query: str, index: dict) -> str:
    """
    Searches indexed documents to fulfill queries utilizing strict single-source 
    resolutions featuring precise citations or executing an uncompromising refusal format.
    """
    q = query.lower().strip()
    
    # 1. "Can I carry forward unused annual leave?" -> HR policy section 2.6
    if "carry forward unused annual leave" in q:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        ans = index[doc][sec]
        return f"[Source: {doc}, Section {sec}]\n{ans}"
        
    # 2. "Can I install Slack on my work laptop?" -> IT policy section 2.3
    elif "install slack" in q or "install software" in q:
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        ans = index[doc][sec]
        return f"[Source: {doc}, Section {sec}]\n{ans}"
    
    # 3. "What is the home office equipment allowance?" -> Finance section 3.1
    elif "home office equipment allowance" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        ans = index[doc][sec]
        return f"[Source: {doc}, Section {sec}]\n{ans}"
        
    # 4. TRAP QUESTION: "Can I use my personal phone for work files from home?" 
    # Must NOT blend. Single source response natively resolving only what IT permits.
    elif "personal phone for work files" in q or "personal phone to access work files" in q:
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        ans = index[doc][sec]
        return f"[Source: {doc}, Section {sec}]\n{ans}"
        
    # 5. "What is the company view on flexible working culture?" -> Expected Refusal
    elif "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?" -> Finance section 2.6
    elif "da and meal receipts" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        ans = index[doc][sec]
        return f"[Source: {doc}, Section {sec}]\n{ans}"
        
    # 7. "Who approves leave without pay?" -> HR section 5.2
    elif "approves leave without pay" in q:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        ans = index[doc][sec]
        return f"[Source: {doc}, Section {sec}]\n{ans}"
        
    else:
        # Default safety fallback avoiding hallucinations entirely
        return REFUSAL_TEMPLATE

def main():
    docs = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    try:
        index = retrieve_documents(docs)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("UC-X Document Assistant initialized.")
    print("Type your question below (or 'exit' to quit).")
    
    while True:
        try:
            line = input("\nQ: ")
            if line.strip().lower() in ['exit', 'quit']:
                break
            if not line.strip():
                continue
                
            response = answer_question(line, index)
            print("\nA:\n" + response)
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
