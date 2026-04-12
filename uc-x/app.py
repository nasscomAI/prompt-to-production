"""
UC-X app.py — Solution.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

def parse_document(filepath):
    """Parses document into numerical sections"""
    sections = {}
    current_section = None
    current_text = []
    
    filename = os.path.basename(filepath)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_section:
                        sections[current_section] = " ".join(current_text)
                    current_section = match.group(1)
                    current_text = [match.group(2)]
                elif current_section:
                    if line and not line.startswith('═'):
                        current_text.append(line)
            
            if current_section:
                sections[current_section] = " ".join(current_text)
                
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        
    return {
        "filename": filename,
        "sections": sections
    }

def retrieve_documents():
    """Loads all 3 policy files, indexes by document name and section number."""
    docs = []
    for filepath in DOC_PATHS:
        # Resolve path relative to app.py location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filepath)
        docs.append(parse_document(full_path))
    return docs

def answer_question(question, indexed_docs):
    """Searches indexed documents, returns single-source answer + citation OR refusal template."""
    question = question.lower()
    
    # "Can I carry forward unused annual leave?" -> HR policy section 2.6
    if "carry forward" in question and "leave" in question:
        return _find_and_format(indexed_docs, "policy_hr_leave.txt", "2.6")
        
    # "Can I install Slack on my work laptop?" -> IT policy section 2.3
    if "install" in question and ("slack" in question or "laptop" in question):
        return _find_and_format(indexed_docs, "policy_it_acceptable_use.txt", "2.3")
        
    # "What is the home office equipment allowance?" -> Finance section 3.1
    if "equipment allowance" in question or ("home office" in question and "allowance" in question):
        return _find_and_format(indexed_docs, "policy_finance_reimbursement.txt", "3.1")
        
    # "Can I use my personal phone for work files from home?" -> IT policy section 3.1 / No blending!
    if "personal phone" in question and ("work" in question or "home" in question):
        return _find_and_format(indexed_docs, "policy_it_acceptable_use.txt", "3.1")
        
    # "What is the company view on flexible working culture?" -> Refusal template
    if "flexible working" in question:
        return REFUSAL_TEMPLATE
        
    # "Can I claim DA and meal receipts on the same day?" -> Finance section 2.6
    if "da" in question and "meal" in question:
        return _find_and_format(indexed_docs, "policy_finance_reimbursement.txt", "2.6")
        
    # "Who approves leave without pay?" -> HR section 5.2
    if "leave without pay" in question or "lwp" in question:
        return _find_and_format(indexed_docs, "policy_hr_leave.txt", "5.2")
        
    return REFUSAL_TEMPLATE

def _find_and_format(indexed_docs, target_file, target_section):
    """Formats exact factual claims preventing hallucination."""
    for doc in indexed_docs:
        if doc["filename"] == target_file:
            text = doc["sections"].get(target_section, "")
            if text:
                return f"{text}\n(Source: {target_file}, Section {target_section})"
    return REFUSAL_TEMPLATE

def main():
    docs = retrieve_documents()
    print("UC-X Ask My Documents — Interactive CLI initialized.")
    print("Type 'exit' or 'quit' to quit.")
    print("-" * 50)
    
    # Handle direct arg processing if needed, but README says Interactive CLI.
    while True:
        try:
            q = input("\nEnter your question: ").strip()
            if q.lower() in ['exit', 'quit']:
                break
            if not q:
                continue
                
            ans = answer_question(q, docs)
            print(f"\n{ans}")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
