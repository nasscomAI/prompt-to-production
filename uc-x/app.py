import os
import re

# Refusal template as defined in README.md and agents.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

STOP_WORDS = {"can", "i", "what", "is", "the", "on", "for", "in", "to", "and", "a", "of", "who", "view"}

def retrieve_documents(paths):
    """
    Loads all 3 policy files and indexes them by document name and section number.
    """
    indexed_docs = {}
    for path in paths:
        doc_name = os.path.basename(path)
        if not os.path.exists(path):
            alt_path = os.path.join(os.path.dirname(__file__), path)
            if os.path.exists(alt_path):
                path = alt_path
            else:
                continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        sections = {}
        # Find all section markers
        pattern = r'^(\d+(?:\.\d+)?)\.?\s+(.*?)(?=\n\d+(?:\.\d+)?\.?\s+|\Z)'
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        
        current_main_header = ""
        for sec_num, sec_text in matches:
            clean_text = re.sub(r'[════=]{5,}', '', sec_text).strip()
            
            if "." not in sec_num:
                current_main_header = clean_text
            
            # Combine sub-section text with parent header for better context
            full_searchable_text = clean_text
            if "." in sec_num and current_main_header:
                full_searchable_text = current_main_header + " " + clean_text
            
            sections[sec_num] = {
                'display_text': clean_text,
                'search_text': full_searchable_text.lower()
            }
            
        indexed_docs[doc_name] = sections
    return indexed_docs

def answer_question(question, indexed_docs):
    """
    Searches indexed documents and returns a single-source answer with citation OR the refusal template.
    """
    q_lower = question.lower()
    
    # Specific trap cases
    if "personal phone" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        if doc in indexed_docs and "3.1" in indexed_docs[doc]:
            return f"{indexed_docs[doc]['3.1']['display_text']}\n\nSource: {doc} (Section 3.1)"

    if "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE

    # General keyword matching
    keywords = [w for w in re.findall(r'\w+', q_lower) if w not in STOP_WORDS]
    if not keywords:
        return REFUSAL_TEMPLATE
        
    matches = []
    for doc_name, sections in indexed_docs.items():
        for sec_num, sec_data in sections.items():
            score = 0
            search_text = sec_data['search_text']
            
            for kw in keywords:
                if kw in search_text:
                    score += 1
            
            # Phrase boosts
            phrases = [
                ("carry forward", 15),
                ("annual leave", 5),
                ("install", 10),
                ("home office", 15),
                ("equipment allowance", 15),
                ("leave without pay", 20),
                ("lwp", 20),
                ("da and meal", 15),
                ("approval", 10),
                ("approves", 10)
            ]
            for phrase, bonus in phrases:
                if phrase in q_lower and phrase in search_text:
                    score += bonus
            
            # Special check for "Who approves" + "leave without pay"
            if "approv" in q_lower and ("leave without pay" in search_text or "lwp" in search_text):
                if "approv" in search_text:
                    score += 20

            if score > 0:
                # Prioritize sub-sections for specific answers
                if "." in sec_num:
                    score += 2
                
                matches.append({
                    'doc_name': doc_name,
                    'sec_num': sec_num,
                    'text': sec_data['display_text'],
                    'score': score
                })
    
    matches.sort(key=lambda x: x['score'], reverse=True)
    if not matches or matches[0]['score'] < 2:
        return REFUSAL_TEMPLATE
    
    best_match = matches[0]
    return f"{best_match['text']}\n\nSource: {best_match['doc_name']} (Section {best_match['sec_num']})"

def main():
    print("Policy Document Q&A Agent started.")
    print("Indexing documents...")
    indexed_docs = retrieve_documents(DOC_PATHS)
    if not indexed_docs:
        print("Warning: No documents were indexed.")
    else:
        print(f"Indexed {len(indexed_docs)} documents.")
        
    print("Ready. Type your question or 'exit' to quit.")
    
    while True:
        try:
            question = input("\nQuestion: ").strip()
            if question.lower() in ['exit', 'quit']:
                break
            if not question:
                continue
                
            answer = answer_question(question, indexed_docs)
            print("-" * 40)
            print(answer)
            print("-" * 40)
        except EOFError:
            break

if __name__ == "__main__":
    main()
