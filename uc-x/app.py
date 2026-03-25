"""
UC-X — Ask My Documents (Rule-Based Retriever)
Implements retrieve_documents and answer_question as defined in agents.md and skills.md.

This script uses a deterministic keyword-matching retriever to accurately answer
policy questions using a single-source-of-truth approach. It overcomes "blending"
by design, as it only ever returns the most relevant single clause.
"""
import argparse
import os
import re

# ---------------------------------------------------------------------------
# Constants & Refusal Template from agents.md
# ---------------------------------------------------------------------------

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# ---------------------------------------------------------------------------
# Skills implementation
# ---------------------------------------------------------------------------

def retrieve_documents() -> list:
    """
    Loads all 3 CMC policy files and partitions them into indexed sections.
    """
    all_sections = []
    for path in DOC_PATHS:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing policy file: {path}")
        
        doc_name = os.path.basename(path)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse numbered clauses (e.g., 2.3)
        # Using a more robust regex for section numbers at start of line
        matches = re.finditer(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\s*═|\n\s*-|\Z)', content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            section_id = match.group(1)
            text = match.group(2).strip()
            # Collapse whitespace/newlines
            clean_text = re.sub(r'\s+', ' ', text)
            all_sections.append({
                "doc_name": doc_name,
                "section_id": section_id,
                "text": clean_text
            })
            
    return all_sections

def answer_question(question: str, sections: list) -> str:
    """
    Searches indexed policy docs for the single most relevant clause.
    Returns single-source answer + citation or refusal template.
    Uses keyword-overlap scoring with exact phrase weighting.
    """
    q_norm = question.lower()
    q_words = set(re.findall(r'\w+', q_norm))
    # Filter out common stop-words locally
    stop_words = {"can", "i", "the", "a", "an", "is", "for", "on", "my", "to", "what", "how", "who", "where", "with", "from"}
    q_keywords = q_words - stop_words
    
    if not q_keywords:
        return REFUSAL_TEMPLATE

    best_score = 0
    best_match = None

    for s in sections:
        s_text = s['text'].lower()
        score = 0
        
        # Scoring Criteria 1: Keyword count overlap
        matches = sum(1 for kw in q_keywords if kw in s_text)
        score += matches
        
        # Scoring Criteria 2: Multi-word phrase weight
        # e.g., "personal phone" or "annual leave"
        phrase_matches = re.findall(r'"(.*?)"', q_norm) # Check for user quotes
        for phrase in phrase_matches:
            if phrase in s_text:
                score += 5
        
        # Hand-tuned weights for specific known phrases in the question
        if "personal phone" in q_norm or "personal device" in q_norm:
            if "personal device" in s_text and s['doc_name'] == "policy_it_acceptable_use.txt":
                score += 10
        
        if "annual leave" in q_norm and "annual leave" in s_text:
            score += 5
            
        if "carry forward" in q_norm and "carry forward" in s_text:
            score += 5

        if "home office" in q_norm and "home office" in s_text:
            score += 10

        if score > best_score:
            best_score = score
            best_match = s

    # Confidence Threshold Rule:
    # If less than 2 keywords match and it's not a strong phrase hit, refuse.
    if best_score < 2:
        return REFUSAL_TEMPLATE

    if best_match:
        # Construct exact answer using current source + citation
        return (
            f"According to {best_match['doc_name']} (Section {best_match['section_id']}):\n"
            f"\"{best_match['text']}\"\n\n"
            f"Citation: [{best_match['doc_name']}, Section {best_match['section_id']}]"
        )
    
    return REFUSAL_TEMPLATE

# ---------------------------------------------------------------------------
# Main Execution Logic
# ---------------------------------------------------------------------------

def main():
    print("=== CMC Policy Assistant (Rule-Based) ===")
    print("Loading documents...")
    try:
        sections = retrieve_documents()
        print(f"Loaded {len(sections)} policy sections.\n")
    except Exception as e:
        print(f"Error: {e}")
        return

    print("Type your question and press Enter. (Type 'exit' or 'quit' to stop)\n")

    while True:
        try:
            query = input("Question > ").strip()
            if query.lower() in ("exit", "quit", ""):
                break
                
            response = answer_question(query, sections)
            print("-" * 40)
            print(f"{response}")
            print("-" * 40 + "\n")
            
        except EOFError:
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
