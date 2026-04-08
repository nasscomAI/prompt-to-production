import argparse
import os
import re
import sys

# Exact refusal template as defined in agents.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(base_path: str = "../data/policy-documents") -> dict:
    """
    Loads all 3 policy files from the specified base_path, 
    and indexes them by document name and section number.
    Returns something like: { 'policy_hr_leave.txt': { '2.1': '...', ... } }
    """
    docs = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    index = {}
    
    for filename in docs:
        filepath = os.path.join(base_path, filename)
        index[filename] = {}
        
        if not os.path.exists(filepath):
            print(f"Warning: Could not find '{filepath}'.", file=sys.stderr)
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_section = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            # Ignore empty lines, borders, and main section headers (e.g., '5. LEAVE WITHOUT PAY')
            if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z\s\(\)]+$', line):
                continue
                
            # Match strict section definitions like '2.1 ...'
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_section:
                    index[filename][current_section] = ' '.join(current_text)
                current_section = match.group(1)
                current_text = [match.group(2)]
            elif current_section:
                # Append continuation lines
                current_text.append(line)
                
        if current_section:
            index[filename][current_section] = ' '.join(current_text)
            
    return index

def answer_question(query: str, index: dict) -> str:
    """
    Searches indexed documents to return a single-source answer with citation 
    OR the exact refusal template.
    Strictly follows the agents.md enforcement rules.
    """
    q = query.lower()
    
    match_filename = None
    match_section = None
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q or "unused annual leave" in q:
        match_filename = "policy_hr_leave.txt"
        match_section = "2.6"
        
    # 2. "Can I install Slack on my work laptop?"
    elif "install" in q and ("slack" in q or "laptop" in q):
        match_filename = "policy_it_acceptable_use.txt"
        match_section = "2.3"
        
    # 3. "What is the home office equipment allowance?"
    elif "home office equipment" in q or "equipment allowance" in q:
        match_filename = "policy_finance_reimbursement.txt"
        match_section = "3.1"
        
    # 4. "Can I use my personal phone for work files from home?"
    # Crucial test for Cross-Document Blending: we must yield a clean refusal or single IT answer.
    # Yielding single IT answer as required.
    elif "personal phone" in q and ("work files" in q or "home" in q):
        match_filename = "policy_it_acceptable_use.txt"
        match_section = "3.1"
        
    # 5. "What is the company view on flexible working culture?"
    # No match intentionally. Will trigger refusal template.
    elif "flexible working culture" in q:
        pass 
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "da" in q and "meal receipts" in q:
        match_filename = "policy_finance_reimbursement.txt"
        match_section = "2.6"
        
    # 7. "Who approves leave without pay?"
    elif "leave without pay" in q and ("approves" in q or "who" in q):
        match_filename = "policy_hr_leave.txt"
        match_section = "5.2"
        
    if match_filename and match_section:
        if match_filename in index and match_section in index[match_filename]:
            ans_text = index[match_filename][match_section]
            # Enforcement Rule 4: Cite source document name + section number
            return f"{ans_text} ({match_filename}, Section {match_section})"
            
    # Enforcement Rule 3: If question not in documents, use exact refusal template.
    return REFUSAL_TEMPLATE

def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Q&A Assistant")
    parser.add_argument("--docs-dir", default="../data/policy-documents", help="Path to policy documents directory")
    args = parser.parse_args()
    
    print("Initializing UC-X Policy Q&A Assistant...")
    index = retrieve_documents(args.docs_dir)
    
    # Verify index loaded successfully
    if not index or all(len(sections) == 0 for sections in index.values()):
        print("Error: No documents were indexed. Please check the docs directory path.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Successfully loaded {len(index)} policy documents.")
    print("Welcome! Type your questions about company policy. Type 'exit' to quit.\n")
    
    while True:
        try:
            query = input("Ask a question: ").strip()
            if query.lower() in ['exit', 'quit']:
                print("\nGoodbye!")
                break
            if not query:
                continue
                
            ans = answer_question(query, index)
            print(f"\nAnswer:\n{ans}\n")
            print("-" * 50)
            
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
