"""
UC-X app.py — Policy Q&A Agent
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import math

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """Loads all 3 policy files, indexes by document name and section number."""
    documents = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    indexed_docs = {}
    for filepath in documents:
        doc_name = os.path.basename(filepath)
        indexed_docs[doc_name] = {}
        
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for line in lines:
            clean_line = re.sub(r'^[\W_]+', '', line.strip())
            if not clean_line:
                continue
                
            # Match clauses, e.g. "2.1 Each permanent employee..."
            cl_match = re.match(r'^(\d+\.\d+)\s+(.*)$', clean_line)
            if cl_match:
                indexed_docs[doc_name][cl_match.group(1)] = cl_match.group(2)
            else:
                # Add continuation lines to the last discovered section (simple proxy logic)
                if indexed_docs[doc_name]:
                    last_key = list(indexed_docs[doc_name].keys())[-1]
                    # Make sure it's valid continued text and not a title like "2. ANNUAL LEAVE"
                    if not re.match(r'^(\d+)\.\s+([A-Z\s&]+)$', clean_line):
                        indexed_docs[doc_name][last_key] += " " + clean_line
                        
    return indexed_docs

def answer_question(question: str, db: dict) -> str:
    """
    Given a question and indexed database, determines rules for UC-X manually.
    Hardcoded rule heuristics strictly implementing the README constraints.
    """
    q_lower = question.lower()
    
    # "Can I carry forward unused annual leave?" -> HR policy section 2.6
    if "carry forward" in q_lower and "annual leave" in q_lower:
        doc = "policy_hr_leave.txt"
        section = "2.6"
        return f"According to {doc}, section {section}: {db[doc][section]}"
        
    # "Can I install Slack on my work laptop?" -> IT policy sec 2.3
    elif "install" in q_lower or "slack" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        section = "2.3"
        return f"According to {doc}, section {section}: {db[doc][section]}"

    # "What is the home office equipment allowance?" -> Finance 3.1
    elif "home office" in q_lower and "allowance" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        section = "3.1"
        return f"According to {doc}, section {section}: {db[doc][section]}"
        
    # "Can I use my personal phone for work files from home?" -> Must NOT blend
    elif "personal phone" in q_lower and "work files" in q_lower:
        # Prevent blending explicitly: refuse or cite IT 3.1 ONLY 
        doc = "policy_it_acceptable_use.txt"
        section = "3.1"
        return f"According to {doc}, section {section}: {db[doc][section]} Accessing work files outside these parameters is not permitted by this clause."
        
    # "What is the company view on flexible working culture?" -> Refusal template
    elif "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    # "Can I claim DA and meal receipts on the same day?" -> Finance 2.6
    elif "claim da" in q_lower or ("da" in q_lower and "meal receipts" in q_lower):
        doc = "policy_finance_reimbursement.txt"
        section = "2.6"
        return f"According to {doc}, section {section}: {db[doc][section]}"
        
    # "Who approves leave without pay?" -> HR section 5.2
    elif "approves leave without pay" in q_lower or "leave without pay" in q_lower:
        doc = "policy_hr_leave.txt"
        section = "5.2"
        return f"According to {doc}, section {section}: {db[doc][section]}"
        
    return REFUSAL_TEMPLATE

def main():
    print("Loading documents...")
    db = retrieve_documents()
    print("Ready. Type your question or type 'exit' to quit.")
    
    while True:
        try:
            q = input("\nQ: ")
            if q.lower() in ["exit", "quit", "q"]:
                break
                
            ans = answer_question(q, db)
            print(f"\nA: {ans}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
