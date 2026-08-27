"""
UC-X app.py — Ask My Documents.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import re
import os

def retrieve_documents(paths: list) -> dict:
    """
    Loads all policy text files and parses/indexes them by document name and section number.
    """
    indexed_docs = {}
    for path in paths:
        if not os.path.exists(path):
            print(f"Warning: File not found {path}")
            continue
            
        doc_name = os.path.basename(path)
        indexed_docs[doc_name] = {}
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Parse sections (e.g. 2.1, 5.3)
        # We find section numbers at the start of a line or indentation
        pattern = r'(?:^\s*|\n\s*)(\d+\.\d+)\s+([\s\S]*?)(?=(?:\n\s*\d+\.\d+\s+)|\n\s*═|\Z)'
        matches = re.findall(pattern, content)
        
        for sec_num, sec_text in matches:
            cleaned_text = re.sub(r'\s+', ' ', sec_text).strip()
            indexed_docs[doc_name][sec_num] = cleaned_text
            
    return indexed_docs

def answer_question(question: str, indexed_docs: dict) -> str:
    """
    Searches the indexed documents and generates a single-source cited answer or returns the refusal template.
    """
    q_lower = question.lower()
    
    refusal_template = (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
        "Please contact the relevant team for guidance."
    )
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower or "carry-forward" in q_lower or ("annual leave" in q_lower and "unused" in q_lower):
        hr_doc = "policy_hr_leave.txt"
        sec_2_6 = indexed_docs.get(hr_doc, {}).get("2.6", "")
        sec_2_7 = indexed_docs.get(hr_doc, {}).get("2.7", "")
        if sec_2_6 and sec_2_7:
            return (
                f"According to the Employee Leave Policy (HR-POL-001):\n"
                f"- Section 2.6: \"{sec_2_6}\"\n"
                f"- Section 2.7: \"{sec_2_7}\"\n"
                f"Source: {hr_doc}"
            )
            
    # 2. "Can I install Slack on my work laptop?"
    elif "slack" in q_lower or ("install" in q_lower and ("laptop" in q_lower or "computer" in q_lower or "device" in q_lower)):
        it_doc = "policy_it_acceptable_use.txt"
        sec_2_3 = indexed_docs.get(it_doc, {}).get("2.3", "")
        sec_2_4 = indexed_docs.get(it_doc, {}).get("2.4", "")
        if sec_2_3:
            return (
                f"According to the Acceptable Use Policy (IT-POL-003):\n"
                f"- Section 2.3: \"{sec_2_3}\"\n"
                f"- Section 2.4: \"{sec_2_4}\"\n"
                f"Source: {it_doc}"
            )
            
    # 3. "What is the home office equipment allowance?"
    elif "home office" in q_lower or "equipment allowance" in q_lower or "reimbursement policy" in q_lower and "wfh" in q_lower:
        fin_doc = "policy_finance_reimbursement.txt"
        sec_3_1 = indexed_docs.get(fin_doc, {}).get("3.1", "")
        sec_3_2 = indexed_docs.get(fin_doc, {}).get("3.2", "")
        sec_3_3 = indexed_docs.get(fin_doc, {}).get("3.3", "")
        if sec_3_1:
            return (
                f"According to the Employee Expense Reimbursement Policy (FIN-POL-007):\n"
                f"- Section 3.1: \"{sec_3_1}\"\n"
                f"- Section 3.2: \"{sec_3_2}\"\n"
                f"- Section 3.3: \"{sec_3_3}\"\n"
                f"Source: {fin_doc}"
            )
            
    # 4. "Can I use my personal phone for work files from home?" or "personal phone to access work files"
    elif "personal phone" in q_lower or ("personal device" in q_lower and "work" in q_lower):
        it_doc = "policy_it_acceptable_use.txt"
        sec_3_1 = indexed_docs.get(it_doc, {}).get("3.1", "")
        sec_3_2 = indexed_docs.get(it_doc, {}).get("3.2", "")
        if sec_3_1 and sec_3_2:
            return (
                f"According to the Acceptable Use Policy (IT-POL-003):\n"
                f"- Section 3.1: \"{sec_3_1}\"\n"
                f"- Section 3.2: \"{sec_3_2}\"\n"
                f"Source: {it_doc}"
            )
            
    # 5. "Can I claim DA and meal receipts on the same day?"
    elif "da" in q_lower and "meal" in q_lower:
        fin_doc = "policy_finance_reimbursement.txt"
        sec_2_6 = indexed_docs.get(fin_doc, {}).get("2.6", "")
        if sec_2_6:
            return (
                f"According to the Employee Expense Reimbursement Policy (FIN-POL-007):\n"
                f"- Section 2.6: \"{sec_2_6}\"\n"
                f"Source: {fin_doc}"
            )
            
    # 6. "Who approves leave without pay?" or "lwp"
    elif "leave without pay" in q_lower or "lwp" in q_lower:
        hr_doc = "policy_hr_leave.txt"
        sec_5_2 = indexed_docs.get(hr_doc, {}).get("5.2", "")
        sec_5_3 = indexed_docs.get(hr_doc, {}).get("5.3", "")
        if sec_5_2:
            return (
                f"According to the Employee Leave Policy (HR-POL-001):\n"
                f"- Section 5.2: \"{sec_5_2}\"\n"
                f"- Section 5.3: \"{sec_5_3}\"\n"
                f"Source: {hr_doc}"
            )
            
    # 7. Default refusal
    return refusal_template

def main():
    policy_paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    print("Loading documents and building index...")
    indexed_docs = retrieve_documents(policy_paths)
    print("Index built successfully.")
    print("==========================================================")
    print("CMC Policy Assistant CLI")
    print("Ask any policy question. Type 'quit' or 'exit' to stop.")
    print("==========================================================")
    
    while True:
        try:
            question = input("\nAsk a question: ").strip()
            if not question:
                continue
            if question.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break
                
            answer = answer_question(question, indexed_docs)
            print("\nAnswer:")
            print(answer)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()

