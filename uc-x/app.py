"""
UC-X Policy Assistant CLI — Implementation based on agents.md + skills.md
"""
import os
import re

# Configuration: File paths based on agents.md context
DATA_DIR = os.path.join("..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

# Verbatim Refusal Template as defined in agents.md Enforcement
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Expanded stopword list including corpus-specific noise
STOPWORDS = set([
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'can', 'could', 'do', 'does', 'did', 'have', 'has', 'had',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her',
    'and', 'or', 'but', 'if', 'then', 'else', 'when', 'where', 'why', 'how',
    'of', 'at', 'by', 'for', 'with', 'about', 'on', 'in', 'to', 'from',
    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
    'cmc', 'policy', 'city', 'municipal', 'corporation', 'department', 'section'
])

def stem(word):
    """Simple stemming for better matching coverage."""
    word = word.lower()
    for suffix in ['ing', 'ly', 'ed', 'es', 's', 'ment']:
        if len(word) > 4 and word.endswith(suffix):
            return word[:-len(suffix)]
    return word

def retrieve_documents():
    """Skill: loads all 3 policy files, indexes by document name and section number."""
    indexed_docs = {}
    
    for filename in POLICY_FILES:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        sections = []
        # Matches section markers like "1. ", "5.1 ", or "2.6.4 " at the start of a line
        pattern = r'(?m)^\s*(\d+(?:\.\d+)*)\.?\s+'
        matches = list(re.finditer(pattern, content))
        
        for i, m in enumerate(matches):
            sec_id = m.group(1)
            start = m.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(content)
            
            # Clean text: flatten whitespace and remove decorative bars
            raw_text = content[start:end]
            clean_text = re.sub(r'[═\s\n\t]+', ' ', raw_text).strip()
            
            if clean_text:
                sections.append({
                    'id': sec_id,
                    'content': clean_text,
                    'source': filename
                })
        indexed_docs[filename] = sections
    return indexed_docs

def answer_question(question, indexed_docs):
    """Skill: searches document index for single-source answer + citation or refusal template."""
    q_words = re.findall(r'\w+', question.lower())
    q_stems = {stem(w) for w in q_words if w not in STOPWORDS}
    
    if not q_stems:
        q_stems = {stem(w) for w in q_words}
    
    matches = []
    
    for doc_name, sections in indexed_docs.items():
        doc_label = doc_name.replace('_', ' ').replace('.txt', '').lower()
        doc_label_stems = {stem(w) for w in re.findall(r'\w+', doc_label)}
        
        for sec in sections:
            s_text = f"{sec['id']} {sec['content']}".lower()
            s_stems = {stem(w) for w in re.findall(r'\w+', s_text)}
            
            overlap = q_stems.intersection(s_stems)
            score = len(overlap) * 10
            
            # Context bonus: if the question refers to the specific department or file
            if doc_label_stems.intersection(q_stems):
                score += 5
                
            if score > 0:
                matches.append({
                    'score': score,
                    'content': sec['content'],
                    'source': sec['source'],
                    'id': sec['id']
                })
                
    if not matches:
        return REFUSAL_TEMPLATE
        
    # Sort and pick the best single-source candidate
    matches.sort(key=lambda x: x['score'], reverse=True)
    best = matches[0]
    
    # Blending Risk Check: Refuse if another source is also highly relevant (to avoid hallu/blending)
    if len(matches) > 1:
        for other in matches[1:3]:
            if other['source'] != best['source'] and other['score'] >= best['score'] * 0.7:
                return REFUSAL_TEMPLATE
                
    # Threshold for refusal: at least one unique significant match required
    if best['score'] < 10:
        return REFUSAL_TEMPLATE
        
    # Standard citation format: answer + (Source: [doc], Section [id])
    return f"{best['content']}\n\n(Source: {best['source']}, Section {best['id']})"

def main():
    print("UC-X Policy Assistant CLI")
    print("Type your question or 'exit' to quit.")
    print("-" * 30)
    
    indexed_data = retrieve_documents()
    if not indexed_data:
        print("Error: Could not load policy documents. Check your data directory.")
        return
        
    while True:
        try:
            query = input("\nQuestion: ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                break
                
            response = answer_question(query, indexed_data)
            print(f"\nAnswer: {response}")
            
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
