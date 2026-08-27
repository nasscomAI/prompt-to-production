"""
UC-X app.py — Policy Document Assistant.
Implements retrieve_documents and answer_question skills based on agents.md and skills.md.
"""
import os
import re
from typing import Dict, List, Tuple

# Configuration
DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(file_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Loads and indexes policy files by document name and section number.
    """
    indexed_docs = {}
    
    for path in file_paths:
        if not os.path.exists(path):
            print(f"Error: File not found at {path}")
            continue
            
        doc_name = os.path.basename(path)
        indexed_docs[doc_name] = {}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Clean up box-drawing lines
        content = re.sub(r'═+', '', content)
        
        # Split by section headers: line starting with "N. "
        sections = re.split(r'\n(?=\d+\.\s+[A-Z\(\)\s/—]+(?:\n|$))', content)
        
        for section in sections:
            # Find section number and header
            header_match = re.search(r'^(\d+)\.\s+(.*)\n', section.strip())
            if header_match:
                section_num = header_match.group(1)
                section_clean = section.strip()
                indexed_docs[doc_name][section_num] = section_clean
                
                # Split by sub-sections (e.g., "1.1")
                # Look for "X.Y " at the start of a line
                subsections = re.split(r'\n(?=\d+\.\d+)', section_clean)
                for sub in subsections:
                    sub_match = re.match(r'(\d+\.\d+)', sub.strip())
                    if sub_match:
                        sub_num = sub_match.group(1)
                        indexed_docs[doc_name][sub_num] = sub.strip()
                        
    return indexed_docs

def answer_question(question: str, indexed_docs: Dict[str, Dict[str, str]]) -> str:
    """
    Searches indexed documents and returns a single-source answer with citation 
    OR the refusal template.
    """
    # Normalized question
    question_lower = question.lower()
    
    # Common abbreviations and synonyms in the policy docs
    synonyms = {
        "lwp": ["leave without pay", "leave without pay"],
        "leave without pay": ["lwp"],
        "da": ["daily allowance"],
        "daily allowance": ["da"],
        "byod": ["personal devices", "personal phone"],
        "personal phone": ["byod", "personal devices"],
        "wfh": ["work from home", "working from home"],
        "work from home": ["wfh"],
    }
    
    # Expand query with synonyms
    expanded_query = question_lower
    for term, syns in synonyms.items():
        if term in question_lower:
            for syn in syns:
                if syn not in expanded_query:
                    expanded_query += " " + syn

    query_words = set(re.findall(r'\w+', expanded_query))
    
    # Simple stemmer: remove common suffixes
    def stem(word):
        if len(word) <= 3: return word
        for suffix in ['s', 'es', 'ed', 'ing', 'al', 'ment', 'tion']:
            if word.endswith(suffix):
                return word[:-len(suffix)]
        return word

    stemmed_query = {stem(w) for w in query_words}
    
    # Exclude common stop words
    stop_words = {'the', 'a', 'is', 'can', 'i', 'for', 'on', 'my', 'what', 'who', 'how', 'of', 'to', 'in', 'and', 'with', 'any', 'from', 'all', 'be', 'an', 'are'}
    stemmed_query = {w for w in stemmed_query if w not in stop_words and len(w) > 1}
    
    if not stemmed_query:
        return REFUSAL_TEMPLATE

    # Simple word frequency across all documents for IDF-like weighting
    word_counts = {}
    total_sections = 0
    for sections in indexed_docs.values():
        for content in sections.values():
            total_sections += 1
            seen_in_section = set(re.findall(r'\w+', content.lower()))
            for w in seen_in_section:
                sw = stem(w)
                word_counts[sw] = word_counts.get(sw, 0) + 1

    scores = []
    
    for doc_name, sections in indexed_docs.items():
        for section_id, content in sections.items():
            # Skip parent sections if sub-sections are available for better precision
            if '.' not in section_id and any(f"{section_id}." in sid for sid in sections.keys()):
                continue
                
            content_lower = content.lower()
            content_words = set(re.findall(r'\w+', content_lower))
            
            # Expand content with synonyms
            expanded_content_words = set(content_words)
            for term, syns in synonyms.items():
                if term in content_words:
                    for syn in syns:
                        expanded_content_words.update(re.findall(r'\w+', syn))
            
            stemmed_content = {stem(w) for w in expanded_content_words}
            
            # Intersection of query stems and content stems
            matches = stemmed_query.intersection(stemmed_content)
            
            if matches:
                # Calculate score using IDF-like weights
                # Rare words get higher weight
                score = 0
                for match in matches:
                    idf = 1.0 / (word_counts.get(match, 1) + 1)
                    score += idf
                
                # Normalize by content length (very slight penalty for long sections)
                score = score / (len(content_lower) ** 0.05)
                
                # Big bonus for matching more words from the original query
                coverage = len(matches) / len(stemmed_query)
                score *= (1 + coverage)
                
                scores.append({
                    'doc': doc_name,
                    'section': section_id,
                    'content': content,
                    'score': score,
                    'matches': len(matches)
                })

    if not scores:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    top_match = scores[0]
    
    # Enforcement: Threshold for "What is the company view on flexible working culture?"
    # If the coverage is too low, it's likely a weak match.
    # For a query with 3+ keywords, we expect at least 2 to match or a high score.
    if len(stemmed_query) >= 3 and top_match['matches'] < 2:
        return REFUSAL_TEMPLATE
    
    if top_match['matches'] < 1:
        return REFUSAL_TEMPLATE

    # Citations and Answer Formatting
    answer = f"According to {top_match['doc']} section {top_match['section']}:\n\n{top_match['content']}"
    
    return answer

def main():
    print("UC-X Policy Assistant initialized.")
    print("Type your question or 'exit' to quit.")
    
    indexed_data = retrieve_documents(DOC_PATHS)
    
    while True:
        try:
            user_input = input("\nQuestion: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if not user_input:
                continue
                
            result = answer_question(user_input, indexed_data)
            print("-" * 40)
            print(result)
            print("-" * 40)
            
        except EOFError:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
