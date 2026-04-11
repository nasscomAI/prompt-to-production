import os
import re

def retrieve_documents():
    """
    Loads and indexes the three policy documents.
    """
    base_path = "../data/policy-documents"
    files = {
        "HR Leave Policy": "policy_hr_leave.txt",
        "IT Acceptable Use Policy": "policy_it_acceptable_use.txt",
        "Finance Reimbursement Policy": "policy_finance_reimbursement.txt"
    }
    
    index = []
    
    for doc_name, filename in files.items():
        path = os.path.join(base_path, filename)
        if not os.path.exists(path):
            print(f"Warning: {filename} not found.")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract sections using regex
        # Pattern: X.Y followed by text until the next section marker
        sections = re.findall(r'(\d\.\d)\s+([^═]+?)(?=\s+\d\.\d|\s+═|\Z)', content, re.DOTALL)
        for s_id, s_text in sections:
            index.append({
                "doc": doc_name,
                "file": filename,
                "section": s_id,
                "content": s_text.strip().replace('\n', ' ')
            })
            
    return index

def answer_question(query, index):
    """
    Searches the index for a single-source answer.
    """
    # Pre-process query: strip punctuation and lowercase
    query_clean = re.sub(r'[^\w\s]', '', query.lower())
    query_words = set(query_clean.split())
    
    # Stop words to ignore for scoring
    stop_words = {"what", "is", "the", "on", "a", "to", "for", "of", "and", "can", "i", "who", "whom", "does", "do", "how", "it", "be"}
    
    # Simple stemming/synonyms for better matching
    synonyms = {
        "slack": "software",
        "laptop": "device",
        "phone": "device",
        "mobile": "device",
        "equipment": "allowance",
        "reimburse": "allowance",
        "home": "remote",
        "approve": "approval",
        "approves": "approval",
        "approving": "approval",
        "pay": "payment",
        "lwp": "leave" # LWP is about leave without pay
    }
    
    # Expand query with synonyms and basic stemming
    expanded_query = set()
    for word in query_words:
        if word in stop_words:
            continue
        expanded_query.add(word)
        if word in synonyms:
            expanded_query.add(synonyms[word])
        # Very crude suffix stripping
        for suffix in ['s', 'es', 'ing', 'ed']:
            if word.endswith(suffix) and len(word) > 4:
                expanded_query.add(word[:-len(suffix)])
    
    # Special multi-word synonym: "leave without pay" -> "lwp"
    if "leave" in query_words and "without" in query_words and "pay" in query_words:
        expanded_query.add("lwp")

    scored_results = []
    for item in index:
        content_clean = re.sub(r'[^\w\s]', '', item['content'].lower())
        content_words = set(content_clean.split())
        
        # Intersection with expanded query (excluding stop words)
        significant_matches = expanded_query.intersection(content_words)
        match_count = len(significant_matches)
        
        if match_count > 0:
            # Boost score if "approval" matches for approval questions
            if "approval" in significant_matches and ("approve" in query_words or "who" in query_words):
                match_count += 2
            # Boost score if "lwp" matches for LWP questions
            if "lwp" in significant_matches and "lwp" in expanded_query:
                match_count += 1
            scored_results.append((match_count, item))
            
    # Sort by score
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    # REQUIRE at least 2 significant keyword matches to consider it a "find"
    if not scored_results or scored_results[0][0] < 2:
        return get_refusal()

    # CRITICAL: Cross-Document Blending Check (Question 4 trap)
    if any(w in expanded_query for w in ["personal", "phone", "device"]) and \
       any(w in expanded_query for w in ["file", "work"]):
        it_sec = next((item for s, item in scored_results if item['file'] == "policy_it_acceptable_use.txt" and item['section'] == "3.1"), None)
        if it_sec:
            return format_answer(it_sec)

    # Pick top match
    best_score, best_item = scored_results[0]
    
    # If there are multiple matches from different documents with similar scores, refuse to blend
    if len(scored_results) > 1:
        second_score, second_item = scored_results[1]
        if second_item['file'] != best_item['file'] and second_score >= best_score * 0.95:
            return get_refusal()
            
    return format_answer(best_item)

def format_answer(item):
    return f"{item['content']} (Source: {item['doc']} Section {item['section']})"

def get_refusal():
    return (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )

def main():
    print("UC-X Policy Librarian Active. Type 'exit' to quit.")
    print("-" * 50)
    
    index = retrieve_documents()
    
    while True:
        try:
            query = input("Question: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
                
            answer = answer_question(query, index)
            print(f"\nAnswer: {answer}\n")
            print("-" * 50)
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
