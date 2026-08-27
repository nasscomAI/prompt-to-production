import os
import re
import sys

# Refusal template from README.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DATA_PATH = "../data/policy-documents"
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

def retrieve_documents():
    """
    Skill: retrieve_documents
    Loads the three corporate policy files and indexes them by document name and section number.
    """
    indexed_data = []
    for filename in POLICY_FILES:
        filepath = os.path.join(DATA_PATH, filename)
        if not os.path.exists(filepath):
            print(f"Error: Required file {filename} is missing.")
            sys.exit(1)
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Find sub-sections (e.g. 1.1, 2.3, 10.1)
            # Use regex to find sections properly
            sections = re.split(r'\n(?=\d+\.\d+)', content)
            
            for section in sections:
                lines = section.strip().split('\n')
                if not lines: continue
                
                # First line should be the section number + start of text
                match = re.match(r'^(\d+\.\d+)\s*(.*)', lines[0], re.DOTALL)
                if match:
                    sec_num = match.group(1)
                    first_line_text = match.group(2)
                    remaining_text = " ".join(lines[1:])
                    full_content = f"{first_line_text} {remaining_text}".strip()
                    
                    indexed_data.append({
                        'doc': filename,
                        'section': sec_num,
                        'text': full_content,
                        'full_text': f"{sec_num} {full_content}"
                    })
    return indexed_data

def answer_question(question, indexed_data):
    """
    Skill: answer_question
    Searches indexed documents to provide a single-source answer with citations or the refusal template.
    """
    question_lower = question.lower()
    
    # Simple keyword-based matching
    # Remove common stop words and split into tokens
    stop_words = {'can', 'i', 'the', 'is', 'at', 'on', 'in', 'to', 'for', 'with', 'a', 'an', 'what', 'who', 'how', 'where', 'why', 'do', 'does', 'my'}
    tokens = [t for t in re.findall(r'\w+', question_lower) if t not in stop_words]
    
    if not tokens:
        return REFUSAL_TEMPLATE

    # Score each section based on token matches
    scored_results = []
    for item in indexed_data:
        score = 0
        text_lower = item['full_text'].lower()
        for token in tokens:
            # Simple stemming: search for the word OR the word minus 's'
            stem = token[:-1] if token.endswith('s') and len(token) > 3 else token
            if token in text_lower or (stem and stem in text_lower):
                score += 1
                # Bonus for exact word match
                if re.search(rf'\b{token}\b', text_lower):
                    score += 0.5
        
        if score > 0:
            scored_results.append((score, item))
            
    if not scored_results:
        return REFUSAL_TEMPLATE
        
    # Sort by score descending
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    # Rule 1 & 5 Enforcement
    top_score, top_item = scored_results[0]
    
    # If it's a "personal" + "phone/device" question, strictly prefer IT policy section 3
    if any(k in question_lower for k in ["personal"]) and any(k in question_lower for k in ["phone", "device"]):
        it_3_results = [r for r in scored_results if r[1]['doc'] == "policy_it_acceptable_use.txt" and r[1]['section'].startswith('3.')]
        if it_3_results:
            top_score, top_item = it_3_results[0]

    # Rule 3: Refusal if score is too low
    # "Flexible working culture" should fail because "working" might match common phrases but "flexible" is missing.
    if top_score < 2.0:
        return REFUSAL_TEMPLATE


    # Rule 4 & 2
    citation = f"--- Citation: {top_item['doc']} Section {top_item['section']} ---"
    answer = f"{top_item['text']}\n\n{citation}"
    
    return answer

def main():
    print("--- UC-X Policy Assistant ---")
    print("Loading documents...")
    indexed_data = retrieve_documents()
    print("System ready. Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            query = input("User Question: ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                print("Goodbye.")
                break
                
            response = answer_question(query, indexed_data)
            print(f"\nAssistant: {response}\n")
            print("-" * 40)
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

if __name__ == "__main__":
    main()


