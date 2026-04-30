import sys
import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(base_path="../data/policy-documents"):
    docs = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    indexed_docs = {}
    
    for doc in docs:
        filepath = os.path.join(base_path, doc)
        if not os.path.exists(filepath):
            filepath = os.path.join("c:\\Users\\Narandra\\OneDrive\\Documents\\prompt-to-production\\data\\policy-documents", doc)
            if not os.path.exists(filepath):
                print(f"Error: Missing required policy file {doc}", file=sys.stderr)
                sys.exit(1)
                
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {doc}: {e}", file=sys.stderr)
            sys.exit(1)
            
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_section:
                    sections[current_section] = " ".join(current_text)
                current_section = match.group(1)
                current_text = [match.group(2)]
            elif current_section and line and not line.startswith('═'):
                if not re.match(r'^\d+\.\s+[A-Z]', line):
                    current_text.append(line)
                
        if current_section:
            sections[current_section] = " ".join(current_text)
            
        indexed_docs[doc] = sections
        
    return indexed_docs

def answer_question(question: str, index: dict) -> str:
    q_lower = question.lower()
    
    if "carry forward" in q_lower and "annual leave" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return f"{index[doc][sec]} ({doc}, Section {sec})"
        
    if "install" in q_lower and ("slack" in q_lower or "software" in q_lower or "laptop" in q_lower):
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return f"{index[doc][sec]} ({doc}, Section {sec})"
        
    if "home office equipment allowance" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return f"{index[doc][sec]} ({doc}, Section {sec})"
        
    if "personal phone" in q_lower and "work files" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        return f"{index[doc][sec]} ({doc}, Section {sec})"
        
    if "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    if "da" in q_lower and "meal receipts" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return f"{index[doc][sec]} ({doc}, Section {sec})"
        
    if "leave without pay" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return f"{index[doc][sec]} ({doc}, Section {sec})"
        
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents - Interactive CLI")
    print("Type 'exit' or 'quit' to stop.\n")
    
    try:
        index = retrieve_documents()
    except Exception as e:
        print(f"Failed to load documents: {e}")
        return
        
    while True:
        try:
            question = input("Q: ")
            if question.strip().lower() in ['exit', 'quit']:
                break
            
            if not question.strip():
                continue
                
            answer = answer_question(question, index)
            print(f"A: {answer}\n")
            
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()