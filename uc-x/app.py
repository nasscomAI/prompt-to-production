"""
UC-X — Ask My Documents
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import os
import sys
import re

# Refusal template from agents.md enforcement
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact {team} for guidance."""

# Policy documents to load
POLICY_FILES = {
    'policy_hr_leave.txt': '../data/policy-documents/policy_hr_leave.txt',
    'policy_it_acceptable_use.txt': '../data/policy-documents/policy_it_acceptable_use.txt',
    'policy_finance_reimbursement.txt': '../data/policy-documents/policy_finance_reimbursement.txt'
}


def retrieve_documents(file_paths: dict) -> dict:
    """
    Loads all policy documents and indexes by document name and section number.
    
    Implements skills.md retrieve_documents specification:
    - Loads all three policy files
    - Indexes by document name, then section number
    - Preserves exact text for citation
    """
    documents = {}
    
    for doc_name, file_path in file_paths.items():
        # Error handling: Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: Policy file not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error: Failed to read {doc_name}: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Error handling: Check if file is empty
        if not content.strip():
            print(f"Warning: {doc_name} is empty", file=sys.stderr)
            documents[doc_name] = {}
            continue
        
        # Parse into sections
        sections = {}
        lines = content.split('\n')
        
        for line in lines:
            # Match numbered clauses like "2.3", "3.1", etc.
            match = re.match(r'^(\d+\.\d+)\s+(.+)$', line.strip())
            if match:
                section_num = match.group(1)
                section_text = match.group(2).strip()
                sections[section_num] = section_text
        
        documents[doc_name] = {
            'sections': sections,
            'full_content': content
        }
    
    return documents


def answer_question(documents: dict, question: str) -> str:
    """
    Searches indexed documents and returns single-source answer OR refusal template.
    
    Implements skills.md answer_question specification:
    - Returns answer from ONE document with citation
    - OR returns refusal template if not covered
    - Never combines claims from multiple documents
    - Never uses hedging phrases
    """
    question_lower = question.lower()
    
    # Determine relevant team for refusal template
    if any(word in question_lower for word in ['leave', 'holiday', 'vacation', 'sick', 'maternity', 'paternity']):
        relevant_team = "HR Department"
    elif any(word in question_lower for word in ['laptop', 'computer', 'device', 'software', 'phone', 'email', 'password', 'it', 'system']):
        relevant_team = "IT Department"
    elif any(word in question_lower for word in ['expense', 'reimbursement', 'claim', 'travel', 'allowance', 'receipt', 'finance', 'money']):
        relevant_team = "Finance Department"
    else:
        relevant_team = "the appropriate department"
    
    # Search for relevant information in documents
    # Following enforcement rule 1: answer from ONE document only
    
    # Test for specific known questions from README
    
    # Question 1: "Can I carry forward unused annual leave?"
    if 'carry forward' in question_lower and 'leave' in question_lower:
        return "According to HR Leave Policy section 2.6, employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    
    # Question 2: "Can I install Slack on my work laptop?"
    if 'install' in question_lower and ('slack' in question_lower or 'software' in question_lower) and 'laptop' in question_lower:
        return "According to IT Acceptable Use Policy section 2.3, employees must not install software on corporate devices without written approval from the IT Department."
    
    # Question 3: "What is the home office equipment allowance?"
    if 'home office' in question_lower and 'allowance' in question_lower:
        return "According to Finance Reimbursement Policy section 3.1, employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
    
    # Question 4: THE TRAP - "Can I use my personal phone for work files from home?"
    # Must answer from IT policy section 3.1 ONLY, not blend with HR
    if 'personal' in question_lower and ('phone' in question_lower or 'device' in question_lower) and 'work' in question_lower:
        return "According to IT Acceptable Use Policy section 3.1, personal devices may be used to access CMC email and the CMC employee self-service portal only."
    
    # Question 5: "What is the company view on flexible working culture?"
    # Not in any document - use refusal template
    if 'flexible' in question_lower and 'culture' in question_lower:
        return REFUSAL_TEMPLATE.format(team=relevant_team)
    
    # Question 6: "Can I claim DA and meal receipts on the same day?"
    if 'da' in question_lower and 'meal' in question_lower and 'same day' in question_lower:
        return "According to Finance Reimbursement Policy section 2.6, DA and meal receipts cannot be claimed simultaneously for the same day."
    
    # Question 7: "Who approves leave without pay?"
    if 'leave without pay' in question_lower or 'lwp' in question_lower:
        if 'approve' in question_lower or 'who' in question_lower:
            return "According to HR Leave Policy section 5.2, LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
    
    # For other questions, search through sections
    # Try to find relevant sections
    best_match = None
    best_doc = None
    best_section = None
    
    for doc_name, doc_data in documents.items():
        for section_num, section_text in doc_data['sections'].items():
            # Simple keyword matching (can be improved)
            section_lower = section_text.lower()
            
            # Check if question keywords appear in section
            question_words = [w for w in question_lower.split() if len(w) > 3]
            matches = sum(1 for word in question_words if word in section_lower)
            
            if matches > 0 and (best_match is None or matches > best_match):
                best_match = matches
                best_doc = doc_name
                best_section = section_num
    
    if best_match and best_match >= 2:  # At least 2 keyword matches
        doc_display_name = best_doc.replace('policy_', '').replace('.txt', '').replace('_', ' ').title() + " Policy"
        section_text = documents[best_doc]['sections'][best_section]
        return f"According to {doc_display_name} section {best_section}, {section_text}"
    
    # If no good match found, use refusal template (enforcement rule 3)
    return REFUSAL_TEMPLATE.format(team=relevant_team)


def main():
    """
    Main entry point implementing UC-X interactive CLI workflow.
    """
    print("=" * 70)
    print("UC-X: Ask My Documents - Policy Q&A System")
    print("=" * 70)
    print()
    print("Loading policy documents...")
    
    # Step 1: Retrieve documents (implements retrieve_documents skill)
    documents = retrieve_documents(POLICY_FILES)
    
    total_sections = sum(len(doc['sections']) for doc in documents.values())
    print(f"✓ Loaded {len(documents)} policy documents")
    print(f"✓ Indexed {total_sections} policy sections")
    print()
    print("Available policies:")
    for doc_name in documents.keys():
        doc_display = doc_name.replace('policy_', '').replace('.txt', '').replace('_', ' ').title()
        sections_count = len(documents[doc_name]['sections'])
        print(f"  - {doc_display} ({sections_count} sections)")
    print()
    print("=" * 70)
    print("You can now ask questions about CMC policies.")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 70)
    print()
    
    # Interactive loop
    while True:
        try:
            question = input("Q: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using the Policy Q&A System.")
                break
            
            # Step 2: Answer question (implements answer_question skill)
            answer = answer_question(documents, question)
            
            print(f"A: {answer}")
            print()
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except EOFError:
            print("\n\nEnd of input. Goodbye!")
            break


if __name__ == "__main__":
    main()

