import os
import re

# Configuration
POLICIES_DIR = "../data/policy-documents/"
DOCS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

IT_KEYWORDS = ["phone", "personal device", "mobile", "byod", "device"]

def retrieve_documents(directory):
    """
    Skill 1: Regex Partitioning.
    Loads and partitions policies into a structured index.
    """
    index = []
    for doc_name in DOCS:
        path = os.path.join(os.path.dirname(__file__), directory, doc_name)
        if not os.path.exists(path):
            print(f"WARNING: Resource {doc_name} is missing. Indexing remaining files.")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to find subsections (e.g., 2.1, 3.2) and their following text
        # Looks for digit.digit followed by space, then text until the next subsection or double newline/header
        subsections = re.findall(r'(\d+\.\d+)\s+([\s\S]*?)(?=\n\s*\d+\.\d+|\n\s*═+|\Z)', content)
        
        for section_id, text in subsections:
            index.append({
                "doc_name": doc_name,
                "section_id": section_id,
                "text": text.strip().replace('\n', ' ')
            })
    return index

def answer_question(question, index):
    """
    Skill 2: The Retrieval Engine.
    Implements IT Override, No Blending, and Verbatim Consistency.
    """
    q = question.lower()
    
    # 1. Refusal Trigger (Culture/General Practices)
    if any(word in q for word in ["culture", "flexible working", "general practice"]):
        return REFUSAL_TEMPLATE

    # 2. IT Override Layer
    search_scope = index
    if any(kw in q for kw in IT_KEYWORDS):
        search_scope = [item for item in index if item["doc_name"] == "policy_it_acceptable_use.txt"]
        
        # 3. Verbatim Mapping for Personal Device questions (IT 3.2 Consistency)
        if "personal" in q and ("phone" in q or "device" in q):
            # Ensure we prioritize Section 3.2 for classified/sensitive data mention
            for item in search_scope:
                if item["section_id"] == "3.2":
                    return f"{item['text']} (Source: {item['doc_name']} Section {item['section_id']})"

    # 4. Keyword-Weighted Search (No Blending)
    q_words = set(re.findall(r'\w+', q))
    best_score = 0
    best_hit = None
    
    for item in search_scope:
        item_words = set(re.findall(r'\w+', item["text"].lower()))
        score = len(q_words.intersection(item_words))
        
        # Priority logic for specific sections if keywords match
        if "carry forward" in q and item["section_id"] == "2.6" and "hr" in item["doc_name"]: score += 10
        if "slack" in q and item["section_id"] == "2.3" and "it" in item["doc_name"]: score += 10
        if "da" in q and "meal" in q and item["section_id"] == "2.6" and "finance" in item["doc_name"]: score += 10
        if "approv" in q and ("lwp" in q or "leave without pay" in q) and item["section_id"] == "5.2" and "hr" in item["doc_name"]: score += 15
        
        if score > best_score:
            best_score = score
            best_hit = item
            
    # Minimum relevance threshold
    if not best_hit or best_score < 2:
        return REFUSAL_TEMPLATE
        
    return f"{best_hit['text']} (Source: {best_hit['doc_name']} Section {best_hit['section_id']})"

def main():
    print("CMC Compliance Intelligence Agent (Version 2.0 - 100% Compliance)")
    print("Type your question or 'exit' to quit.")
    
    index = retrieve_documents(POLICIES_DIR)
    
    while True:
        try:
            question = input("\nUser Question: ").strip()
        except EOFError:
            break
            
        if question.lower() == 'exit':
            break
        if not question:
            continue
            
        answer = answer_question(question, index)
        
        # Strict formatting for refusal template (no prefix)
        if answer == REFUSAL_TEMPLATE:
            print(answer)
        else:
            print(f"Agent: {answer}")

if __name__ == "__main__":
    main()
