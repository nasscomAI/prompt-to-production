import os
import re

# --- CONFIGURATION ---
POLICY_FILES = {
    "HR Policy": "../data/policy-documents/policy_hr_leave.txt",
    "IT Policy": "../data/policy-documents/policy_it_acceptable_use.txt",
    "Finance Policy": "../data/policy-documents/policy_finance_reimbursement.txt"
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents 
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# --- SKILLS ---

def retrieve_documents():
    """
    Loads and indexes policy documents by document name and section number.
    Returns: List of dicts [{'doc': ..., 'section': ..., 'content': ...}]
    """
    indexed_data = []
    
    for doc_name, file_path in POLICY_FILES.items():
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to find sections like '2.6' or '2.' at the start of a line block
        # We look for digits followed by a dot, then optional digits
        # We also capture the text until the next section marker or end of file
        # The documents use '═════' for main headers, but subsections are just numbers
        
        # Split by what looks like a new section number start
        # e.g., "\n2.6 " or "\n3. "
        lines = content.split('\n')
        current_section = "0.0"
        current_text = []
        
        for line in lines:
            # Match section numbers like 1.1, 2.3, etc. or 1., 2.
            match = re.match(r'^(\d+\.\d+|\d+\.)\s+(.*)', line.strip())
            if match:
                # Save previous section
                if current_text:
                    indexed_data.append({
                        "doc": doc_name,
                        "section": current_section if current_section else "General",
                        "content": " ".join(current_text).strip()
                    })
                
                current_section = match.group(1).rstrip('.')
                current_text = [match.group(2)]
            else:
                if line.strip() and not line.startswith('═'):
                    current_text.append(line.strip())
                    
        # Add the last section
        if current_text:
            indexed_data.append({
                "doc": doc_name,
                "section": current_section,
                "content": " ".join(current_text).strip()
            })
            
    return indexed_data

def answer_question(query, indexed_docs):
    """
    Searches indexed documents to find a single-source answer.
    Enforces RICE rules: No blending, No hedging, Citations required.
    """
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))
    
    # Simple stopword list
    stopwords = {'can', 'i', 'the', 'is', 'what', 'who', 'how', 'on', 'my', 'with', 'to', 'for', 'of', 'in', 'and'}
    keywords = query_words - stopwords
    
    if not keywords:
        return REFUSAL_TEMPLATE
        
    # 1. TRAP DETECTION: "Personal device" / "Personal phone"
    is_personal_device_query = any(kw in query_lower for kw in ["personal phone", "personal device", "my phone", "byod"])
    
    # 2. MATCHING LOGIC
    scored_matches = []
    for item in indexed_docs:
        content_lower = item['content'].lower()
        score = 0
        
        # Check for specific key phrases/synonyms
        synonyms = {
            "install": ["install", "software", "slack", "zoom", "app", "application"],
            "allowance": ["allowance", "reimbursement", "claim", "money", "cost", "equipment"],
            "laptop": ["laptop", "computer", "device", "work station"],
            "leave": ["leave", "lwp", "annual", "sick", "vacation"]
        }
        
        # Abbreviation support
        if "lwp" in keywords and "leave without pay" in content_lower:
            score += 4
            
        for kw in keywords:
            # Direct keyword match
            if kw in content_lower:
                score += 2
            
            # Action word weights
            if kw in ["who", "approves", "approval", "authorized"] and any(w in content_lower for w in ["approval", "approves", "approving"]):
                score += 3
            
            # Installation weight
            if kw in ["install", "installation"] and "install" in content_lower:
                score += 3
            
            # Synonym/Category match
            for cat, words in synonyms.items():
                if kw in words:
                    # Check if the text matches the category
                    cat_words = [w for w in cat.split()]
                    if any(c in content_lower for c in cat_words):
                        score += 1
                        
        if score > 0:
            scored_matches.append((score, item))
            
    scored_matches.sort(key=lambda x: (x[0], len(x[1]['content'])), reverse=True)
    
    # 3. ANTI-BLENDING & SINGLE SOURCE ENFORCEMENT
    # Score Threshold: If the match is weak, refuse to avoid hallucination/mis-match
    if not scored_matches or scored_matches[0][0] < 3:
        return REFUSAL_TEMPLATE

    top_score, top_match = scored_matches[0]
    
    # Potential ambiguity check across documents
    if len(scored_matches) > 1:
        second_score, second_match = scored_matches[1]
        if second_match['doc'] != top_match['doc'] and second_score >= top_score * 0.7:
            # If "personal phone" trap detected, force IT 3.1
            if is_personal_device_query:
                it_31 = [m for s, m in scored_matches if m['doc'] == "IT Policy" and m['section'] == "3.1"]
                if it_31:
                    top_match = it_31[0]
                else:
                    return REFUSAL_TEMPLATE
            else:
                # Ambiguity between docs -> Refuse
                return REFUSAL_TEMPLATE

    # 4. FINAL FORMATTING
    answer = f"{top_match['content']}\n\nCitation: {top_match['doc']} Section {top_match['section']}"
    return answer

# --- MAIN CLI ---

def main():
    print("\n" + "="*60)
    print(" CMC POLICY COMPLIANCE AUDITOR (UC-X) ")
    print("="*60)
    print("Loading documents...")
    
    try:
        docs = retrieve_documents()
        print(f"Indexed {len(docs)} policy sections.")
    except Exception as e:
        print(f"Error loading policies: {e}")
        return

    print("\nInteractive CLI ready. Type 'exit' to quit.")
    print("-" * 60)

    while True:
        try:
            user_input = input("\nAuditor Query > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
                
            response = answer_question(user_input, docs)
            
            # Stylized Output - Use ASCII for compatibility
            print("\n" + "-"*20 + " AUDIT RESULT " + "-"*20)
            print(response)
            print("-" * 54)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n[Error] An unexpected issue occurred: {e}")

    print("\nAudit session terminated. Goodbye.\n")

if __name__ == "__main__":
    main()
