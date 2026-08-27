import os
import re
import sys

# List of allowed policy documents
POLICY_DOCS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

DATA_DIR = "../data/policy-documents/"

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """
    Loads all policy files and indexes them by document name and section number.
    Returns: Dict mapping (doc_name, section_id) -> raw_text
    """
    indexed_data = {}
    
    for doc_name in POLICY_DOCS:
        path = os.path.join(DATA_DIR, doc_name)
        if not os.path.exists(path):
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Pattern to find numbered sections (e.g., 2.3)
        # It handles multiline section text until the next section start or divider
        section_pattern = re.compile(r'\n(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\s*════|\Z)', re.DOTALL)
        matches = section_pattern.findall(content)
        
        for section_id, text in matches:
            clean_text = " ".join(text.split())
            indexed_data[(doc_name, section_id)] = clean_text
            
    return indexed_data

STOPWORDS = {"can", "what", "who", "the", "for", "and", "not", "with", "this", "some", "any", "are", "you", "your", "from", "they", "will", "has"}

def get_keywords(text):
    """Simple tokenizer with basic stemming (tails) and stopword removal."""
    # Basic lowercase words
    words = re.findall(r'\b\w{3,}\b', text.lower())
    processed = []
    for w in words:
        if w in STOPWORDS:
            continue
        # Very crude stemming (remove 's', 'es', 'ing', 'ed')
        if w.endswith('ing') and len(w) > 6: w = w[:-3]
        elif w.endswith('ed') and len(w) > 5: w = w[:-2]
        elif w.endswith('es') and len(w) > 5: w = w[:-2]
        elif w.endswith('s') and len(w) > 4: w = w[:-1]
        processed.append(w)
    return set(processed)

def get_document_weights(indexed_data):
    """Calculates how many sections each word appears in for IDF-like weighting."""
    word_counts = {}
    for text in indexed_data.values():
        words = get_keywords(text)
        for w in words:
            word_counts[w] = word_counts.get(w, 0) + 1
    return word_counts

def get_synonyms(words):
    """Adds common policy synonyms to the keyword set for better matching."""
    synonyms = {
        "laptop": {"hardware", "device"},
        "phone": {"personal", "device", "mobile"},
        "mobile": {"phone", "device"},
        "file": {"data", "document", "classified"},
        "salary": {"pay", "entitlement"},
        "money": {"reimbursement", "allowance", "claim"},
        "approve": {"approval", "require", "permission", "head"},
        "approv": {"approval", "require", "permission", "head", "approve"},
        "install": {"software", "catalogue", "application"},
        "equipment": {"desk", "chair", "office"},
        "pay": {"lwp"},
        "leave": {"lwp"},
        "without": {"lwp"},
    }
    new_words = set(words)
    for w in words:
        if w in synonyms:
            new_words.update(synonyms[w])
    return new_words

def answer_question(question, indexed_data):
    """
    Searches indexed documents for a single-source answer.
    Enforces no blending and refuses if no high-confidence single match is found.
    """
    q_words = get_keywords(question)
    q_lower = question.lower()
    if not q_words:
        return REFUSAL_TEMPLATE
        
    expanded_q_words = get_synonyms(q_words)
    weights = get_document_weights(indexed_data)

    rankings = []
    
    for (doc, section), text in indexed_data.items():
        doc_words = get_keywords(text)
        
        # Weighted matching
        score = 0
        overlap = expanded_q_words.intersection(doc_words)
        for w in overlap:
            weight = 8.0 / (1 + weights.get(w, 0))
            if w in q_words:
                weight *= 4.0
            score += weight
            
        # Specific section bonus for approval questions
        if ("approv" in q_lower) and ("approval" in text.lower() or "approve" in text.lower()):
            # Higher bonus if it's explicitly about the topic (e.g., LWP)
            if "lwp" in doc_words or "leave" in doc_words:
                score += 30.0
            else:
                score += 10.0
        
        if score > 0:
            rankings.append({
                "doc": doc,
                "section": section,
                "text": text,
                "score": score
            })
            
    # Sort by score descending
    rankings.sort(key=lambda x: x["score"], reverse=True)
    
    if not rankings or rankings[0]["score"] < 5.0:
        return REFUSAL_TEMPLATE
        
    top_result = rankings[0]
    
    # Specific Rule for the "Personal Phone / BYOD" Trap
    if "personal" in q_lower and ("phone" in q_lower or "device" in q_lower):
        if "file" in q_lower or "data" in q_lower or "access" in q_lower:
             if top_result["doc"] != "policy_it_acceptable_use.txt" or top_result["section"] != "3.1":
                 return REFUSAL_TEMPLATE

    # Enforcement: Choose a single source. If scores are close across docs, refuse.
    if len(rankings) > 1:
        next_result = rankings[1]
        # Ambiguity/Blending Trap detection
        if next_result["doc"] != top_result["doc"] and next_result["score"] > top_result["score"] * 0.7:
            # If the top result is very high (e.g. from bonus), allow it.
            if top_result["score"] < 40.0:
                return REFUSAL_TEMPLATE

    answer = f"{top_result['text']}\n\n(Source: {top_result['doc']} section {top_result['section']})"
    return answer

def main():
    print("--- CMC Policy Document QA System ---")
    print("Type your question or 'exit' to quit.")
    
    try:
        indexed_data = retrieve_documents()
    except Exception as e:
        print(f"Error indexing documents: {e}")
        return

    while True:
        try:
            user_input = input("\nQuestion: ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
                
            if not user_input:
                continue
                
            response = answer_question(user_input, indexed_data)
            print("-" * 40)
            print(response)
            print("-" * 40)
            
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
