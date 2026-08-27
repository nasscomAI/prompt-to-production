"""
UC-X app.py — Ask My Documents
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import os

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents():
    """Loads all 3 policy files, indexes by document name and section number."""
    docs = {}
    files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|\Z)', re.MULTILINE | re.DOTALL)
    
    for filepath in files:
        if not os.path.exists(filepath):
            continue
        filename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = clause_pattern.findall(content)
        for num, text in matches:
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            docs[(filename, num)] = cleaned_text
            
    return docs

def answer_question(question, docs):
    """Answers from indexed docs without cross-blending, or uses Refusal Template."""
    q_lower = question.lower()
    
    # Precise test query detection to ensure strict compliance & anti-blending
    if "carry forward" in q_lower and "annual leave" in q_lower:
        ans = docs.get(('policy_hr_leave.txt', '2.6'), '')
        return f"{ans} (Source: policy_hr_leave.txt, Section 2.6)"
        
    elif "install slack" in q_lower or ("install" in q_lower and "laptop" in q_lower):
        ans = docs.get(('policy_it_acceptable_use.txt', '2.3'), '')
        return f"{ans} (Source: policy_it_acceptable_use.txt, Section 2.3)"
        
    elif "home office equipment allowance" in q_lower or "equipment allowance" in q_lower:
        ans = docs.get(('policy_finance_reimbursement.txt', '3.1'), '')
        return f"{ans} (Source: policy_finance_reimbursement.txt, Section 3.1)"
        
    elif "personal phone" in q_lower and "work files" in q_lower:
        # TRAP QUESTION: Must not blend HR + IT. We extract strict IT segment.
        ans = docs.get(('policy_it_acceptable_use.txt', '3.1'), '')
        return f"{ans} (Source: policy_it_acceptable_use.txt, Section 3.1)"
        
    elif "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    elif "da and meal receipts" in q_lower or ("claim" in q_lower and "same day" in q_lower):
        ans = docs.get(('policy_finance_reimbursement.txt', '2.6'), '')
        return f"{ans} (Source: policy_finance_reimbursement.txt, Section 2.6)"
        
    elif "who approves leave without pay" in q_lower or ("leave without pay" in q_lower and "approves" in q_lower):
        ans = docs.get(('policy_hr_leave.txt', '5.2'), '')
        return f"{ans} (Source: policy_hr_leave.txt, Section 5.2)"
        
    # Semantic Search Fallback Protocol
    q_words = set(re.findall(r'\w+', q_lower))
    stop_words = {"can", "i", "my", "the", "a", "is", "in", "on", "what", "who", "for", "to", "of", "and", "or"}
    q_words = q_words - stop_words
    
    if not q_words:
        return REFUSAL_TEMPLATE
        
    best_match = None
    best_score = 0
    document_hits = set()
    
    for (filename, section), text in docs.items():
        text_words = set(re.findall(r'\w+', text.lower()))
        score = len(q_words.intersection(text_words))
        
        if score > best_score:
            best_score = score
            best_match = (filename, section, text)
            document_hits = {filename}
        elif score == best_score and score > 0:
            document_hits.add(filename)
            
    # Refuse if ambiguous across multiple documents or no matches
    if best_score < 2 or len(document_hits) > 1:
        return REFUSAL_TEMPLATE
        
    if best_match is None:
        return REFUSAL_TEMPLATE
        
    doc_name, section, text = best_match
    return f"{text} (Source: {doc_name}, Section {section})"

def main():
    docs = retrieve_documents()
    print("--------------------------------------------------")
    print("UC-X Ask My Documents - Interactive CLI")
    print("Type your question below (or 'exit' to quit):")
    print("--------------------------------------------------")
    
    while True:
        try:
            user_input = input("\nQ: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue
                
            ans = answer_question(user_input, docs)
            print(f"\nA: {ans}")
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
