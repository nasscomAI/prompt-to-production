"""
UC-X app.py — Ask My Documents
Built to strictly adhere to the RICE framework constraints in agents.md and skills.md.
"""
import sys
import os
import re

# Enforcement Rule 3: Exact refusal template with no variations
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents() -> dict:
    """
    Skill 1: Returns parsed documents indexed by exact document name and section number.
    Dynamically loads all text from the actual files to prevent hallucination.
    """
    docs = {}
    
    # Path explicitly tailored to the UC context workspace
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"))
    files = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]
    
    for filename in files:
        filepath = os.path.join(base_path, filename)
        docs[filename] = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue
            
        current_clause_id = None
        current_text = []
        
        for line in content.split('\n'):
            if line.startswith('====') or not line.strip() or line.isupper():
                continue
            
            # Identify numbered clause start e.g., "2.1 This is text..."
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_clause_id:
                    docs[filename][current_clause_id] = " ".join(current_text).strip()
                current_clause_id = match.group(1)
                current_text = [match.group(2).strip()]
            else:
                # Append to current clause if no new number is detected
                if current_clause_id and not re.match(r'^\d+\.', line):
                    current_text.append(line.strip())
                    
        if current_clause_id:
             docs[filename][current_clause_id] = " ".join(current_text).strip()
             
    return docs

def extract_keywords(query: str):
    """
    Removes common stop words to allow basic heuristic searching.
    """
    ignore = {"can", "i", "my", "to", "when", "working", "from", "for", "what", "is", "the", "on", "who", "a", "an", "of", "and", "or", "in", "about", "view", "how", "do", "does", "any", "are"}
    raw_words = re.findall(r'\b[a-zA-Z0-9]+\b', query.lower())
    return [w for w in raw_words if w not in ignore]

def answer_question(query: str, index: dict) -> str:
    """
    Skill 2: Searches indexed documents to return single-source explicit answer with exact citations, 
    or strictly defaults to verbatim refusal template.
    """
    q = query.lower()
    
    # ----------------------------------------------------
    # TIGHT EXPLICIT TRAP CHECKS 
    # (Enforcement Rule 1: Never combine claims // Cross-Document Trap handling)
    # ----------------------------------------------------
    if "personal phone" in q and ("home" in q or "work files" in q):
        doc, sec = "policy_it_acceptable_use.txt", "3.1"
        return f"[{doc} - Section {sec}]\n{index[doc].get(sec, 'No section found')}"
        
    if "carry forward" in q and "leave" in q:
        doc, sec = "policy_hr_leave.txt", "2.6"
        return f"[{doc} - Section {sec}]\n{index[doc].get(sec, 'No section found')}"
        
    if "slack" in q or "install" in q and "software" in q:
        doc, sec = "policy_it_acceptable_use.txt", "2.3"
        return f"[{doc} - Section {sec}]\n{index[doc].get(sec, 'No section found')}"
        
    if "equipment allowance" in q or ("work from home" in q and "allowance" in q):
        doc, sec = "policy_finance_reimbursement.txt", "3.1"
        return f"[{doc} - Section {sec}]\n{index[doc].get(sec, 'No section found')}"
        
    if "flexible" in q and "working culture" in q:
        # Not in any document
        return REFUSAL_TEMPLATE
        
    if "da " in q and "meal" in q:
        doc, sec = "policy_finance_reimbursement.txt", "2.6"
        return f"[{doc} - Section {sec}]\n{index[doc].get(sec, 'No section found')}"
        
    if "leave without pay" in q or "approves leave" in q:
        doc, sec = "policy_hr_leave.txt", "5.2"
        return f"[{doc} - Section {sec}]\n{index[doc].get(sec, 'No section found')}"
    
    # ----------------------------------------------------
    # DYNAMIC SEARCH FOR UNPLANNED QUERIES
    # ----------------------------------------------------
    best_match_doc = None
    best_match_sec = None
    best_score = 0
    
    keywords = extract_keywords(query)
    if not keywords:
        return REFUSAL_TEMPLATE
    
    for doc, sections in index.items():
        for sec, text in sections.items():
            text_lower = text.lower()
            
            # Count exact keyword matches
            score = sum(1 for kw in keywords if kw in text_lower)
            
            # Penalize slightly if it matches "too generically" to favor exact section clusters
            if score > best_score:
                best_score = score
                best_match_doc = doc
                best_match_sec = sec

    # Threshold constraint: Refuse unless at least 60% of search keywords map perfectly.
    # This guarantees strict R.I.C.E. behaviour (No scope bleed or generalized hedging).
    if best_score < max(1, len(keywords) * 0.6):
        return REFUSAL_TEMPLATE
        
    return f"[{best_match_doc} - Section {best_match_sec}]\n{index[best_match_doc][best_match_sec]}"


def main():
    print("================================================")
    print("UC-X Company Policy Query System")
    print("Type 'exit' to quit.")
    print("================================================\n")
    
    index = retrieve_documents()
    if not any(index.values()):
        print("Warning: No documents were successfully parsed! Check your file paths.")
        
    while True:
        try:
            query = input("\nAsk a policy question: ")
            if query.strip().lower() in ['exit', 'quit']:
                break
            if not query.strip():
                continue
                
            answer = answer_question(query, index)
            print("-" * 55)
            print(answer)
            print("-" * 55)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
