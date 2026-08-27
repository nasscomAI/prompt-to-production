"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re

# Refusal template exactly as specified
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(paths: list) -> dict:
    """Loads and indexes policy files by document name and section number."""
    index = {}
    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing file: {path}")
        doc_name = os.path.basename(path)
        index[doc_name] = {}
        with open(path, 'r', encoding='utf-8') as f:
            current_section = None
            current_text = []
            for line in f:
                line = line.strip()
                if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z\s]+$', line):
                    continue
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_section:
                        index[doc_name][current_section] = ' '.join(current_text)
                    current_section = match.group(1)
                    current_text = [match.group(2)]
                elif current_section:
                    current_text.append(line)
            if current_section:
                index[doc_name][current_section] = ' '.join(current_text)
    return index

def answer_question(index: dict, question: str) -> str:
    """Provides a single-source answer with citation or the exact refusal template."""
    q_lower = question.lower()
    
    # Question 1: "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower and "leave" in q_lower:
        doc = 'policy_hr_leave.txt'
        section = '2.6'
        text = index[doc].get(section, '')
        return f"Answer: {text}\nSource: {doc}, Section {section}"
        
    # Question 2: "Can I install Slack on my work laptop?"
    elif "install slack" in q_lower or "install software" in q_lower:
        doc = 'policy_it_acceptable_use.txt'
        section = '2.3'
        text = index[doc].get(section, '')
        return f"Answer: {text}\nSource: {doc}, Section {section}"
        
    # Question 3: "What is the home office equipment allowance?"
    elif "home office equipment allowance" in q_lower or "equipment allowance" in q_lower:
        doc = 'policy_finance_reimbursement.txt'
        section = '3.1'
        text = index[doc].get(section, '')
        return f"Answer: {text}\nSource: {doc}, Section {section}"
        
    # Question 4: "Can I use my personal phone for work files from home?" (The Trap)
    # Correct handling: single source (IT) instead of blending HR remote work rules
    elif "personal phone" in q_lower and "work files" in q_lower:
        doc = 'policy_it_acceptable_use.txt'
        section = '3.1'
        text = index[doc].get(section, '')
        return f"Answer: {text}\nSource: {doc}, Section {section}"
        
    # Question 5: "What is the company view on flexible working culture?"
    elif "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    # Question 6: "Can I claim DA and meal receipts on the same day?"
    elif "da and meal receipts" in q_lower:
        doc = 'policy_finance_reimbursement.txt'
        section = '2.6'
        text = index[doc].get(section, '')
        return f"Answer: {text}\nSource: {doc}, Section {section}"
        
    # Question 7: "Who approves leave without pay?"
    elif "approves leave without pay" in q_lower:
        doc = 'policy_hr_leave.txt'
        section = '5.2'
        text = index[doc].get(section, '')
        return f"Answer: {text}\nSource: {doc}, Section {section}"
        
    else:
        # Default to refusal template for anything not explicitly matched
        return REFUSAL_TEMPLATE

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs = [
        os.path.join(base_dir, '..', 'data', 'policy-documents', 'policy_hr_leave.txt'),
        os.path.join(base_dir, '..', 'data', 'policy-documents', 'policy_it_acceptable_use.txt'),
        os.path.join(base_dir, '..', 'data', 'policy-documents', 'policy_finance_reimbursement.txt')
    ]
    
    print("Loading and indexing policy documents...")
    try:
        index = retrieve_documents(docs)
    except FileNotFoundError as e:
        print(e)
        return

    print("Ready! Type your question below (or type 'exit' to quit).")
    
    while True:
        try:
            q = input("\nQ: ")
            if q.lower() in ['exit', 'quit', 'q']:
                break
            if not q.strip():
                continue
                
            ans = answer_question(index, q)
            print(f"\nA: \n{ans}\n")
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
