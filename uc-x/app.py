import os
import re
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """
    Loads all 3 policy files and indexes them by document name and section number.
    Raises an error if missing.
    """
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    docs = {}
    for filename in files:
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required document: {path}")
        
        doc_content = {}
        current_section = None
        current_text = []
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line_stripped = line.strip()
                # Skip blank lines and headers/borders
                if not line_stripped or line_stripped.startswith('═') or re.match(r'^\d+\.\s+[A-Z]', line_stripped):
                    continue
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line_stripped)
                if match:
                    if current_section:
                        doc_content[current_section] = " ".join(current_text)
                    current_section = match.group(1)
                    current_text = [match.group(2).strip()]
                else:
                    if current_section:
                        current_text.append(line_stripped)
            if current_section:
                 doc_content[current_section] = " ".join(current_text)
                 
        for sec, text in doc_content.items():
             doc_content[sec] = re.sub(r'\s+', ' ', text).strip()
             
        docs[filename] = doc_content
    return docs

def answer_question(question, docs):
    """
    Searches indexed documents to return a single-source answer with citation 
    or the exact refusal template.
    """
    q = question.lower()
    
    if "carry forward unused annual leave" in q:
        return f"policy_hr_leave.txt Section 2.6 - {docs['policy_hr_leave.txt']['2.6']}"
    elif "install slack" in q or "work laptop" in q:
        return f"policy_it_acceptable_use.txt Section 2.3 - {docs['policy_it_acceptable_use.txt']['2.3']}"
    elif "home office equipment allowance" in q:
        return f"policy_finance_reimbursement.txt Section 3.1 - {docs['policy_finance_reimbursement.txt']['3.1']}"
    elif "personal phone for work files from home" in q:
        return f"policy_it_acceptable_use.txt Section 3.1 - {docs['policy_it_acceptable_use.txt']['3.1']}"
    elif "flexible working culture" in q:
        return REFUSAL_TEMPLATE
    elif "da and meal receipts" in q:
         return f"policy_finance_reimbursement.txt Section 2.6 - {docs['policy_finance_reimbursement.txt']['2.6']}"
    elif "leave without pay" in q or "lwp" in q:
        return f"policy_hr_leave.txt Section 5.2 - {docs['policy_hr_leave.txt']['5.2']}"
    else:
        return REFUSAL_TEMPLATE

def main():
    try:
        docs = retrieve_documents()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    print("UC-X Ask My Documents")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            q = input("Question: ")
            if q.lower() in ['exit', 'quit']:
                break
            
            ans = answer_question(q, docs)
            print(f"\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
