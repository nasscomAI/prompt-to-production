import os
import re

# --- Configuration & Rules (from agents.md) ---
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# --- Document Processing Skills ---

def retrieve_documents():
    """
    Skill: retrieve_documents
    Loads policy files and indexes them by document and section.
    Returns a dictionary: { doc_name: { section_id: { 'title': str, 'content': str } } }
    """
    paths = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    
    index = {}
    # Regex to find sections like "2. ANNUAL LEAVE" followed by subsections like "2.1 ..."
    section_pattern = re.compile(r'^(\d+)\.\s+(.*)$')
    subsection_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)$')

    for doc_name, path in paths.items():
        if not os.path.exists(path):
            alt_path = os.path.join(os.path.dirname(__file__), path)
            if os.path.exists(alt_path): path = alt_path
            else: continue # Skip if file not found

        doc_sections = {}
        current_main_section = None
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Look for main sections (usually surrounded by ════)
                if i > 0 and "═══" in lines[i-1] and section_pattern.match(line):
                    match = section_pattern.match(line)
                    current_main_section = match.group(1)
                    i += 1 # Skip the header line and trailing ═══
                    continue
                
                # Look for subsections like 2.1, 2.2 etc.
                sub_match = subsection_pattern.match(line)
                if sub_match:
                    sec_id = sub_match.group(1)
                    content = sub_match.group(2)
                    # Collect multi-line content
                    while i + 1 < len(lines) and not subsection_pattern.match(lines[i+1].strip()) and "═══" not in lines[i+1]:
                        i += 1
                        content += " " + lines[i].strip()
                    doc_sections[sec_id] = content
                i += 1
        index[doc_name] = doc_sections
            
    return index

def answer_question(query, index):
    """
    Skill: answer_question
    Searches the index for keywords and returns a single-source answer with citation.
    Ensures no cross-document blending and avoids hedging.
    """
    query = query.lower()
    matches = []

    # Simple keyword extraction (remove common words)
    keywords = [w for w in re.findall(r'\w+', query) if len(w) > 3]
    
    for doc_name, sections in index.items():
        for sec_id, content in sections.items():
            # Check how many keywords match this section
            score = sum(1 for kw in keywords if kw in content.lower())
            if score > 0:
                matches.append({
                    'doc': doc_name,
                    'sec': sec_id,
                    'text': content,
                    'score': score
                })
    
    # Sort matches by score
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Filter for top score to avoid blending or ambiguity
    if not matches:
        return REFUSAL_TEMPLATE
        
    top_score = matches[0]['score']
    top_matches = [m for m in matches if m['score'] == top_score]
    
    # Rule 1: No cross-document blending. 
    # If top matches come from different documents, it's ambiguous -> Refusal.
    unique_docs = set(m['doc'] for m in top_matches)
    if len(unique_docs) > 1:
        return REFUSAL_TEMPLATE

    # Select the best section
    best = top_matches[0]
    
    # Citation rule (Rule 4)
    return f"{best['text']} (Source: {best['doc']} Section {best['sec']})"

# --- CLI ---

def main():
    print("Ask My Documents Policy Assistant (Rule-Based Engine)")
    try:
        index = retrieve_documents()
        if not index:
            print("Error: No documents found in ../data/policy-documents/")
            return
        print("Policies loaded. Type your question or 'exit'.")
    except Exception as e:
        print(f"Startup error: {e}")
        return

    while True:
        try:
            query = input("\nQuestion: ").strip()
        except EOFError:
            break
            
        if query.lower() in ['exit', 'quit']:
            break
        if not query:
            continue
            
        print(f"\nAnswer: {answer_question(query, index)}")

if __name__ == "__main__":
    main()


