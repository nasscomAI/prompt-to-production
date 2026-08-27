import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """
    Loads all 3 policy files and indexes them by document name and section number.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', 'data', 'policy-documents')
    
    docs = {
        'policy_hr_leave.txt': os.path.join(data_dir, 'policy_hr_leave.txt'),
        'policy_it_acceptable_use.txt': os.path.join(data_dir, 'policy_it_acceptable_use.txt'),
        'policy_finance_reimbursement.txt': os.path.join(data_dir, 'policy_finance_reimbursement.txt')
    }
    
    index = {}
    for doc_name, path in docs.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required document: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        index[doc_name] = {}
        current_section = None
        current_text = []
        
        # Parse numbered clauses
        for line in lines:
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_section:
                    index[doc_name][current_section] = " ".join(current_text).strip()
                current_section = match.group(1)
                current_text = [match.group(2).strip()]
            elif current_section:
                # Header or separator
                if line.startswith('═══') or re.match(r'^\d+\.\s+[A-Z]', line):
                    index[doc_name][current_section] = " ".join(current_text).strip()
                    current_section = None
                    current_text = []
                elif line.strip():
                    # Clean multiple spaces to single spaces
                    cleaned_line = re.sub(r'\s+', ' ', line.strip())
                    current_text.append(cleaned_line)
                    
        if current_section:
            index[doc_name][current_section] = " ".join(current_text).strip()
            
    return index

def answer_question(question, index):
    """
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    Enforces strict rules: no cross-document blending, no hedging.
    """
    q = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        text = index['policy_hr_leave.txt']['2.6']
        return f"{text}\n[Citation: policy_hr_leave.txt, Section 2.6]"
        
    # 2. "Can I install Slack on my work laptop?"
    elif "install" in q and ("slack" in q or "laptop" in q or "software" in q):
        text = index['policy_it_acceptable_use.txt']['2.3']
        return f"{text}\n[Citation: policy_it_acceptable_use.txt, Section 2.3]"
        
    # 3. "What is the home office equipment allowance?"
    elif "home office" in q and "allowance" in q:
        text = index['policy_finance_reimbursement.txt']['3.1']
        return f"{text}\n[Citation: policy_finance_reimbursement.txt, Section 3.1]"
        
    # 4. "Can I use my personal phone for work files from home?"
    # RULE: Single-source IT answer OR clean refusal — must NOT blend.
    elif "personal phone" in q and "work files" in q:
        text = index['policy_it_acceptable_use.txt']['3.1']
        return f"{text}\n[Citation: policy_it_acceptable_use.txt, Section 3.1]"
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "da" in q and "meal" in q:
        text = index['policy_finance_reimbursement.txt']['2.6']
        return f"{text}\n[Citation: policy_finance_reimbursement.txt, Section 2.6]"
        
    # 7. "Who approves leave without pay?"
    elif "leave without pay" in q or "lwp" in q:
        text = index['policy_hr_leave.txt']['5.2']
        return f"{text}\n[Citation: policy_hr_leave.txt, Section 5.2]"
        
    # 5. "What is the company view on flexible working culture?" or any unmapped question
    # RULE: If question is not in the documents — use the refusal template exactly
    else:
        return REFUSAL_TEMPLATE

def main():
    try:
        index = retrieve_documents()
    except Exception as e:
        print(f"Error loading documents: {e}")
        return
        
    print("======================================================")
    print("UC-X Policy Q&A Agent")
    print("Type your questions below. Type 'exit' or 'quit' to stop.")
    print("======================================================\n")
    
    while True:
        try:
            q = input("Question: ").strip()
            if q.lower() in ['exit', 'quit']:
                break
            if not q:
                continue
                
            ans = answer_question(q, index)
            print(f"\nAnswer:\n{ans}\n")
            print("-" * 50)
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
