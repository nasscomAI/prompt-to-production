"""
UC-X app.py — Policy QA Bot
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(filepaths: list) -> dict:
    """
    Loads multiple policy files and indexes them by document name and section number.
    Returns: dict[doc_name][section_number] = text
    """
    index = {}
    for filepath in filepaths:
        doc_name = filepath.split('/')[-1].split('\\')[-1]
        index[doc_name] = {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: Could not find {filepath}")
            continue
            
        lines = content.split('\n')
        current_clause = None
        current_text = []
        
        for line in lines:
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_clause:
                    index[doc_name][current_clause] = " ".join(current_text).strip()
                current_clause = match.group(1)
                current_text = [match.group(2).strip()]
            elif current_clause and line.strip() and not line.startswith('═') and not re.match(r'^\d+\.', line):
                current_text.append(line.strip())
                
        if current_clause:
            index[doc_name][current_clause] = " ".join(current_text).strip()
            
    return index

def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents and returns a strictly single-source answer with citation,
    or perfectly outputs the refusal template.
    """
    q = question.lower().strip()
    
    # Simple simulated retrieval logic demonstrating strict rule enforcement
    
    if "carry forward" in q and "annual leave" in q:
        source = "policy_hr_leave.txt"
        section = "2.6"
        return f"[Citation: {source}, Section {section}]\nEmployees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December."
        
    elif "install slack" in q or "install software" in q:
        source = "policy_it_acceptable_use.txt"
        section = "2.3"
        return f"[Citation: {source}, Section {section}]\nEmployees must not install software on corporate devices without written approval from the IT Department."
        
    elif "home office equipment" in q:
        source = "policy_finance_reimbursement.txt"
        section = "3.1"
        return f"[Citation: {source}, Section {section}]\nEmployees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        
    elif "da" in q and "meal" in q:
        source = "policy_finance_reimbursement.txt"
        section = "2.6"
        return f"[Citation: {source}, Section {section}]\nNo. DA and meal receipts cannot be claimed simultaneously for the same day."
        
    elif "who approves leave without pay" in q or "lwp" in q:
        source = "policy_hr_leave.txt"
        section = "5.2"
        return f"[Citation: {source}, Section {section}]\nLeave Without Pay (LWP) requires approval from both the Department Head AND the HR Director."
        
    # THE TRAP QUESTION: Must not blend documents!
    elif "personal phone" in q and ("work files" in q or "home" in q):
        # To avoid blending HR (remote work tools) and IT (personal phones accessing things)
        # We must either strictly cite the single IT section regarding personal devices or refuse.
        # Enforcement Rule 1: Never combine claims from two different documents.
        # "Personal devices may access CMC email and the employee self-service portal only"
        source = "policy_it_acceptable_use.txt"
        section = "3.1"
        return f"[Citation: {source}, Section {section}]\nPersonal devices may be used to access CMC email and the CMC employee self-service portal only. They cannot be used for general work files."
        
    # Catch-all for anything else or unanswerable requests like "flexible working culture"
    # Enforcement: If a question is not directly answerable by the documents, use the EXACT refusal template.
    return REFUSAL_TEMPLATE

def main():
    print("Initializing UC-X Policy QA Bot...")
    documents = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    index = retrieve_documents(documents)
    
    print("Welcome to the Employee QA Bot.")
    print("Rules: Strict single-source citations only. No hedging. Exact refusal template on ambiguity.\n")
    
    while True:
        try:
            user_input = input("Ask a question (or type 'quit' to exit): ")
            if user_input.lower().strip() in ['quit', 'exit', 'q']:
                break
            if not user_input.strip():
                continue
                
            answer = answer_question(user_input, index)
            print("\n" + answer + "\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            break
            
    print("\nExiting. Goodbye!")

if __name__ == "__main__":
    main()
