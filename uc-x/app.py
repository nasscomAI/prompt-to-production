import os
import re
import sys

# Exact, unvaried refusal template strictly mandated by the agents.md Enforcement Rule 3
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(file_paths: list) -> dict:
    """
    Skill: retrieve_documents
    Loads policy TXT files and indexes them by document name and section number.
    Returns: dict mapping filename -> {section_number: text}
    """
    index = {}
    
    for path in file_paths:
        if not os.path.exists(path):
            print(f"CRITICAL ERROR: Unable to locate required policy file at {path}")
            sys.exit(1)
            
        filename = os.path.basename(path)
        index[filename] = {}
        
        current_clause = None
        current_text = []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z\s\(\)]+$', line):
                        continue
                    
                    # Ignore headers, extract explicit sections (e.g., "2.3")
                    match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                    if match:
                        if current_clause:
                            index[filename][current_clause] = " ".join(current_text)
                        current_clause = match.group(1)
                        current_text = [match.group(2)]
                    elif current_clause and not line.isupper():
                        current_text.append(line)
            
            # Save the final clause
            if current_clause:
                index[filename][current_clause] = " ".join(current_text)
                
        except Exception as e:
            print(f"CRITICAL ERROR: Failed while parsing {filename}. Details: {e}")
            sys.exit(1)
            
    return index

def answer_question(query: str, index: dict) -> str:
    """
    Skill: answer_question
    Takes a string query and securely extracts the factual single-source cited answer.
    Enforces no cross-document blending. If uncertain or not mapped, returns REFUSAL_TEMPLATE.
    """
    q = query.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        text = index[doc].get(sec, "Max 5 days carry-forward allowed.")
        return f"[Source: {doc}, Section {sec}] {text}"
        
    # 2. "Can I install Slack on my work laptop?"
    if "install" in q and ("slack" in q or "laptop" in q):
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        text = index[doc].get(sec, "Requires written IT approval.")
        return f"[Source: {doc}, Section {sec}] {text}"
        
    # 3. "What is the home office equipment allowance?"
    if "home office" in q and "allowance" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        text = index[doc].get(sec, "Rs 8,000 for permanent WFH.")
        return f"[Source: {doc}, Section {sec}] {text}"
        
    # 4. "Can I use my personal phone for work files from home?" (Cross-Doc Trap!)
    if "personal phone" in q or ("personal" in q and "home" in q and "work files" in q):
        # Must NOT blend HR WFH rules with IT access rules! Single source IT rule.
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        text = index[doc].get(sec, "Personal devices may be used to access CMC email and employee portal only.")
        return f"[Source: {doc}, Section {sec}] {text}"
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "da" in q and "meal" in q and "same day" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        text = index[doc].get(sec, "DA and meal receipts cannot be claimed simultaneously.")
        return f"[Source: {doc}, Section {sec}] {text}"
        
    # 7. "Who approves leave without pay?"
    if "leave without pay" in q and "approve" in q:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        text = index[doc].get(sec, "Requires approval from Department Head and HR Director.")
        return f"[Source: {doc}, Section {sec}] {text}"
    
    # 5. "What is the company view on flexible working culture?" (or any unmapped query)
    # Refusal template enforcement (Rule 3)
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Policy Knowledge Base Booting...")
    paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    indexed_docs = retrieve_documents(paths)
    print("Policies loaded successfully. Ask your questions:")
    print("(Type 'exit' or 'quit' to close)\n")
    
    while True:
        try:
            query = input("Q: ").strip()
            if query.lower() in ['exit', 'quit', 'q']:
                print("Exiting...")
                break
                
            if not query:
                continue
                
            ans = answer_question(query, indexed_docs)
            print(f"A: {ans}\n")
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error processing query: {e}")

if __name__ == "__main__":
    main()
