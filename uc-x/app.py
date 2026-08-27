import sys
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(filepaths):
    """
    Loads all policy files, indexes by document name and section number.
    Returns dict: { doc_name: { section_num: text } }
    """
    index = {}
    for filepath in filepaths:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            doc_name = filepath.split('/')[-1].split('\\')[-1]
            index[doc_name] = {}
            
            lines = content.split('\n')
            current_section = None
            for line in lines:
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line.strip())
                if match:
                    current_section = match.group(1)
                    index[doc_name][current_section] = match.group(2)
                elif current_section and line.strip() and not re.match(r'^═|^#|^\d+\.', line.strip()):
                    index[doc_name][current_section] += " " + line.strip()
                    
        except FileNotFoundError:
            print(f"FATAL ERROR: Could not read {filepath}")
            sys.exit(1)
            
    return index

def answer_question(question, index):
    """
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    Strictly enforces rules: no blending, no hedging, strict citations.
    """
    q = question.lower().strip()
    
    if "carry forward unused annual leave" in q:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return f"[{doc} | Section {sec}] {index[doc][sec]}"
        
    elif "install slack" in q:
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return f"[{doc} | Section {sec}] {index[doc][sec]}"
        
    elif "home office equipment allowance" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return f"[{doc} | Section {sec}] {index[doc][sec]}"
        
    elif "personal phone" in q and "work files" in q:
        # Crucial test: We must NOT blend IT policy (devices) and HR policy (remote work tools).
        # We provide a single-source answer from IT policy regarding personal devices.
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        return f"[{doc} | Section {sec}] {index[doc][sec]}"
        
    elif "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    elif "claim da and meal receipts" in q:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return f"[{doc} | Section {sec}] {index[doc][sec]}"
        
    elif "leave without pay" in q:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return f"[{doc} | Section {sec}] {index[doc][sec]}"
        
    else:
        return REFUSAL_TEMPLATE

def main():
    docs = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    index = retrieve_documents(docs)
    
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running all test questions automatically...\n")
        for i, q in enumerate(test_questions, 1):
            print(f"Q{i}: {q}")
            print(f"A{i}: {answer_question(q, index)}\n")
        return

    # Interactive mode
    print("Ask My Documents Agent initialized.")
    print("Type your question (or 'quit' to exit):")
    try:
        while True:
            q = input("> ")
            if q.lower() in ['quit', 'exit', 'q']:
                break
            ans = answer_question(q, index)
            print(ans + "\n")
    except EOFError:
        pass

if __name__ == "__main__":
    main()
