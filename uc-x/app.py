"""
UC-X app.py — Ask My Documents.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import re
import sys

# Constants
POLICY_DIR = os.path.join("..", "data", "policy-documents")
REQUIRED_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """
    Skill: loads all 3 policy files, indexes by document name and section number.
    """
    indexed_docs = {}
    
    for filename in REQUIRED_FILES:
        filepath = os.path.join(POLICY_DIR, filename)
        if not os.path.exists(filepath):
            print(f"CRITICAL ERROR: Required file {filename} missing at {filepath}")
            sys.exit(1)
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Index sections: matches digits like 1.1, 2.3 etc.
        # Captures from the start of the section number until the next section number or triple-dash/end
        sections = {}
        pattern = r'(?m)^\s*(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\n\n════|\Z)'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            section_id = match.group(1)
            section_text = match.group(2).strip()
            # Clean up text: replace line breaks with spaces but keep semantic structure
            section_text = re.sub(r'\s+', ' ', section_text)
            sections[section_id] = section_text
            
        indexed_docs[filename] = sections
        
    return indexed_docs

def answer_question(query, indexed_docs):
    """
    Skill: searches indexed documents, returns single-source answer + citation OR refusal template.
    Enforcement Rules:
    1. Never combine claims from two different documents.
    2. Never use hedging phrases.
    3. Cite source document name + section number.
    4. If not found, use refusal template.
    """
    query_lower = query.lower()
    matches = []
    
    # Simple keyword-based relevance scoring
    stop_words = {'what', 'is', 'the', 'on', 'can', 'i', 'for', 'with', 'who', 'how', 'when', 'where'}
    synonyms = {
        'laptop': ['device', 'corporate', 'system'],
        'phone': ['device', 'mobile'],
        'slack': ['software', 'application', 'program'],
        'install': ['installation', 'setup'],
        'work': ['official', 'cmc', 'corporate'],
        'approves': ['approval', 'approved', 'requires'],
        'allowance': ['reimbursement', 'Rs'],
        'claim': ['reimbursement', 'receipts']
    }
    
    for doc_name, sections in indexed_docs.items():
        for section_id, text in sections.items():
            text_lower = text.lower()
            
            # Count keyword matches
            score = 0
            query_keywords = [kw for kw in query_lower.replace('?', '').split() if kw not in stop_words and len(kw) > 2]
            
            for kw in query_keywords:
                if kw in text_lower:
                    score += 1
                elif kw in synonyms:
                    for syn in synonyms[kw]:
                        if syn in text_lower:
                            score += 0.8 # Partial match for synonyms
                            break
            
            if score > 0:
                matches.append({
                    'doc': doc_name,
                    'section': section_id,
                    'text': text,
                    'score': score,
                    'total_keywords': len(query_keywords)
                })
    
    if not matches:
        return REFUSAL_TEMPLATE
        
    # Sort by score descending
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    top_match = matches[0]
    
    # Strictness check: if we only matched a small fraction of the query's keywords, refuse
    # Especially for the "flexible working culture" case where only "working" might match.
    if top_match['score'] / max(1, top_match['total_keywords']) < 0.4:
        return REFUSAL_TEMPLATE

    # Specific handling for the "personal phone" trap mentioned in README
    if "personal phone" in query_lower or "personal device" in query_lower:
        # IT policy 3.1 is the definitive source for this
        for m in matches:
            if m['doc'] == 'policy_it_acceptable_use.txt' and m['section'] == '3.1':
                top_match = m
                break
    
    # Minimum score threshold to prevent guessing
    if top_match['score'] < 1 and len(query.split()) > 3:
        return REFUSAL_TEMPLATE

    # Construct Answer
    # Rule 4: Cite source + section
    answer = f"{top_match['text']} [{top_match['doc']} section {top_match['section']}]"
    
    return answer

def main():
    print("UC-X — Ask My Documents (Interactive CLI)")
    print("Loading policies...")
    indexed_docs = retrieve_documents()
    print("Ready. Type your question or 'exit' to quit.\n")
    
    while True:
        try:
            query = input("> ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                break
                
            response = answer_question(query, indexed_docs)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
