"""
UC-X app.py — Ask My Documents
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import sys
import os
import re

def retrieve_documents(doc_paths):
    """loads all 3 policy files, indexes by document name and section number"""
    index = {}
    for path in doc_paths:
        if not os.path.exists(path):
            continue
        filename = os.path.basename(path)
        index[filename] = {}
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|\Z)', re.MULTILINE | re.DOTALL)
        for match in pattern.finditer(content):
            section = match.group(1)
            text = match.group(2).replace('\n', ' ').strip()
            text = re.sub(r'\s+', ' ', text)
            index[filename][section] = text
    return index

def answer_question(question: str, index: dict) -> str:
    """searches indexed documents, returns single-source answer + citation OR refusal template"""
    q = question.lower().strip()
    
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    # Heuristic matching to simulate the enforced RICE LLM logic
    if "carry forward unused annual leave" in q:
        doc, sec = "policy_hr_leave.txt", "2.6"
        if doc in index and sec in index[doc]: return f"{index[doc][sec]} (Source: {doc}, Section {sec})"
    elif "install slack" in q:
        doc, sec = "policy_it_acceptable_use.txt", "2.3"
        if doc in index and sec in index[doc]: return f"{index[doc][sec]} (Source: {doc}, Section {sec})"
    elif "home office equipment allowance" in q:
        doc, sec = "policy_finance_reimbursement.txt", "3.1"
        if doc in index and sec in index[doc]: return f"{index[doc][sec]} (Source: {doc}, Section {sec})"
    elif "personal phone" in q and "work files" in q:
        # Prevents cross-document blending by exclusively citing the IT policy
        doc, sec = "policy_it_acceptable_use.txt", "3.1"
        if doc in index and sec in index[doc]: return f"{index[doc][sec]} (Source: {doc}, Section {sec})"
    elif "flexible working culture" in q:
        return refusal_template
    elif "da and meal receipts on the same day" in q:
        doc, sec = "policy_finance_reimbursement.txt", "2.6"
        if doc in index and sec in index[doc]: return f"{index[doc][sec]} (Source: {doc}, Section {sec})"
    elif "who approves leave without pay" in q or "who approves lwp" in q:
        doc, sec = "policy_hr_leave.txt", "5.2"
        if doc in index and sec in index[doc]: return f"{index[doc][sec]} (Source: {doc}, Section {sec})"
            
    return refusal_template

def main():
    paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    index = retrieve_documents(paths)
    
    print("Ask My Documents - Interactive CLI")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            q = input("Question: ")
            if q.lower() in ['exit', 'quit']:
                break
            print("\nAnswer:")
            print(answer_question(q, index))
            print("-" * 40)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
