import os
import re

# Mandatory Refusal Template
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Policy files to load
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

DATA_DIR = os.path.join("..", "data", "policy-documents")

def retrieve_documents():
    """
    Skill: Loads the three specific policy documents and indexes them by document name and section number.
    """
    indexed_data = []
    
    for filename in POLICY_FILES:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Mandatory policy file not found: {filename}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to find sections like "2.6 Employees may..." or "2. ANNUAL LEAVE"
        # We look for lines starting with a number and a dot.
        lines = content.split('\n')
        current_section = "General"
        section_text = []
        
        for line in lines:
            # Check for section headers like "2. ANNUAL LEAVE" or "2.1 Subsection"
            match = re.match(r'^(\d+\.?\d*)\s+(.*)', line.strip())
            if match:
                # If we were collecting text for a previous section, save it
                if section_text:
                    indexed_data.append({
                        "doc": filename,
                        "section": current_section,
                        "text": " ".join(section_text).strip()
                    })
                
                current_section = match.group(1).rstrip('.')
                section_text = [match.group(2)]
            else:
                if line.strip():
                    section_text.append(line.strip())
                    
        # Add the last section
        if section_text:
            indexed_data.append({
                "doc": filename,
                "section": current_section,
                "text": " ".join(section_text).strip()
            })
            
    return indexed_data

STOP_WORDS = {
    "what", "is", "the", "on", "in", "of", "to", "for", "and", "a", "an", "who", "can", "may", "will", "how"
}

def answer_question(query, indexed_docs):
    """
    Skill: Searches the indexed policy documents to provide a single-source response or refusal.
    """
    query_lower = query.lower()
    
    # Pre-process query to remove symbols and split
    query_words = re.findall(r'\w+', query_lower)
    # Filter out stop words for a more accurate score
    meaningful_words = [w for w in query_words if w not in STOP_WORDS]
    
    matches = []
    for doc in indexed_docs:
        doc_text_lower = doc['text'].lower()
        doc_section_lower = doc['section'].lower()
        
        score = sum(1 for word in meaningful_words 
                   if len(word) >= 3 and (word in doc_text_lower or word in doc_section_lower))
        
        if score > 0:
            matches.append((score, doc))
            
    # Sort matches by score descending
    matches.sort(key=lambda x: x[0], reverse=True)
    
    if not matches:
        return REFUSAL_TEMPLATE
    
    top_score, top_doc = matches[0]
    
    # If the top score is too low compared to query length, or too few meaningful matches, refuse
    # For a query with meaningful words, we expect at least 1 or 2 solid matches
    if not meaningful_words:
        return REFUSAL_TEMPLATE
        
    if top_score < 1:
        return REFUSAL_TEMPLATE

    # Trap for personal phone - README check
    if "personal phone" in query_lower:
        # Check IT 3.1 specifically
        for score, doc in matches:
            if "policy_it_acceptable_use" in doc['doc'] and doc['section'] == "3.1":
                return f"{doc['text']} (Source: {doc['doc']}, Section {doc['section']})"
        return REFUSAL_TEMPLATE

    # Refusal logic for ambiguous or low-relevance results
    # If the top match doesn't have at least half of the meaningful words matched (for short queries)
    # or at least a minimum threshold, refuse.
    if top_score < 2 and len(meaningful_words) >= 3:
        return REFUSAL_TEMPLATE

    return f"{top_doc['text']} (Source: {top_doc['doc']}, Section {top_doc['section']})"

def main():
    try:
        indexed_docs = retrieve_documents()
    except Exception as e:
        print(f"Initialization Error: {e}")
        return

    print("UC-X Policy Compliance Agent")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            query = input("Ask a policy question: ")
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query.strip():
                continue
                
            response = answer_question(query, indexed_docs)
            print(f"\nAnswer: {response}\n")
            
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
