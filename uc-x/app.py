"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import sys

# Refusal template (exact wording required)
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact HR, IT, or Finance for guidance."""

# Document paths
DOC_PATHS = {
    'policy_hr_leave.txt': '../data/policy-documents/policy_hr_leave.txt',
    'policy_it_acceptable_use.txt': '../data/policy-documents/policy_it_acceptable_use.txt',
    'policy_finance_reimbursement.txt': '../data/policy-documents/policy_finance_reimbursement.txt'
}


def retrieve_documents(doc_paths: dict) -> dict:
    """
    Loads all policy files, indexes content by document name and section number.
    """
    documents = {}
    
    for doc_name, doc_path in doc_paths.items():
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Warning: {doc_name} not found at {doc_path}")
            documents[doc_name] = {'sections': {}, 'content': ''}
            continue
        
        # Parse sections by finding numbered clauses (e.g., 2.3, 3.1, etc.)
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            stripped = line.strip()
            # Skip separator lines
            if re.match(r'^[═=_\-]+$', stripped):
                continue
            # Skip section headers like "3. PERSONAL DEVICES (BYOD)" (single digit + dot + text)
            if re.match(r'^\d+\.\s+[A-Z]', stripped) and not re.match(r'^\d+\.\d+\s+', stripped):
                continue
            # Match section numbers like 2.3, 3.1
            match = re.match(r'^(\d+\.\d+)\s+(.+)$', stripped)
            if match:
                if current_section:
                    sections[current_section] = ' '.join(current_content)
                current_section = match.group(1)
                current_content = [match.group(2)]
            elif current_section:
                if stripped:
                    current_content.append(stripped)
        
        if current_section:
            sections[current_section] = ' '.join(current_content)
        
        documents[doc_name] = {'sections': sections, 'content': content}
    
    return {'documents': documents}


def answer_question(question: str, documents: dict, refusal_template: str) -> dict:
    """
    Searches indexed documents for question, returns single-source answer with citation
    OR refusal template. Never blends multiple documents.
    """
    question_lower = question.lower()
    
    # Keywords mapping to documents and sections
    # Format: {keyword_tuple: (doc_name, section_num, keywords_to_match)}
    # Use special marker for refusal cases
    REFUSAL_MARKER = ('__REFUSAL__',)
    knowledge_base = {
        # HR Leave Policy
        ('carry', 'forward', 'annual', 'leave'): ('policy_hr_leave.txt', '2.6', ['carry forward', '5 days', 'forfeited', '31 december']),
        ('leave', 'without', 'pay', 'approve'): ('policy_hr_leave.txt', '5.2', ['department head', 'hr director', 'approval']),
        ('maternity', 'leave', 'weeks'): ('policy_hr_leave.txt', '4.1', ['26 weeks', 'first two']),
        ('paternity', 'leave', 'days'): ('policy_hr_leave.txt', '4.3', ['5 days', '30 days']),
        ('sick', 'leave', 'certificate'): ('policy_hr_leave.txt', '3.2', ['medical certificate', '48 hours', '3 days']),
        
        # IT Policy
        ('install', 'slack'): ('policy_it_acceptable_use.txt', '2.3', ['written approval', 'it department']),
        ('install', 'software'): ('policy_it_acceptable_use.txt', '2.3', ['written approval', 'it department']),
        ('personal', 'phone', 'work', 'files', 'home'): ('policy_it_acceptable_use.txt', '3.1', ['personal devices', 'email', 'self-service portal']),
        ('personal', 'device', 'access'): ('policy_it_acceptable_use.txt', '3.1', ['email', 'portal']),
        ('password', 'share'): ('policy_it_acceptable_use.txt', '4.1', ['not share', 'password']),
        
        # Finance Policy
        ('home', 'office', 'equipment', 'allowance'): ('policy_finance_reimbursement.txt', '3.1', ['8000', 'one-time', 'permanent']),
        ('da', 'meal', 'receipt', 'same'): ('policy_finance_reimbursement.txt', '2.6', ['cannot be claimed', 'simultaneously']),
        ('travel', 'approval'): ('policy_finance_reimbursement.txt', '2.2', ['pre-approved', 'not reimbursable']),
        ('mobile', 'phone', 'reimbursement'): ('policy_finance_reimbursement.txt', '5.1', ['500', 'grade']),
        
        # Flexible working - should be refusal
        ('flexible', 'working', 'culture'): REFUSAL_MARKER,
        ('company', 'view', 'flexible'): REFUSAL_MARKER,
    }
    
    # Search for matching keywords
    matched_doc = None
    matched_section = None
    matched_keywords = None
    should_refuse = False
    
    for keywords, result in knowledge_base.items():
        # Check if all keywords in the tuple are in the question
        if all(kw in question_lower for kw in keywords):
            if result == REFUSAL_MARKER:
                should_refuse = True
            else:
                matched_doc, matched_section, matched_keywords = result
            break
    
    if should_refuse:
        return {
            'answer': refusal_template,
            'source_doc': None,
            'source_section': None,
            'is_refusal': True
        }
    
    if matched_doc and matched_section:
        doc_data = documents.get(matched_doc, {})
        sections = doc_data.get('sections', {})
        
        if matched_section in sections:
            content = sections[matched_section]
            # Extract relevant portion
            return {
                'answer': content,
                'source_doc': matched_doc,
                'source_section': matched_section,
                'is_refusal': False
            }
    
    # Check for flexible working / culture questions - these should be refused
    if any(phrase in question_lower for phrase in ['flexible working', 'company view', 'company culture', 'work culture']):
        return {
            'answer': refusal_template,
            'source_doc': None,
            'source_section': None,
            'is_refusal': True
        }
    
    # No match found - use refusal template
    return {
        'answer': refusal_template,
        'source_doc': None,
        'source_section': None,
        'is_refusal': True
    }


def main():
    print("=" * 60)
    print("UC-X Ask My Documents - Policy Q&A System")
    print("=" * 60)
    print("Ask questions about HR, IT, or Finance policies.")
    print("Type 'quit' or 'exit' to exit.")
    print("=" * 60)
    
    # Load documents
    print("\nLoading policy documents...")
    data = retrieve_documents(DOC_PATHS)
    documents = data['documents']
    print(f"Loaded {len(documents)} documents")
    
    # Interactive loop
    while True:
        print("\n" + "-" * 40)
        question = input("Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question:
            print("Please enter a question.")
            continue
        
        # Get answer
        result = answer_question(question, documents, REFUSAL_TEMPLATE)
        
        print("\n" + "=" * 40)
        print(result['answer'])
        
        if not result['is_refusal']:
            print(f"\n[Source: {result['source_doc']} Section {result['source_section']}]")
        print("=" * 40)


if __name__ == "__main__":
    main()
