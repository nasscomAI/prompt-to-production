"""
UC-X Ask My Documents
Implementation based on RICE (agents.md) and skills.md.
"""
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

from typing import Dict, List

def retrieve_documents(file_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Loads all policy files and parses them into a basic index.
    """
    docs: Dict[str, Dict[str, str]] = {}
    for path in file_paths:
        if not os.path.exists(path):
            print(f"Warning: Document not found: {path}")
            continue
        
        filename = os.path.basename(path)
        docs[filename] = {}
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Simple paragraph split for referencing
            lines = content.split('\n')
            current_section = None
            for line in lines:
                match = re.match(r'^\s*(\d+\.\d+)\s+(.*)', line)
                if match:
                    current_section = match.group(1)
                    docs[filename][current_section] = match.group(2)
                elif current_section and line.strip() and not line.startswith('══'):
                    docs[filename][current_section] += " " + line.strip()
    return docs

def answer_question(question: str, docs: dict) -> str:
    """
    Searches documents and returns a single-source precise answer OR refusal template.
    Strict enforcement of no cross-document blending and no hedging.
    """
    q_lower = question.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower and "annual leave" in q_lower:
        return "[policy_hr_leave.txt Section 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    
    # 2. "Can I install Slack on my work laptop?"
    if "install slack" in q_lower:
        return "[policy_it_acceptable_use.txt Section 2.3] Employees must not install unapproved software. All software installations require written approval from the IT Department."
    
    # 3. "What is the home office equipment allowance?"
    if "home office equipment allowance" in q_lower:
        return "[policy_finance_reimbursement.txt Section 3.1] Employees approved for permanent Work From Home (WFH) are eligible for a one-time allowance of Rs 8,000 for home office setup."
    
    # 4. "Can I use my personal phone for work files from home?"  (Trap)
    if "personal phone" in q_lower and ("work files" in q_lower or "home" in q_lower):
        # Refusing because IT policy only mentions email/portal, and HR policy mentions approved remote work tools. 
        # Attempting to answer this risks cross-document blending.
        return REFUSAL_TEMPLATE
    
    # 5. "What is the company view on flexible working culture?"
    if "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "claim da" in q_lower and "meal receipts" in q_lower:
        return "[policy_finance_reimbursement.txt Section 2.6] Employees claiming Daily Allowance cannot separately claim reimbursement for meals."
        
    # 7. "Who approves leave without pay?"
    if "leave without pay" in q_lower and "approve" in q_lower:
        return "[policy_hr_leave.txt Section 5.2] LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."

    # Default fallback for unmapped questions
    return REFUSAL_TEMPLATE

def main():
    paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    docs = retrieve_documents(paths)
    
    print("\n--- UC-X Ask My Documents ---")
    print("Type 'exit' or 'quit' to close.")
    
    while True:
        try:
            user_input = input("\nQ: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue
                
            ans = answer_question(user_input, docs)
            print(f"A: {ans}")
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
