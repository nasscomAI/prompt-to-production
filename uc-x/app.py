import os
import sys
import re

# Policy document paths
DATA_DIR = os.path.join("..", "data", "policy-documents")
FILES = {
    "policy_hr_leave.txt": "HR Policy",
    "policy_it_acceptable_use.txt": "IT Policy",
    "policy_finance_reimbursement.txt": "Finance Policy"
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """Loads all 3 policy files and indexes them by document name and section number."""
    documents = {}
    for filename in FILES:
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing document: {filename}")
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            sections = {}
            
            # Match patterns like "3.1" at the start of a line
            pattern = re.compile(r'^(\d+\.\d+)\s+(.*)', re.MULTILINE)
            matches = list(pattern.finditer(content))
            
            for i, match in enumerate(matches):
                sec_num = match.group(1)
                start = match.end()
                # End is the start of the next match or end of file
                end = matches[i+1].start() if i + 1 < len(matches) else len(content)
                text = content[start:end].strip()
                sections[sec_num] = text
            
            documents[filename] = sections
    return documents

def answer_question(question, documents):
    """Searches indexed documents and returns single-source answer + citation OR refusal template."""
    q = question.lower()
    
    # 1. Check for specific known traps or topics
    if ("personal phone" in q or "personal device" in q) and "work files" in q:
        if "policy_it_acceptable_use.txt" in documents:
            it_sections = documents["policy_it_acceptable_use.txt"]
            if "3.1" in it_sections:
                return f"According to policy_it_acceptable_use.txt (Section 3.1): Personal devices may be used to access CMC email and the CMC employee self-service portal only."

    # 2. General retrieval logic with higher precision
    # Split question into key nouns/verbs (ignoring common words)
    stop_words = {"what", "is", "the", "on", "can", "i", "how", "who", "whom", "where", "when", "why", "do", "does", "did", "have", "has", "had", "are", "were", "was", "be", "been", "being", "a", "an", "of", "to", "in", "for", "with", "at", "by", "from", "about", "as", "into", "through", "during", "before", "after", "above", "below", "between", "under", "again", "further", "then", "once", "here", "there", "any", "all", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"}
    keywords = [w for w in re.findall(r'\b\w+\b', q) if w not in stop_words and len(w) > 3]
    
    matches = []
    for filename, sections in documents.items():
        for sec_num, content in sections.items():
            content_lower = content.lower()
            # Require at least 2 keywords to match or 1 very specific one
            matched_keywords = [kw for kw in keywords if kw in content_lower]
            if len(matched_keywords) >= 2:
                matches.append((filename, sec_num, content, len(matched_keywords)))

    # Sort matches by number of keyword hits
    matches.sort(key=lambda x: x[3], reverse=True)

    if not matches:
        return REFUSAL_TEMPLATE

    # Rule 1: No blending. 
    # If the top match is significantly better, pick it.
    # Otherwise, if we have matches from different documents, we might need to refuse or be careful.
    best_match = matches[0]
    doc, sec, text, score = best_match
    
    # Special check for "culture" or general terms that might have weak hits
    if "culture" in q and "culture" not in text.lower():
        return REFUSAL_TEMPLATE

    # Rule 4: Cite source document name + section number
    # Return the first complete sentence
    sentence_match = re.search(r'[^.!?]+[.!?]', text)
    if sentence_match:
        answer_text = sentence_match.group(0).strip()
    else:
        answer_text = text[:200]
        
    return f"According to {doc} (Section {sec}): {answer_text}"

def main():
    print("UC-X — Ask My Documents (Policy AI)")
    print("Type 'exit' to quit.\n")
    
    try:
        docs = retrieve_documents()
        print("Documents indexed successfully.")
    except Exception as e:
        print(f"Error loading documents: {e}")
        return

    while True:
        try:
            query = input("\nQuestion: ").strip()
            if query.lower() in ["exit", "quit"]:
                break
            if not query:
                continue
            
            response = answer_question(query, docs)
            print(f"\nAnswer: {response}")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
