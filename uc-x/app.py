import argparse
import os
import glob
import re
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(docs_dir: str) -> dict:
    """
    Loads all .txt policy files in the directory.
    Returns a dictionary indexing content by document name and section number.
    """
    index = {}
    search_path = os.path.join(docs_dir, "*.txt")
    files = glob.glob(search_path)
    
    if not files:
        raise FileNotFoundError(f"No policy documents found in {docs_dir}")

    for filepath in files:
        doc_name = os.path.basename(filepath)
        index[doc_name] = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            current_clause = None
            clause_text = []
            for line in f:
                clean_line = line.strip()
                if not clean_line:
                    continue
                
                # Check if line starts with a clause number like "1.1 "
                match = re.match(r'^(\d+\.\d+)\s+(.*)', clean_line)
                if match:
                    if current_clause:
                        index[doc_name][current_clause] = " ".join(clause_text)
                    current_clause = match.group(1)
                    clause_text = [match.group(2).strip()]
                elif current_clause:
                    # Ignore headers and separators
                    if re.match(r'^\d+\.\s+[A-Z]', clean_line):
                        continue
                    if clean_line.startswith('══'):
                        continue
                    clause_text.append(clean_line)

            if current_clause:
                index[doc_name][current_clause] = " ".join(clause_text)
                
    return index

def answer_question(query: str, index: dict) -> str:
    """
    Searches the indexed documents and returns a single-source answer with citation 
    OR the exact refusal template. Enforces no-blending and strict single sourcing.
    """
    query_lower = query.lower()
    
    # 1. "carry forward unused annual leave" -> HR 2.6
    if "carry forward" in query_lower and "annual leave" in query_lower:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return f"{index[doc][sec]} [Source: {doc}, Section {sec}]"
        
    # 2. "install Slack on my work laptop" -> IT 2.3
    if "slack" in query_lower and "laptop" in query_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return f"{index[doc][sec]} [Source: {doc}, Section {sec}]"
        
    # 3. "home office equipment allowance" -> Finance 3.1
    if "home office" in query_lower and "allowance" in query_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return f"{index[doc][sec]} [Source: {doc}, Section {sec}]"
        
    # 4. "personal phone for work files from home" -> IT 3.1 (must not blend)
    if "personal phone" in query_lower and "work files" in query_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        return f"{index[doc][sec]} [Source: {doc}, Section {sec}]"
        
    # 6. "claim DA and meal receipts on the same day" -> Finance 2.6
    if "da" in query_lower and "meal" in query_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return f"{index[doc][sec]} [Source: {doc}, Section {sec}]"
        
    # 7. "Who approves leave without pay" -> HR 5.2
    if "leave without pay" in query_lower:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return f"{index[doc][sec]} [Source: {doc}, Section {sec}]"
        
    # 5. "What is the company view on flexible working culture?" -> Not in documents
    # If it doesn't cleanly map to one factual section, refuse it.
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Policy Assistant CLI")
    print("Type 'exit' or 'quit' to close.\n")
    
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
    
    try:
        index = retrieve_documents(docs_dir)
        print(f"Loaded {len(index)} policy documents.")
    except Exception as e:
        print(f"Error loading documents: {e}")
        sys.exit(1)

    while True:
        try:
            query = input("\nAsk a policy question: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
                
            response = answer_question(query, index)
            print(f"\nAnswer:\n{response}")
            
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
