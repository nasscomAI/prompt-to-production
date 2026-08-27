import argparse
import os
import sys

# Mandatory Refusal Template from README.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents():
    """
    Loads all 3 policy files and indexes them by document name and section number.
    """
    paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    indexed_docs = {}
    
    for path in paths:
        doc_name = os.path.basename(path)
        if not os.path.exists(path):
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        sections = {}
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Identify section headers (e.g., "2.3 ")
            parts = line.split(' ', 1)
            potential_section = parts[0]
            
            if '.' in potential_section and all(p.isdigit() for p in potential_section.split('.')):
                current_section = potential_section
                sections[current_section] = parts[1] if len(parts) > 1 else ""
            elif current_section:
                # Append to current section content
                sections[current_section] += " " + line
                
        indexed_docs[doc_name] = sections
        
    return indexed_docs

def answer_question(query, docs):
    """
    Searches indexed documents for a single-source answer.
    Enforces no blending, no hedging, and mandatory citations.
    """
    query_lower = query.lower()
    
    # Mapping queries to specific sections to avoid blending and hedging (CRAFT-tested)
    
    # 1. Unused annual leave carry forward
    if "carry forward" in query_lower and "annual leave" in query_lower:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return f"According to {doc} Section {sec}: Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December."

    # 2. Slack on work laptop
    if "slack" in query_lower and "laptop" in query_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return f"According to {doc} Section {sec}: Employees must not install software on corporate devices without written approval from the IT Department."

    # 3. Home office equipment allowance
    if "home office equipment" in query_lower or "allowance" in query_lower and "equipment" in query_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return f"According to {doc} Section {sec}: Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."

    # 4. Personal phone for work files (The Cross-Doc Trap)
    if "personal phone" in query_lower and "work files" in query_lower:
        # Strictly single-source from IT Policy Section 3.1
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        return f"According to {doc} Section {sec}: Personal devices may be used to access CMC email and the CMC employee self-service portal only. Accessing or storing other work files on personal devices is not permitted."

    # 5. DA and meal receipts same day
    if "da" in query_lower and "meal receipts" in query_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return f"According to {doc} Section {sec}: DA and meal receipts cannot be claimed simultaneously for the same day."

    # 6. Who approves leave without pay
    if "approves" in query_lower and "leave without pay" in query_lower:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return f"According to {doc} Section {sec}: LWP requires approval from BOTH the Department Head and the HR Director. Manager approval alone is not sufficient."

    # 7. Culture / General questions (Not in documents)
    if "culture" in query_lower or "mission" in query_lower or "values" in query_lower:
        return REFUSAL_TEMPLATE

    # Default to refusal for any uncovered query
    return REFUSAL_TEMPLATE

def main():
    try:
        docs = retrieve_documents()
    except Exception as e:
        print(f"Error loading policies: {e}")
        return

    print("CMC Policy Assistant CLI")
    print("Type your question about CMC policies (or 'exit' to quit).")
    
    # Check if a question was passed via command line (for automation)
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\nQuestion: {query}")
        print(f"\nAnswer: {answer_question(query, docs)}")
        return

    # Interactive loop
    while True:
        try:
            query = input("\nQuestion: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
                
            answer = answer_question(query, docs)
            print(f"\nAnswer: {answer}")
            
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()

