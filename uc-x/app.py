"""
UC-X Policy Retrieval App
Interactive CLI for answering policy questions.
"""
import os
import re

# Exact refusal template as required by README and agents.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Common words to ignore during search
STOPWORDS = {"is", "the", "a", "an", "for", "to", "how", "many", "what", "can", "i", "each", "do", "need", "with", "at", "who", "on", "am", "my"}

def retrieve_documents(base_dir="../data/policy-documents/"):
    """
    Loads and indexes policy files by document name and section number.
    Handles multi-line sections for better context capture.
    """
    documents = {}
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    for filename in files:
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        sections = {}
        current_num = None
        current_text = []
        
        for line in lines:
            # Check for section number at start (e.g., "1.1 ", "2.3. ")
            match = re.match(r"^(\d+\.\d+)\s+(.*)", line.strip())
            if match:
                if current_num:
                    sections[current_num] = " ".join(current_text).strip()
                current_num = match.group(1)
                current_text = [match.group(2)]
            elif current_num:
                # Append subsequent lines to the current section
                stripped_line = line.strip()
                if stripped_line:
                    current_text.append(stripped_line)
        
        # Save last section
        if current_num:
            sections[current_num] = " ".join(current_text).strip()
            
        documents[filename] = sections
        
    return documents

def answer_question(question, documents):
    """
    Searches documents using keyword overlap and scoring.
    Enforces single-source and no-hedging rules.
    """
    # Clean and tokenize the question
    question_clean = re.sub(r'[^\w\s]', '', question.lower())
    q_tokens = [w for w in question_clean.split() if w not in STOPWORDS]
    
    if not q_tokens:
        return REFUSAL_TEMPLATE

    best_score = 0
    best_answer = None
    
    # Critical keywords that should trigger high relevance
    important_keywords = ["annual", "sick", "leave", "reimbursement", "hotel", "phone", "device", "install", "maternity", "paternity", "da", "meal", "password", "grievances", "work from home", "wfh"]

    for doc_name, sections in documents.items():
        for sec_num, text in sections.items():
            text_lower = text.lower()
            score = 0
            
            # Count keyword overlap
            for token in q_tokens:
                if token in text_lower:
                    score += 1
            
            # Apply bonuses for important keywords to improve precision
            for kw in important_keywords:
                if kw in question_clean and kw in text_lower:
                    score += 2
                    
            # Check for section-specific precision (e.g. "annual" vs "sick")
            if "annual" in question_clean and "sick" in text_lower: score -= 5
            if "sick" in question_clean and "annual" in text_lower: score -= 5

            if score > best_score:
                best_score = score
                best_answer = f"According to {doc_name} section {sec_num}: {text}"
            elif score == best_score and best_score > 0:
                # If tied, we don't blend. We stick to the first strong match found.
                pass

    # Threshold for relevance. If score is too low, it's likely a hallucination or irrelevant.
    if best_score < 3:
        return REFUSAL_TEMPLATE
        
    return best_answer

def main():
    print("=== CMC Policy Retrieval Assistant ===")
    print("Loading documents...")
    documents = retrieve_documents()
    
    if not documents:
        print("Error: Could not load policy documents.")
        return

    print("System ready. Type your question or 'quit' to exit.")
    
    while True:
        try:
            query = input("\nQuestion: ").strip()
            if query.lower() in ['quit', 'exit']:
                break
            if not query:
                continue
                
            answer = answer_question(query, documents)
            print(f"\nAnswer: {answer}")
            
        except EOFError:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


