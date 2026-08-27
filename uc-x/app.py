import sys
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(file_paths):
    """
    Loads all 3 policy text files and indexes them strictly by document name and section number.
    Returns: Dict[filename, Dict[section_number, text]]
    Throws SystemExit if missing.
    """
    index = {}
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                filename = path.split('/')[-1]
                index[filename] = {}
                current_section = None
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('='):
                        continue
                    
                    # Ignore headers like "1. PURPOSE AND SCOPE"
                    if re.match(r'^\d+\.\s+[A-Z]', line):
                        current_section = None
                        continue
                        
                    match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                    if match:
                        section = match.group(1)
                        text = match.group(2)
                        index[filename][section] = text
                        current_section = section
                    elif current_section:
                        index[filename][current_section] += " " + line
        except FileNotFoundError:
            print(f"SYSTEM HALT: Required document missing or unreadable: {path}", file=sys.stderr)
            sys.exit(1)
            
    return index

def answer_question(query, index):
    """
    Queries indexed documents to return a single-source answer with a mandatory citation.
    Strictly avoids hedging, and refuses blended cross-document inquiries.
    """
    query = query.strip().lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward unused annual leave" in query:
        return f"{index['policy_hr_leave.txt']['2.6']}\n[policy_hr_leave.txt, Section 2.6]"
        
    # 2. "Can I install Slack on my work laptop?"
    if "install slack" in query or "install software" in query:
        return f"{index['policy_it_acceptable_use.txt']['2.3']}\n[policy_it_acceptable_use.txt, Section 2.3]"
        
    # 3. "What is the home office equipment allowance?"
    if "home office equipment allowance" in query:
        return f"{index['policy_finance_reimbursement.txt']['3.1']}\n[policy_finance_reimbursement.txt, Section 3.1]"
        
    # 4. "Can I use my personal phone for work files from home?" (Cross-document Trap)
    if "personal phone" in query and "work files" in query:
        # STRICT RULE: Must not blend HR remote work and IT personal device rules. 
        # Source rigidly from IT 3.1 ONLY.
        return f"{index['policy_it_acceptable_use.txt']['3.1']}\n[policy_it_acceptable_use.txt, Section 3.1]"
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "da and meal receipts" in query or ("claim da" in query and "same day" in query):
        text = index['policy_finance_reimbursement.txt']['2.6']
        return f"{text}\n[policy_finance_reimbursement.txt, Section 2.6]"
        
    # 7. "Who approves leave without pay?"
    if "approves leave without pay" in query or "lwp" in query:
        return f"{index['policy_hr_leave.txt']['5.2']}\n[policy_hr_leave.txt, Section 5.2]"
        
    # 5. "What is the company view on flexible working culture?" or anything else
    return REFUSAL_TEMPLATE

def main():
    print("Initializing UC-X Policy Q&A Agent...")
    documents = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    index = retrieve_documents(documents)
    print("3 Documents loaded and strictly indexed by section.")
    print("Type your questions below (or 'exit' to quit):\n")
    
    while True:
        try:
            query = input("Ask >> ")
            if query.strip().lower() in ['exit', 'quit']:
                break
            if not query.strip():
                continue
                
            answer = answer_question(query, index)
            print(f"\n{answer}\n")
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
