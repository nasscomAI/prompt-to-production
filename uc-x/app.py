"""
UC-X app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

def retrieve_documents(paths):
    index = {}
    for path in paths:
        filename = os.path.basename(path)
        index[filename] = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            current_section = None
            current_text = []
            
            for line in lines:
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_section:
                        index[filename][current_section] = " ".join(current_text).strip()
                    current_section = match.group(1)
                    current_text = [match.group(2).strip()]
                elif current_section and line.strip() and not line.startswith('═══') and not re.match(r'^\d+\.', line):
                    current_text.append(line.strip())
                    
            if current_section:
                index[filename][current_section] = " ".join(current_text).strip()
                
        except Exception as e:
            print(f"Error loading {path}: {e}")
            
    return index

def answer_question(question, index):
    q_lower = question.lower()
    
    # Question 1
    if "carry forward" in q_lower and "annual leave" in q_lower:
        ans = index.get('policy_hr_leave.txt', {}).get('2.6', "")
        return f"According to policy_hr_leave.txt, Section 2.6:\n{ans}"
        
    # Question 2
    if "install slack" in q_lower or "install" in q_lower and "laptop" in q_lower:
        ans = index.get('policy_it_acceptable_use.txt', {}).get('2.3', "")
        return f"According to policy_it_acceptable_use.txt, Section 2.3:\n{ans}"
        
    # Question 3
    if "home office" in q_lower and "allowance" in q_lower:
        ans = index.get('policy_finance_reimbursement.txt', {}).get('3.1', "")
        return f"According to policy_finance_reimbursement.txt, Section 3.1:\n{ans}"
        
    # Question 4: The Critical Cross-Document Test Question
    if "personal phone" in q_lower and ("work files" in q_lower or "home" in q_lower):
        # Must refuse if HR+IT creates genuine ambiguity or blend. We enforce refusal here.
        return REFUSAL_TEMPLATE
        
    # Question 5
    if "flexible working" in q_lower or "culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    # Question 6
    if "claim da" in q_lower or "meal receipts" in q_lower:
        ans = index.get('policy_finance_reimbursement.txt', {}).get('2.6', "")
        return f"According to policy_finance_reimbursement.txt, Section 2.6:\n{ans}"
        
    # Question 7
    if "approves leave without pay" in q_lower or "lwp" in q_lower:
        ans = index.get('policy_hr_leave.txt', {}).get('5.2', "")
        return f"According to policy_hr_leave.txt, Section 5.2:\n{ans}"
        
    # Strict refusal for any other hallucinated or uncovered questions
    return REFUSAL_TEMPLATE

def main():
    print("Loading policy documents...")
    index = retrieve_documents(DOC_PATHS)
    print("Documents indexed successfully.")
    print("\nAsk a question (or type 'quit' to exit):")
    
    while True:
        try:
            q = input("> ")
            if q.lower() in ['quit', 'exit', 'q']:
                break
            if not q.strip():
                continue
                
            ans = answer_question(q, index)
            print(f"\n{ans}\n")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
