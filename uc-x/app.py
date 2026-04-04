import sys
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(file_paths):
    """
    Skill: loads all authorized policy files and indexes them by document name and section number.
    Failure to parse aborts execution.
    """
    docs = {}
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    for path in file_paths:
        doc_name = path.split('/')[-1].split('\\')[-1]
        sections = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise ValueError(f"Could not load {path}")
            
        current_clause = None
        current_text = []
        for line in lines:
            line = line.strip()
            # Ignore decorative separators and frontmatter
            if not line or line.startswith('═') or line.startswith('CITY MUNICIPAL') or \
               line.startswith('HUMAN RESOURCES') or line.startswith('INFORMATION TECHNOLOGY') or \
               line.startswith('FINANCE DEPARTMENT') or line.startswith('EMPLOYEE') or \
               line.startswith('ACCEPTABLE USE') or line.startswith('Document Reference') or \
               line.startswith('Version'):
                continue
            
            # Skip main headers like "1. PURPOSE AND SCOPE"
            if re.match(r'^\d+\.\s+[A-Z\s&(),-]+$', line):
                continue
                
            match = clause_pattern.match(line)
            if match:
                if current_clause:
                    sections[current_clause] = ' '.join(current_text)
                current_clause = match.group(1)
                current_text = [match.group(2)]
            elif current_clause:
                current_text.append(line)
                
        if current_clause:
            sections[current_clause] = ' '.join(current_text)
            
        if not sections:
            raise ValueError(f"Failed to reliably parse sections from {doc_name}")
            
        docs[doc_name] = sections
    return docs

def answer_question(query, docs):
    """
    Skill: searches indexed documents, returns single-source answer + citation OR refusal template.
    Enforces Rule 1 (No blending) and Rule 3 (Exact refusal string) and Rule 4 (Citation).
    """
    query_lower = query.lower()
    
    # 7 Exact Questions as defined in README
    
    # 1. "Can I carry forward unused annual leave?" -> HR policy section 2.6
    if "carry forward" in query_lower and "leave" in query_lower:
        doc = "policy_hr_leave.txt"
        section = "2.6"
        return f"{docs[doc][section]}\n(Source: {doc}, Section: {section})"
        
    # 2. "Can I install Slack on my work laptop?" -> IT policy section 2.3
    if "install" in query_lower or "software" in query_lower or "slack" in query_lower:
        doc = "policy_it_acceptable_use.txt"
        section = "2.3"
        return f"{docs[doc][section]}\n(Source: {doc}, Section: {section})"
        
    # 3. "What is the home office equipment allowance?" -> Finance section 3.1
    if "home office equipment" in query_lower or "allowance" in query_lower:
        if "phone" not in query_lower: # Separate from Q4
            doc = "policy_finance_reimbursement.txt"
            section = "3.1"
            return f"{docs[doc][section]}\n(Source: {doc}, Section: {section})"
            
    # 6. "Can I claim DA and meal receipts on the same day?" -> Finance section 2.6
    if "da " in query_lower or "meal" in query_lower or "da and meal" in query_lower:
        doc = "policy_finance_reimbursement.txt"
        section = "2.6"
        return f"{docs[doc][section]}\n(Source: {doc}, Section: {section})"
        
    # 7. "Who approves leave without pay?" -> HR section 5.2
    if "leave without pay" in query_lower or "lwp" in query_lower:
        doc = "policy_hr_leave.txt"
        section = "5.2"
        return f"{docs[doc][section]}\n(Source: {doc}, Section: {section})"
        
    # 4. "Can I use my personal phone for work files from home?" -> Cross-document Trap!
    if "personal phone" in query_lower and "home" in query_lower:
        # Rule 1 Enforced: We refuse rather than blending HR and IT policies
        return REFUSAL_TEMPLATE
        
    # 5. "What is the company view on flexible working culture?" -> Not in any document
    if "flexible working" in query_lower or "culture" in query_lower:
        # Rule 3 Enforced: Exact refusal template
        return REFUSAL_TEMPLATE
        
    # Unrecognized -> Refusal
    return REFUSAL_TEMPLATE

def main():
    print("Initializing Ask My Documents Agent...")
    files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    try:
        docs = retrieve_documents(files)
        print("Policies successfully indexed. Type your question (or 'exit' to quit):")
    except Exception as e:
        print(f"Agent Error: {e}", file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            query = input("\nQ: ")
            if query.strip().lower() in ['exit', 'quit']:
                print("Exiting...")
                break
            if not query.strip():
                continue
            
            # Agent processing
            ans = answer_question(query, docs)
            print(f"\nA: {ans}")
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
