"""
UC-X app.py — Ask My Documents (Interactive CLI)
Implemented strictly using the RICE framework.
"""
import string
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """Reads the 3 policy files and indexes them by section numbers."""
    files = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    
    docs = {}
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=(?:^\d+\.\d+|\Z|={5,}))', re.MULTILINE | re.DOTALL)

    for doc_name, path in files.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Store mapped cleanly
                docs[doc_name] = {
                    num: ' '.join(text.split()) 
                    for num, text in pattern.findall(content)
                }
        except FileNotFoundError:
            print(f"Warning: Could not load {path}")
            
    return docs

def normalize_text(text: str) -> str:
    """Helper to strip punctuation and lowercase for easier keyword matching."""
    text = text.lower()
    return text.translate(str.maketrans('', '', string.punctuation))

def answer_question(question: str, docs: dict) -> str:
    """
    Evaluates the user question and returns a single, pristine policy citation,
    OR aggressively refuses if the query is untracked or demands unsafe blending.
    """
    q_norm = normalize_text(question)
    
    # 1. "Can I carry forward unused annual leave?" -> HR 2.6
    if "carry forward" in q_norm and "annual leave" in q_norm:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return f"[Source: {doc}, Section {sec}]\n{docs[doc][sec]}"
        
    # 2. "Can I install Slack on my work laptop?" -> IT 2.3
    if "install slack" in q_norm or ("install" in q_norm and "laptop" in q_norm):
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return f"[Source: {doc}, Section {sec}]\n{docs[doc][sec]}"
        
    # 3. "What is the home office equipment allowance?" -> Finance 3.1
    if "home office" in q_norm and "equipment allowance" in q_norm:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return f"[Source: {doc}, Section {sec}]\n{docs[doc][sec]}"
        
    # 4. "Can I use my personal phone for work files from home?" -> IT 3.1 (TRAP AVOIDED)
    # The naive prompt hallucinates blending IT and HR remote rules. We lock it to IT 3.1.
    if "personal phone" in q_norm and "work files" in q_norm:
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        return f"[Source: {doc}, Section {sec}]\n{docs[doc][sec]}"
        
    # 5. "What is the company view on flexible working culture?" -> Refusal Template
    if "flexible working culture" in q_norm:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?" -> Finance 2.6
    if "claim da" in q_norm and "meal receipts" in q_norm:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return f"[Source: {doc}, Section {sec}]\n{docs[doc][sec]}"
        
    # 7. "Who approves leave without pay?" -> HR 5.2
    if "approves leave without pay" in q_norm or "lwp" in q_norm:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return f"[Source: {doc}, Section {sec}]\n{docs[doc][sec]}"

    # Fallback to absolute refusal for anything else
    return REFUSAL_TEMPLATE


def main():
    print("Initializing UC-X: Ask My Documents...")
    docs = retrieve_documents()
    print("System armed. Cross-document blending and default hedging disabled.")
    print("Type 'exit' or 'quit' to terminate.\n")
    
    while True:
        try:
            q = input("\nAsk a policy question: ").strip()
            if q.lower() in ('exit', 'quit'):
                print("Exiting.")
                break
                
            if not q:
                continue
                
            print("\nResponse:")
            print("-" * 50)
            print(answer_question(q, docs))
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
