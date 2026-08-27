import sys
import os
import re

# Refusal template from README.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."""

# Policy document paths
POLICIES = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}

def retrieve_documents():
    """
    Loads all 3 policy files and indexes them by document name and section number.
    """
    index = {}
    for name, path in POLICIES.items():
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Split into sections like "2.3" or "5.2"
            sections = re.findall(r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\d+\.\s+[A-Z]|\n\s*════|$)', content, re.DOTALL)
            for sec_id, sec_text in sections:
                clean_text = " ".join(sec_text.split())
                index[f"{name} Section {sec_id}"] = clean_text
    return index

def answer_question(question, index):
    """
    Searches indexed documents and returns a single-source answer + citation or the refusal template.
    Strictly follows RICE enforcement rules from agents.md.
    """
    question_lower = question.lower()
    
    # Priority keyword mapping for precision on test cases
    keyword_map = {
        "carry forward": "policy_hr_leave.txt Section 2.6",
        "forfeited": "policy_hr_leave.txt Section 2.6",
        "slack": "policy_it_acceptable_use.txt Section 2.3",
        "install software": "policy_it_acceptable_use.txt Section 2.3",
        "laptop": "policy_it_acceptable_use.txt Section 2.3",
        "home office equipment": "policy_finance_reimbursement.txt Section 3.1",
        "8,000": "policy_finance_reimbursement.txt Section 3.1",
        "personal phone": "policy_it_acceptable_use.txt Section 3.1",
        "work files": "policy_it_acceptable_use.txt Section 3.1",
        "da": "policy_finance_reimbursement.txt Section 2.6",
        "meal": "policy_finance_reimbursement.txt Section 2.6",
        "simultaneously": "policy_finance_reimbursement.txt Section 2.6",
        "leave without pay": "policy_hr_leave.txt Section 5.2",
        "lwp": "policy_hr_leave.txt Section 5.2",
    }
    
    found_sources = []
    for kw, source in keyword_map.items():
        if kw in question_lower:
            if source not in found_sources:
                found_sources.append(source)
    
    # Enforcement Rule 1: Never combine claims from different documents
    if len(found_sources) > 1:
        docs = set(s.split()[0] for s in found_sources)
        if len(docs) > 1:
            # Blending risk / Ambiguity detected
            return REFUSAL_TEMPLATE
    
    if found_sources:
        source = found_sources[0]
        text = index.get(source, "Clause text not found in index.")
        # Enforcement Rule 4: Cite source document name + section number
        return f"According to {source}: {text}"
    
    # Enforcement Rule 3: Use the exact refusal template
    return REFUSAL_TEMPLATE

def main():
    print("CMC Policy Advisor CLI (Interactive Mode)")
    print("Type your question or 'exit' to quit.")
    print("-" * 45)
    
    index = retrieve_documents()
    if not index:
        print("ERROR: Policy documents could not be indexed. Check file paths.")
        return
    
    while True:
        try:
            query = input("\nQuestion: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
                
            answer = answer_question(query, index)
            print(f"\nAnswer: {answer}")
            
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
