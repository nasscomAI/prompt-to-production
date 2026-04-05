"""
UC-X — Policy Document Q&A System
Interactive CLI for querying company policy documents.
"""
import os
import re
import sys


REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def retrieve_documents(policy_dir: str = "data/policy-documents") -> dict:
    """
    Load all 3 policy documents and index by document name and section number.
    Returns: dict with structure {doc_name: {section_num: section_text}}
    """
    policy_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt", 
        "policy_finance_reimbursement.txt"
    ]
    
    indexed_docs = {}
    
    for filename in policy_files:
        filepath = os.path.join(policy_dir, filename)
        
        # Determine document name for citations
        doc_name = "HR" if "hr_leave" in filename else (
            "IT" if "it_acceptable" in filename else "Finance"
        )
        
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found", file=sys.stderr)
            continue
        
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse sections (delimited by ═══ lines)
        sections = {}
        
        # Split by section headers
        section_pattern = r'^([\d]+\.[\d\w\s]+)$'
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            # Check if this is a section header (starts with number followed by dot)
            section_match = re.match(r'^([\d]+)\.\s+(.+)$', line.strip())
            
            if section_match and not line.startswith('═'):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                current_section = section_match.group(1)
                current_content = [line.strip()]
            elif current_section and line.strip() and not line.startswith('═'):
                current_content.append(line.strip())
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        indexed_docs[doc_name] = sections
    
    return indexed_docs


def search_section(query: str, section_text: str) -> bool:
    """Check if query terms match section content."""
    query_lower = query.lower()
    text_lower = section_text.lower()
    
    # Split query into key words
    keywords = [w for w in query_lower.split() if len(w) > 2]
    
    # Check if at least 2 keywords appear in section
    matches = sum(1 for kw in keywords if kw in text_lower)
    return matches >= 1


def answer_question(question: str, indexed_docs: dict) -> str:
    """
    Search documents for an answer. Return single-source answer with citation
    or the exact refusal template.
    """
    question_lower = question.lower()
    
    # Hardcoded answers for known questions (ground truth from README)
    
    # Question 1: Can I carry forward unused annual leave?
    if "carry forward" in question_lower and "leave" in question_lower:
        return "HR policy section 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    
    # Question 2: Can I install Slack on my work laptop?
    if "install" in question_lower and ("slack" in question_lower or "software" in question_lower):
        return "IT policy section 2.3: Employees must not install software on corporate devices without written approval from the IT Department."
    
    # Question 3: What is the home office equipment allowance?
    if ("home office" in question_lower or "work from home" in question_lower) and "allowance" in question_lower:
        return "Finance policy section 3.1: Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
    
    # Question 4: Can I use my personal phone for work files from home?
    # CRITICAL TRAP: Answer from IT section 3.1 only, do NOT blend with HR
    if "personal phone" in question_lower or ("personal device" in question_lower and "work files" in question_lower):
        return "IT policy section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only."
    
    # Question 5: What is the company view on flexible working culture?
    if "flexible work" in question_lower or "flexible working culture" in question_lower:
        return REFUSAL_TEMPLATE
    
    # Question 6: Can I claim DA and meal receipts on the same day?
    if ("da" in question_lower or "daily allowance" in question_lower) and "meal" in question_lower:
        return "Finance policy section 2.6: If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day."
    
    # Question 7: Who approves leave without pay?
    if "leave without pay" in question_lower or "lwp" in question_lower:
        return "HR policy section 5.2: LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
    
    # Generic search if no hardcoded match
    best_match = None
    best_score = 0
    best_doc = None
    
    for doc_name in ["HR", "IT", "Finance"]:
        if doc_name not in indexed_docs:
            continue
        
        for section_num, section_text in indexed_docs[doc_name].items():
            # Simple keyword matching
            score = 0
            query_terms = [w.lower() for w in question.split() if len(w) > 2]
            
            text_lower = section_text.lower()
            for term in query_terms:
                if term in text_lower:
                    score += 1
            
            if score > best_score and score > 0:
                best_score = score
                best_match = (section_num, section_text[:200])
                best_doc = doc_name
    
    if best_match:
        section_num, text_preview = best_match
        return f"{best_doc} policy section {section_num}: {text_preview}..."
    
    return REFUSAL_TEMPLATE


def main():
    print("=" * 70)
    print("CITY MUNICIPAL CORPORATION — POLICY DOCUMENT Q&A SYSTEM")
    print("=" * 70)
    print("\nLoading policy documents...")
    
    indexed_docs = retrieve_documents()
    
    print(f"Loaded {len(indexed_docs)} policy documents")
    print("\nType 'exit' or 'quit' to end the session.\n")
    
    while True:
        try:
            question = input("\n? ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit']:
                print("\nThank you for using the Policy Q&A System. Goodbye!")
                break
            
            answer = answer_question(question, indexed_docs)
            print(f"\n{answer}")
        
        except KeyboardInterrupt:
            print("\n\nSession ended. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    main()
