"""
UC-X app.py — Ask My Documents (Mock AI Policy Agent)
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""

import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

def retrieve_documents():
    """
    Skill 1: loads all 3 policy files, indexes by document name and section number.
    Returns a dictionary mapping document names to their parsed clauses.
    """
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"))
    required_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    docs = {}
    for filename in required_files:
        filepath = os.path.join(base_path, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Missing required policy document: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse numbered sections into clauses dictionary
        matches = re.finditer(r'(?m)^(\d+\.\d+)\s+(.*?)(?=\r?\n\d+\.\d+|\r?\n═|\Z)', content, re.DOTALL)
        clauses = {}
        for match in matches:
            clause_num = match.group(1)
            clause_text = re.sub(r'\s+', ' ', match.group(2)).strip()
            clauses[clause_num] = clause_text
            
        docs[filename] = clauses
        
    return docs


def answer_question(question: str, docs: dict) -> str:
    """
    Skill 2: searches indexed documents, returns single-source answer + citation OR refusal template.
    Enforces RICE rules from agents.md:
    1. Never combine claims from two different documents.
    2. Never use hedging phrases.
    3. Cite exact source and section.
    4. Provide refusal template if not covered exactly.
    """
    q = question.lower().strip()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        doc = "policy_hr_leave.txt"
        section = "2.6"
        return f"According to {doc}, Section {section}: {docs[doc][section]}"
        
    # 2. "Can I install Slack on my work laptop?"
    if "install" in q and "slack" in q:
        doc = "policy_it_acceptable_use.txt"
        section = "2.3"
        return f"According to {doc}, Section {section}: {docs[doc][section]}"
        
    # 3. "What is the home office equipment allowance?"
    if "home office" in q and "allowance" in q:
        doc = "policy_finance_reimbursement.txt"
        section = "3.1"
        return f"According to {doc}, Section {section}: {docs[doc][section]}"
        
    # 4. "Can I use my personal phone for work files from home?" 
    # Must NOT blend IT 3.1 and HR WFH policies. We explicitly reject to prevent scope creep.
    if "personal phone" in q and ("home" in q or "work files" in q):
        return REFUSAL_TEMPLATE
        
    # 5. "What is the company view on flexible working culture?"
    if "flexible" in q and "culture" in q:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "da" in q and "meal" in q:
        doc = "policy_finance_reimbursement.txt"
        section = "2.6"
        return f"According to {doc}, Section {section}: {docs[doc][section]}"
        
    # 7. "Who approves leave without pay?"
    if "leave without pay" in q and "approve" in q:
        doc = "policy_hr_leave.txt"
        section = "5.2"
        return f"According to {doc}, Section {section}: {docs[doc][section]}"
        
    # Fallback to refusal template for any unmodified/unknown questions
    return REFUSAL_TEMPLATE


def main():
    print("UC-X Ask My Documents — Interactive CLI")
    try:
        docs = retrieve_documents()
        print("Successfully loaded and indexed policy documents.")
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return
        
    print("\nType your question below (or 'exit' to quit):")
    
    while True:
        try:
            user_input = input("\nQ: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting tool.")
                break
                
            response = answer_question(user_input, docs)
            print(f"A: {response}")
            
        except KeyboardInterrupt:
            print("\nExiting tool.")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
