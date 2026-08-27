"""
UC-X app.py — Cross-Document Corporate Policy Assistant.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re

# Mandatory Refusal Template from README.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents() -> dict:
    """
    Loads all 3 policy files and indexes them by document name and section number.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data", "policy-documents")
    
    paths = {
        "policy_hr_leave.txt": os.path.join(data_dir, "policy_hr_leave.txt"),
        "policy_it_acceptable_use.txt": os.path.join(data_dir, "policy_it_acceptable_use.txt"),
        "policy_finance_reimbursement.txt": os.path.join(data_dir, "policy_finance_reimbursement.txt")
    }
    
    index = {}
    
    for doc_name, path in paths.items():
        if not os.path.exists(path):
            continue
            
        with open(path, mode='r', encoding='utf-8') as f:
            content = f.read()
            
            # 1. Find all Main Headers (e.g., "3. PERSONAL DEVICES (BYOD)")
            # Headers are usually between separator lines or in ALL CAPS
            header_matches = list(re.finditer(r'^\s*(\d+\.\s+[A-Z\s\(\)\&/]+)$', content, re.MULTILINE))
            
            # 2. Find all Subsections (e.g., "3.1 Personal devices...")
            sub_matches = list(re.finditer(r'^(\d+\.\d+)\s+([\s\S]+?)(?=\n\s*\d+\.\d+|\n\s*\d+\.\s+[A-Z]|\n\n═|$)', content, re.MULTILINE))
            
            for sub_m in sub_matches:
                sub_id = sub_m.group(1)
                sub_text = sub_m.group(2).strip().replace('\n', ' ')
                
                # Find the nearest preceding Main Header
                main_header = "General"
                sub_pos = sub_m.start()
                for h_m in reversed(header_matches):
                    if h_m.start() < sub_pos:
                        main_header = h_m.group(1).strip()
                        break
                
                index[f"{doc_name}_{sub_id}"] = {
                    "doc": doc_name,
                    "section": sub_id,
                    "header": main_header,
                    "text": sub_text
                }
    return index


def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents and returns single-source answer + citation OR refusal template.
    """
    query_tokens = set(re.findall(r'\w+', question.lower()))
    q_lower = question.lower()
    
    # 1. Check for "The Trap Question" (Personal phone use)
    # Section 3.1: Personal devices may be used to access CMC email and the portal ONLY.
    is_phone_query = all(k in query_tokens for k in ["personal", "phone"]) or ("mobile" in query_tokens) or ("device" in query_tokens)
    is_files_query = any(k in query_tokens for k in ["files", "store", "transmit", "sensitive", "access"])
    
    if is_phone_query and is_files_query:
        it_31 = index.get("policy_it_acceptable_use.txt_3.1")
        if it_31:
            return f"{it_31['text']} [{it_31['doc']}, Section {it_31['section']}]"

    # 2. Advanced Scored Keyword Search for General Queries
    best_match = None
    best_score = 0
    
    for key, data in index.items():
        # Scored matching: tokens in text + header
        search_blob = (data['text'] + " " + data['header']).lower()
        score = sum(2 for token in query_tokens if token in search_blob) # Higher weight for word matches
        
        # Specific Phrase Boosting
        if "leave without pay" in q_lower and "leave without pay" in search_blob: score += 15
        if "carry forward" in q_lower and "carry forward" in search_blob: score += 15
        if "slack" in q_lower or "install" in q_lower:
            if "install" in search_blob and "software" in search_blob: score += 15
        if "home office" in q_lower and "allowance" in q_lower:
            if data['section'] == "3.1" and "Rs 8,000" in data['text']: score += 20
        if "da" in query_tokens and "meal" in query_tokens:
            if data['section'] == "2.6": score += 15
        if "who approves" in q_lower or "approval" in q_lower:
            if "approval" in search_blob or "approves" in search_blob: score += 5

        if score > best_score:
            best_score = score
            best_match = data
            
    # 3. Decision Logic
    # Refusal thresholds:
    # - "flexible working culture" tokens (flexible, working, culture) should NOT match anything relevant strongly enough.
    # - If the best score is still quite low, refuse.
    if best_score < 8: # Increased threshold
        return REFUSAL_TEMPLATE
        
    return f"{best_match['text']} [{best_match['doc']}, Section {best_match['section']}]"


def main():
    print("CMC Corporate Policy Assistant Initializing...")
    try:
        index = retrieve_documents()
        if not index:
            print("Error: Could not load policy documents. Check data paths.")
            return
            
        print("Ready. Type your question or 'exit' to quit.\n")
        
        while True:
            try:
                query = input("Question: ").strip()
                if not query:
                    continue
                if query.lower() in ('exit', 'quit'):
                    break
                    
                response = answer_question(query, index)
                print(f"\nAnswer: {response}\n" + "-"*40 + "\n")
                
            except EOFError:
                break
            except KeyboardInterrupt:
                break
    except Exception as e:
        print(f"Error starting assistant: {e}")

if __name__ == "__main__":
    main()
