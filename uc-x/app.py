import os
import re

# Refusal Template from agents.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Paths to the policy documents
DATA_DIR = os.path.join("..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

def retrieve_documents():
    """
    Skill: retrieve_documents
    Loads all 3 policy files and indexes them by document name and section number.
    """
    corpus = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            # Fallback for different working directories if needed
            filepath = os.path.join("data", "policy-documents", filename)
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple regex to split by sections (e.g., 2. ANNUAL LEAVE or 2.1 This policy...)
                # This finds headers and sub-sections
                sections = re.split(r'\n(?=\d+\.\s)', content)
                doc_sections = []
                for sec in sections:
                    lines = sec.strip().split('\n')
                    if lines:
                        header = lines[0].strip()
                        body = "\n".join(lines[1:]).strip()
                        doc_sections.append({
                            "header": header,
                            "content": body,
                            "full_text": sec.strip()
                        })
                corpus[filename] = doc_sections
        except FileNotFoundError:
            print(f"Warning: {filename} not found.")
            continue
    return corpus

def answer_question(user_question, indexed_data):
    """
    Skill: answer_question
    Searches the indexed documents and returns a single-source answer + citation or refusal.
    Ensures no cross-document blending and no hedging.
    """
    user_question = user_question.lower()
    matches = []

    # Simple keyword-based scoring for "vibe" search
    keywords = set(re.findall(r'\w+', user_question))
    
    # Stop words to filter out
    stop_words = {'can', 'i', 'the', 'is', 'a', 'to', 'for', 'of', 'in', 'on', 'with', 'what', 'who'}
    filtered_keywords = keywords - stop_words

    for doc_name, sections in indexed_data.items():
        for sec in sections:
            # Check for header matches (weight 5) or content matches (weight 1)
            score = 0
            for kw in filtered_keywords:
                if kw in sec['header'].lower():
                    score += 5
                if kw in sec['content'].lower():
                    score += 1
            
            if score > 0:
                matches.append({
                    "doc_name": doc_name,
                    "section": sec['header'],
                    "content": sec['content'],
                    "score": score
                })

    # Rule enforcement: "Single-source attribution"
    # Sort by score
    matches = sorted(matches, key=lambda x: x['score'], reverse=True)

    if not matches or matches[0]['score'] < 2:
        return REFUSAL_TEMPLATE

    # Check for ambiguity: If top two matches are from different documents and have near identical scores
    if len(matches) > 1:
        top_match = matches[0]
        second_match = matches[1]
        # Ambiguity rule: if scores are close and docs are different, be careful
        if top_match['doc_name'] != second_match['doc_name'] and (top_match['score'] - second_match['score']) < 3:
            # The cross-doc test question (personal phone) often hits both IT and HR.
            # If we can't definitively pick one source, we refuse to blend.
            return REFUSAL_TEMPLATE

    # Fulfill intent: "Direct, cited response without interpretation or creative blending"
    best = matches[0]
    # Clean up the output to include citation
    # Note: agents.md requires: "Answer text [Document Name Section Number]"
    
    # We find the specific sentence(s) that match to avoid dumping a giant block
    sentences = best['content'].split('.')
    answer_parts = []
    for sent in sentences:
        if any(kw in sent.lower() for kw in filtered_keywords):
            answer_parts.append(sent.strip())
    
    if not answer_parts:
        final_answer = best['content']
    else:
        final_answer = ". ".join(answer_parts[:2]) + "."

    # Citation enforcement
    citation = f"[{best['doc_name']} Section {best['section']}]"
    
    return f"{final_answer} {citation}"

def main():
    print("=== CMC Policy Compliance Assistant ===")
    print("Operational boundary: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("Type 'exit' to quit.\n")
    
    indexed_data = retrieve_documents()
    
    if not indexed_data:
        print("Error: No policy documents found. Please check data/policy-documents/")
        return

    while True:
        try:
            user_input = input("Question: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue
                
            answer = answer_question(user_input, indexed_data)
            print(f"\nAnswer: {answer}\n")
            print("-" * 40)
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
