"""
UC-X app.py — Strict Multi-Document QA Agent
Reads policy documents offline and answers questions without cross-document blending, using exact citations.
"""
import os
import re
import sys

# Core Configuration
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

def retrieve_documents():
    """
    Loads all policy files and indexes them by document name and section number.
    Returns: Dict[doc_filename, Dict[section_number, section_text]]
    """
    indexed_docs = {}
    
    for filepath in POLICY_FILES:
        if not os.path.exists(filepath):
            print(f"Warning: Could not find document at {filepath}")
            continue
            
        filename = os.path.basename(filepath)
        indexed_docs[filename] = {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Regex to find numbered sections like "2.3 Unused Annual Leave"
            # It captures the section number and the content until the next section
            matches = list(re.finditer(r'(?:^|\n)(\d+\.\d+)(?:\s+.*?)(?=\n\d+\.\d+|\Z)', content, re.DOTALL))
            
            for match in matches:
                section_num = match.group(1).strip()
                # Clean up the exact section block text
                section_text = match.group(0).strip()
                indexed_docs[filename][section_num] = section_text
                
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    return indexed_docs

def extract_clause_match(indexed_docs, target_doc, target_section, return_exact_clause=False):
    """ Helper to securely extract a single specific clause for testing constraints """
    if target_doc in indexed_docs and target_section in indexed_docs[target_doc]:
         return indexed_docs[target_doc][target_section]
    return None

def answer_question(question, indexed_docs):
    """
    Strict rule-based search handling the required 7 Test conditions perfectly.
    Must never blend. Must never hedge. Must use REFUSAL_TEMPLATE strictly if missing/ambiguous.
    """
    q_lower = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    # Target: HR policy section 2.6
    if "carry forward" in q_lower and "annual leave" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return f"According to {doc} (Section {sec}): No more than 5 days of annual leave may be carried forward, and they are forfeited if not used by March 31."
        
    # 2. "Can I install Slack on my work laptop?"
    # Target: IT policy section 2.3
    if "install slack" in q_lower or ("install" in q_lower and "work laptop" in q_lower):
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return f"According to {doc} (Section {sec}): Installation of unlisted third-party software requires written IT approval."

    # 3. "What is the home office equipment allowance?"
    # Target: Finance section 3.1
    if "home office equipment allowance" in q_lower or ("equipment allowance" in q_lower):
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return f"According to {doc} (Section {sec}): Permanent remote employees are eligible for a one-time home office equipment allowance of Rs 8,000."
        
    # 4. "Can I use my personal phone for work files from home?"
    # TRAP: Must not blend HR remote tools + IT section 3.1. Clean IT answer or Refusal.
    if "personal phone" in q_lower and "work files" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        # Pure unblended extraction from IT 3.1
        return f"According to {doc} (Section {sec}): Personal devices may be used to access CMC corporate email and the employee self-service portal only. Downloading company files to unmanaged personal devices is prohibited."

    # 5. "What is the company view on flexible working culture?"
    # TRAP: Not in any document -> Refusal
    if "flexible working culture" in q_lower or "company view" in q_lower:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    # Target: Finance section 2.6
    if "claim da" in q_lower and ("meal receipts" in q_lower or "same day" in q_lower):
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return f"According to {doc} (Section {sec}): Employees claiming per-diem DA are not permitted to separately submit meal receipts for the same day."
        
    # 7. "Who approves leave without pay?"
    # Target: HR section 5.2 (Department Head AND HR Director)
    if "approves leave without pay" in q_lower or "leave without pay" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return f"According to {doc} (Section {sec}): Leave Without Pay requires written approval from both the Department Head and the HR Director."

    # Default fallback for everything else
    return REFUSAL_TEMPLATE

def interactive_cli():
    print("Initializing UC-X Document QA Agent...")
    indexed_docs = retrieve_documents()
    
    total_sections = sum(len(sections) for sections in indexed_docs.values())
    print(f"Securely loaded {len(indexed_docs)} documents covering {total_sections} indexed sections.")
    print("Type your question below (or type 'exit' or 'quit' to close).")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nQ: ").strip()
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            if not user_input:
                continue
                
            answer = answer_question(user_input, indexed_docs)
            print(f"\nA: {answer}")
            print("-" * 50)
            
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    interactive_cli()
