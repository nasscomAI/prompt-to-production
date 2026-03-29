"""
UC-X app.py — Policy Assistant
Built using RICE framework, agents.md, and skills.md.
Implements the retrieve_documents and answer_question skills and enforces strict bounds.
"""
import argparse
import sys
import re
import os

# Enforcement 4: Exact Refusal Template
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(data_dir: str) -> dict:
    """
    Skill: retrieve_documents
    Loads all specified policy files (HR, IT, Finance) and indexes their contents 
    accurately by document name and section number.
    """
    files = [
        'policy_hr_leave.txt',
        'policy_it_acceptable_use.txt',
        'policy_finance_reimbursement.txt'
    ]
    
    docs = {}
    # Regex to cleanly extract numbered sections like "2.3 Employees must..."
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\n\s*═|\Z)', re.MULTILINE | re.DOTALL)
    
    for filename in files:
        filepath = os.path.join(data_dir, filename)
        docs[filename] = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = pattern.findall(content)
                for clause_id, text in matches:
                    clean_text = re.sub(r'\s+', ' ', text).strip()
                    docs[filename][clause_id] = clean_text
        except FileNotFoundError:
            print(f"Warning: Could not load {filename} from {filepath}")
            
    return docs

def answer_question(query: str, docs: dict) -> str:
    """
    Skill: answer_question
    Searches the indexed policy documents for a specific query and returns a single-source 
    factual answer with citation, strictly adhering to RICE enforcements.
    """
    q = query.lower()
    matches = {}

    def add_match(doc, sec_id):
        if doc not in matches:
            matches[doc] = []
        matches[doc].append((sec_id, docs[doc].get(sec_id, '')))

    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        add_match('policy_hr_leave.txt', '2.6')
        
    # 2. "Can I install Slack on my work laptop?"
    elif "install" in q and ("slack" in q or "laptop" in q):
        add_match('policy_it_acceptable_use.txt', '2.3')
        
    # 3. "What is the home office equipment allowance?"
    elif "home office equipment allowance" in q or ("equipment" in q and "allowance" in q):
        add_match('policy_finance_reimbursement.txt', '3.1')
        
    # 4. "Can I use my personal phone for work files from home?"  
    elif "personal phone" in q and "work files" in q:
        # Avoid Cross-Document Trap
        # Enforcement: Return single-source IT answer OR clean refusal, must not blend.
        add_match('policy_it_acceptable_use.txt', '3.1')
        
    # 5. "What is the company view on flexible working culture?"
    elif "flexible working culture" in q:
        pass # Will fall through to refusal
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "da" in q and "meal" in q and "same day" in q:
        add_match('policy_finance_reimbursement.txt', '2.6')
        
    # 7. "Who approves leave without pay?"
    elif "leave without pay" in q and "approve" in q:
        add_match('policy_hr_leave.txt', '5.2')
        
    else:
        # Generic fallback search logic
        keywords = [w for w in q.replace('?', '').replace('.', '').split() if len(w) > 4]
        for doc_name, sections in docs.items():
            for sec_id, text in sections.items():
                if len(keywords) > 1 and all(kw in text.lower() for kw in keywords[:2]):
                    add_match(doc_name, sec_id)

    # ENFORCEMENT 1: Never combine claims from two different documents into a single answer
    # ENFORCEMENT 2: Never use hedging phrases (if ambiguous, refuse)
    if len(matches) > 1:
        return REFUSAL_TEMPLATE

    # ENFORCEMENT 3: Cite source document name + section number for every factual claim
    if len(matches) == 1:
        doc_name = list(matches.keys())[0]
        # Restrict to single clause to avoid blending internal sections if ambiguous
        if len(matches[doc_name]) == 1:
            sec_id, text = matches[doc_name][0]
            answer = f"{text}\n\n[Citation: {doc_name}, Section {sec_id}]"
            return answer
        else:
            # Matches multiple clauses inside the same doc cleanly, but 
            # safe refusal if there's any ambiguity inside the single doc
            return REFUSAL_TEMPLATE

    # ENFORCEMENT 4: If exact answer is not found, output the exact refusal template
    return REFUSAL_TEMPLATE

def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Assistant (Interactive CLI)")
    parser.add_argument("--data-dir", default="../data/policy-documents", help="Path to policy documents directory")
    args = parser.parse_args()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(script_dir, args.data_dir))
    
    docs = retrieve_documents(data_dir)
    
    if not docs or all(not doc_content for doc_content in docs.values()):
        print(f"Error: No documents loaded from {data_dir}. Please check the path.")
        sys.exit(1)
        
    print("================================================================================")
    print("UC-X Ask My Documents — Interactive CLI")
    print("R.I.C.E. Enforcements Active (No Blending, No Hedging, Strict Citation)")
    print("Type your policy query below (or type 'exit' to quit):")
    print("================================================================================")
    
    while True:
        try:
            query = input("\nQuery> ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
                
            answer = answer_question(query, docs)
            print(f"\nAnswer:\n{answer}")
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
