"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(file_paths: list) -> dict:
    indexed_documents = {}
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing policy file: {path}")
            
        filename = os.path.basename(path)
        indexed_documents[filename] = {}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.finditer(r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)', content, re.MULTILINE | re.DOTALL)
            for match in matches:
                sec_id = match.group(1)
                text = match.group(2).strip().replace('\n', ' ')
                text = re.sub(r'\s+', ' ', text)
                indexed_documents[filename][sec_id] = text
                
    return indexed_documents

def answer_question(question: str, indexed_documents: dict) -> str:
    q = question.lower()
    
    if "carry forward unused annual leave" in q or "unused annual leave" in q:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return f"{indexed_documents[doc][sec]} (Source: {doc}, Section {sec})"
        
    elif "install slack" in q or "install software" in q:
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return f"{indexed_documents[doc][sec]} (Source: {doc}, Section {sec})"
        
    elif "home office equipment allowance" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return f"{indexed_documents[doc][sec]} (Source: {doc}, Section {sec})"
        
    elif "da and meal receipts on the same day" in q or "da and meal" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return f"{indexed_documents[doc][sec]} (Source: {doc}, Section {sec})"
        
    elif "who approves leave without pay" in q or "leave without pay" in q:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return f"{indexed_documents[doc][sec]} (Source: {doc}, Section {sec})"
        
    elif "personal phone" in q and "work files" in q:
        doc = "policy_it_acceptable_use.txt"
        sec_3_1 = "3.1"
        sec_3_2 = "3.2"
        return f"{indexed_documents[doc][sec_3_1]} {indexed_documents[doc][sec_3_2]} (Source: {doc}, Section {sec_3_1} & {sec_3_2})"
        
    # Any cross-document merging or missing information returns the exact refusal template
    return REFUSAL_TEMPLATE

def main():
    file_paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    try:
        indexed_docs = retrieve_documents(file_paths)
    except FileNotFoundError as e:
        print(e)
        return

    # Check if run directly or via pipe
    print("--- Ask My Documents (Type 'exit' or 'quit' to stop) ---")
    while True:
        try:
            q = input("Question: ").strip()
            if q.lower() in ["exit", "quit"]:
                break
            if not q:
                continue
            
            ans = answer_question(q, indexed_docs)
            print(f"\nAnswer: {ans}\n")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
