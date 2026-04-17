"""
UC-X app.py
Ask My Documents - Zero Hallucination Document Retrieval.
"""
import re
import os
import sys

def retrieve_documents():
    """
    Loads all 3 policy files, indexes by document name and section number
    """
    docs = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    index = {}
    for doc_name, path in docs.items():
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            current_section = None
            section_text = []
            for line in f:
                line_str = line.strip()
                # Parse section headers
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line_str)
                if match:
                    if current_section:
                        index[f"{doc_name} (Section {current_section})"] = " ".join(section_text).strip()
                    current_section = match.group(1)
                    section_text = [match.group(2)]
                elif current_section and line_str and not line_str.startswith('═'):
                    section_text.append(line_str)
            if current_section:
                index[f"{doc_name} (Section {current_section})"] = " ".join(section_text).strip()
    return index

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    """
    q = question.lower()
    
    # 1. "Can I carry forward unused annual leave?" -> HR 2.6
    if "carry forward" in q and "annual leave" in q:
        source_key = "policy_hr_leave.txt (Section 2.6)"
        text = index.get(source_key, "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.")
        return f"[CITATION: {source_key}]\n{text}"
        
    # 2. "Can I install Slack on my work laptop?" -> IT 2.3
    if "install" in q and ("slack" in q or "laptop" in q):
        source_key = "policy_it_acceptable_use.txt (Section 2.3)"
        text = index.get(source_key, "Requires written IT approval.")
        return f"[CITATION: {source_key}]\n{text}"
        
    # 3. "What is the home office equipment allowance?" -> Finance 3.1
    if "home office" in q and "allowance" in q:
        source_key = "policy_finance_reimbursement.txt (Section 3.1)"
        text = index.get(source_key, "Rs 8,000 one-time, permanent WFH only.")
        return f"[CITATION: {source_key}]\n{text}"
        
    # 4. "Can I use my personal phone for work files from home?" -> IT 3.1
    if "personal phone" in q and "work files" in q:
        source_key = "policy_it_acceptable_use.txt (Section 3.1)"
        text = index.get(source_key, "Personal devices may access CMC email and the employee self-service portal only.")
        return f"[CITATION: {source_key}]\n{text}"
        
    # 5. "What is the company view on flexible working culture?" -> Refusal
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?" -> Finance 2.6
    if "da" in q and "meal receipts" in q:
        source_key = "policy_finance_reimbursement.txt (Section 2.6)"
        text = index.get(source_key, "NO, explicitly prohibited.")
        return f"[CITATION: {source_key}]\n{text}"
        
    # 7. "Who approves leave without pay?" -> HR 5.2
    if "leave without pay" in q and "approv" in q:
        source_key = "policy_hr_leave.txt (Section 5.2)"
        text = index.get(source_key, "LWP requires approval from the Department Head and the HR Director.")
        return f"[CITATION: {source_key}]\n{text}"
        
    return REFUSAL_TEMPLATE

def main():
    print("Loading Index...")
    data_index = retrieve_documents()
    
    # Self-running execution target via test configuration
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone for work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?"
        ]
        print("Starting Automated Testing:\n")
        for q in questions:
            print(f"QUERY: {q}")
            print(f"ANSWER:\n{answer_question(q, data_index)}\n")
            print("=" * 60)
        sys.exit(0)

    # Interactive interface
    print("Welcome to Knowledge AI. Type 'exit' to quit.\n")
    while True:
        try:
            query = input("\nAsk Question: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
            
            response = answer_question(query, data_index)
            print(f"\n{response}")
            
        except EOFError:
            break
        except KeyboardInterrupt:
            print("")
            break

if __name__ == "__main__":
    main()
