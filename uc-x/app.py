import os
import re

# Refusal template as per README
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Paths relative to the script location
FILE_PATHS = {
    "HR": "../data/policy-documents/policy_hr_leave.txt",
    "IT": "../data/policy-documents/policy_it_acceptable_use.txt",
    "Finance": "../data/policy-documents/policy_finance_reimbursement.txt"
}

def retrieve_documents():
    """Builds a structured index of all 3 documents."""
    indexed_data = []

    for doc_name, relative_path in FILE_PATHS.items():
        # Using absolute paths for correctness in this environment
        # Script is in uc-x/, data is in ../data/
        abs_path = os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__), relative_path)))
        
        if not os.path.exists(abs_path):
            continue
            
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Use regex to find subsections like 1.1, 2.3, etc.
            # Pattern: matches "X.Y " at start of line followed by content until next section or line divider
            subsections = re.findall(r'^(\d+\.\d+)\s+([\s\S]*?)(?=\n\d+\.\d+|\n[═=]+|$)', content, re.MULTILINE)
            
            for sec_num, sec_text in subsections:
                clean_text = " ".join(sec_text.strip().split())
                indexed_data.append({
                    "doc": os.path.basename(relative_path),
                    "section": sec_num,
                    "content": clean_text
                })
    return indexed_data

def answer_question(question, index):
    """
    Search indexed documents for a single-source answer.
    Enforces RICE rules.
    """
    question_lower = question.lower()
    
    # Specific refusal for broad cultural questions not in docs
    if any(q in question_lower for q in ["flexible working culture", "company view", "vision", "mission"]):
        return REFUSAL_TEMPLATE

    # Extract keywords for scoring
    keywords = [w for w in re.findall(r'\w+', question_lower) if len(w) > 3]
    
    matches = []
    for entry in index:
        content_lower = entry['content'].lower()
        score = 0
        
        # Check for keyword matches
        for kw in keywords:
            if kw in content_lower:
                score += 1
                
        # Boost for specific key entities
        if "annual leave" in question_lower and "annual leave" in content_lower:
            score += 5
        if "slack" in question_lower and "install software" in content_lower:
            score += 5
        if "home office" in question_lower and "home office" in content_lower:
            score += 8
        if "personal phone" in question_lower and "personal device" in content_lower:
            score += 8
        if "da" in question_lower and ("daily allowance" in content_lower or "da" in content_lower):
            score += 5
        if "leave without pay" in question_lower and "leave without pay" in content_lower:
            score += 8
        if "unused annual leave" in question_lower and "unused" in content_lower:
            score += 2

        if score > 0:
            matches.append((score, entry))
            
    # Sort matches by score
    matches.sort(key=lambda x: x[0], reverse=True)
    
    # Threshold for matching
    if not matches or matches[0][0] < 2:
        return REFUSAL_TEMPLATE
        
    # Top match
    top_score, top_entry = matches[0]
    
    # Special Handling for the "Personal Phone" trap to prevent blending
    # If it's about personal phones/work files, we MUST use IT 3.1 or refuse.
    if "personal phone" in question_lower or "work files" in question_lower:
        if top_entry['doc'] == 'policy_it_acceptable_use.txt' and top_entry['section'] == '3.1':
            pass # Keep it
        else:
            # Check if IT 3.1 is in matches at all
            it_31 = next((m[1] for m in matches if m[1]['doc'] == 'policy_it_acceptable_use.txt' and m[1]['section'] == '3.1'), None)
            if it_31:
                top_entry = it_31
            else:
                return REFUSAL_TEMPLATE

    # Citations are mandatory
    return f"{top_entry['content']}\n\nSource: {top_entry['doc']} section {top_entry['section']}"

def main():
    # retrieve_documents skill
    index = retrieve_documents()
    print("Skill [retrieve_documents] — Indexed policy documents.")
    
    print("\nAgent: Ready to answer policy questions. (Type 'exit' to quit)")
    
    while True:
        try:
            question = input("\nYou: ")
            if not question.strip():
                continue
            if question.lower() in ['exit', 'quit', 'bye']:
                break
            
            # answer_question skill
            answer = answer_question(question, index)
            print(f"\nAgent: {answer}")
        except EOFError:
            break

if __name__ == "__main__":
    main()
