"""
UC-X — Policy Retrieval System
Built using R.I.C.E. framework + agents.md + skills.md
"""
import os
import re

# Mandatory refusal template from agents.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

def retrieve_documents():
    """
    Skill: Loads policy document files and parses them into a searchable index 
    by document name and section number.
    """
    # Base path relative to app.py as specified in README
    base_path = "../data/policy-documents"
    doc_names = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    index = {}
    
    # Try different base paths based on common execution contexts
    paths_to_try = [
        base_path,
        os.path.join(os.getcwd(), "data/policy-documents"),
        os.path.join(os.path.dirname(os.getcwd()), "data/policy-documents"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/policy-documents") # In case of nested structure
    ]
    
    actual_path = None
    for p in paths_to_try:
        if os.path.exists(p) and any(os.path.exists(os.path.join(p, d)) for d in doc_names):
            actual_path = p
            break
            
    if not actual_path:
        return {}

    # Cast to str for linter peace of mind
    base_dir: str = str(actual_path)

    for doc_name in doc_names:
        full_path = os.path.join(base_dir, doc_name)
        if not os.path.exists(full_path):
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                index[doc_name] = parse_sections(content)
        except Exception:
            # Silent failure for individual files, main loop handles empty index
            continue
            
    return index

def parse_sections(content):
    """
    Helper to extract sections labeled with X.Y numbering.
    """
    sections = {}
    lines = content.split('\n')
    current_section_id = None
    section_text = []

    for line in lines:
        # Match lines starting with numbering like "2.6  Text..."
        match = re.match(r'^\s*(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_section_id:
                sections[current_section_id] = " ".join(section_text).strip()
            
            current_section_id = match.group(1)
            section_text = [match.group(2).strip()]
        elif current_section_id:
            clean_line = line.strip()
            # Ignore separators like ═ or ─
            if clean_line and not re.match(r'^[═─]{3,}$', clean_line):
                section_text.append(clean_line)
    
    if current_section_id:
        sections[current_section_id] = " ".join(section_text).strip()
        
    return sections

def answer_question(query, index):
    """
    Skill: Searches the indexed documents to find a single-source answer 
    for the user query, including the section citation.
    """
    if not query or not index:
        return REFUSAL_TEMPLATE

    query_lower = query.lower()
    # Simple keyword extraction
    keywords = set(re.findall(r'\b[a-z]{3,}\b', query_lower))
    
    candidates = []
    
    for doc_name, sections in index.items():
        for sec_id, text in sections.items():
            text_lower = text.lower()
            match_count: int = 0
            for kw in keywords:
                if kw in text_lower:
                    match_count = match_count + 1
            
            if match_count > 0:
                candidates.append({
                    'doc': doc_name,
                    'sec': sec_id,
                    'text': text,
                    'score': match_count
                })
    
    if not candidates:
        return REFUSAL_TEMPLATE
        
    # Sort by score primarily
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    best = candidates[0]
    
    # Requirement: Single-Source Truth & No Blending.
    # If the top answer is very weak (less than 2 keywords or significant mismatch), refuse.
    if best['score'] < 2:
        return REFUSAL_TEMPLATE
        
    # Requirement: Prohibit blending across documents.
    # If there are candidates from DIFFERENT documents with high scores, check if they conflict.
    # For this implementation, we strictly return the single highest-scoring section.
    # If there's a tie across documents, it's ambiguous, so we refuse.
    if len(candidates) > 1:
        second = candidates[1]
        if second['doc'] != best['doc'] and second['score'] == best['score']:
            return REFUSAL_TEMPLATE

    # Requirement: Cite source document name + section number.
    citation = f"[{best['doc']}, Section {best['sec']}]"
    
    # Requirement: No hedging phrases (ensured by returning direct text).
    return f"{best['text']}\n\nSource: {citation}"

def main():
    index = retrieve_documents()
    
    print("UC-X — AI Policy Retrieval Assistant")
    print("Type 'exit' or 'quit' to close.")
    print("-" * 40)
    
    if not index:
        print("Warning: Policy document repository is empty or inaccessible.")

    while True:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                break
                
            response = answer_question(user_input, index)
            print(f"\n{response}")
            
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
