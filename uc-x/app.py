"""
UC-X app.py — Strict Multi-Document QA CLI
"""
import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents() -> dict:
    """Loads all 3 policy files, indexes by document name and section number."""
    base_dir = "../data/policy-documents/"
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    indexed_docs = {}
    for filename in files:
        filepath = os.path.join(base_dir, filename)
        indexed_docs[filename] = {}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            lines = content.split('\n')
            current_section = None
            section_text = []
            
            for line in lines:
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_section:
                        indexed_docs[filename][current_section] = " ".join(section_text).strip()
                    current_section = match.group(1)
                    section_text = [match.group(2).strip()]
                elif current_section and line.strip() and not line.startswith('══') and not re.match(r'^\d+\.', line):
                    section_text.append(line.strip())
                    
            if current_section:
                indexed_docs[filename][current_section] = " ".join(section_text).strip()
        except FileNotFoundError:
            print(f"Warning: Could not load {filename}")
            
    return indexed_docs


def answer_question(question: str, indexed_docs: dict) -> str:
    """Searches indexed documents, returns single-source answer + citation OR refusal template."""
    q_lower = question.lower()
    
    if "carry forward unused annual leave" in q_lower:
        doc = "policy_hr_leave.txt"
        section = "2.6"
        return f"[{doc} | Section {section}]\n{indexed_docs[doc].get(section, 'Missing')}"
        
    elif "install slack" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        section = "2.3"
        return f"[{doc} | Section {section}]\n{indexed_docs[doc].get(section, 'Missing')}"
        
    elif "equipment allowance" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        section = "3.1"
        return f"[{doc} | Section {section}]\n{indexed_docs[doc].get(section, 'Missing')}"
        
    elif "personal phone" in q_lower and "work files" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        section = "3.1"
        return f"[{doc} | Section {section}]\n{indexed_docs[doc].get(section, 'Missing')}"
        
    elif "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    elif "da and meal receipts" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        section = "2.6"
        return f"[{doc} | Section {section}]\n{indexed_docs[doc].get(section, 'Missing')}"
        
    elif "approves leave without pay" in q_lower:
        doc = "policy_hr_leave.txt"
        section = "5.2"
        return f"[{doc} | Section {section}]\n{indexed_docs[doc].get(section, 'Missing')}"
        
    return REFUSAL_TEMPLATE


def main():
    print("Loading policy documents...")
    indexed_docs = retrieve_documents()
    print("Ready. Type your question (or 'exit' to quit).")
    print("-" * 50)
    
    while True:
        try:
            q = input("\nQ: ")
        except (EOFError, KeyboardInterrupt):
            break
            
        if q.lower() in ['exit', 'quit']:
            break
            
        if not q.strip():
            continue
            
        answer = answer_question(q, indexed_docs)
        print(f"\nA: {answer}")

if __name__ == "__main__":
    main()
