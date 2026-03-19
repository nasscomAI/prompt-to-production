"""
UC-X — Policy Document Q&A Agent
Built using RICE + agents.md + skills.md + CRAFT workflow.
Interactive CLI for answering policy questions with single-source citations or refusals.
"""
import re
from typing import Dict, List, Optional


# Refusal template from agents.md
REFUSAL_TEMPLATE = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact {team} for guidance."


def retrieve_documents(file_paths: List[str]) -> Dict:
    """
    Loads all three policy text files and indexes by document name and section number.
    
    Args:
        file_paths: List of paths to the three policy documents
        
    Returns:
        Dictionary with document names as keys and indexed sections
        
    Raises:
        FileNotFoundError: If any required file is missing
        ValueError: If files are empty or lack recognizable structure
    """
    documents = {}
    missing_files = []
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            missing_files.append(file_path)
            continue
        
        if not content.strip():
            raise ValueError(f"File is empty: {file_path}")
        
        # Extract document name from path
        doc_name = file_path.split('/')[-1]
        
        # Parse sections
        sections = []
        lines = content.split('\n')
        
        # Pattern to match section headers like "2. ANNUAL LEAVE"
        section_pattern = re.compile(r'^(\d+)\.\s+([A-Z][A-Z\s&\-]+)$')
        # Pattern to match clauses like "2.1 Text..."
        clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.+)$')
        
        current_section = None
        current_clause = None
        
        for line in lines:
            line_stripped = line.strip()
            
            if not line_stripped or line_stripped.startswith('='):
                continue
            
            # Check for section header
            section_match = section_pattern.match(line_stripped)
            if section_match:
                # Save previous clause and section
                if current_clause and current_section:
                    current_section['clauses'].append(current_clause)
                    current_clause = None
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    'number': section_match.group(1),
                    'title': section_match.group(2).strip(),
                    'clauses': []
                }
                continue
            
            # Check for clause
            clause_match = clause_pattern.match(line_stripped)
            if clause_match and current_section:
                # Save previous clause
                if current_clause:
                    current_section['clauses'].append(current_clause)
                
                current_clause = {
                    'number': clause_match.group(1),
                    'text': clause_match.group(2).strip()
                }
                continue
            
            # Continuation line for current clause
            if current_clause and line_stripped:
                current_clause['text'] += ' ' + line_stripped
        
        # Save last clause and section
        if current_clause and current_section:
            current_section['clauses'].append(current_clause)
        if current_section:
            sections.append(current_section)
        
        if not sections:
            raise ValueError(f"No recognizable section structure in: {file_path}")
        
        documents[doc_name] = {'sections': sections}
    
    if missing_files:
        raise FileNotFoundError(f"Missing required files: {', '.join(missing_files)}")
    
    return documents


def answer_question(documents: Dict, question: str) -> Dict:
    """
    Searches indexed documents for answer, returns single-source citation OR refusal template.
    
    Args:
        documents: Indexed documents from retrieve_documents
        question: User's natural language question
        
    Returns:
        Dictionary with answer, source_document, section, and answer_type
        
    Raises:
        ValueError: If document structure is invalid
    """
    question_lower = question.lower()
    
    # Keyword mapping for finding relevant sections
    keyword_mapping = {
        'leave': ['policy_hr_leave.txt'],
        'annual leave': ['policy_hr_leave.txt'],
        'sick leave': ['policy_hr_leave.txt'],
        'maternity': ['policy_hr_leave.txt'],
        'paternity': ['policy_hr_leave.txt'],
        'carry forward': ['policy_hr_leave.txt'],
        'encash': ['policy_hr_leave.txt'],
        'laptop': ['policy_it_acceptable_use.txt'],
        'device': ['policy_it_acceptable_use.txt'],
        'phone': ['policy_it_acceptable_use.txt'],
        'install': ['policy_it_acceptable_use.txt'],
        'software': ['policy_it_acceptable_use.txt'],
        'password': ['policy_it_acceptable_use.txt'],
        'email': ['policy_it_acceptable_use.txt'],
        'reimbursement': ['policy_finance_reimbursement.txt'],
        'travel': ['policy_finance_reimbursement.txt'],
        'expense': ['policy_finance_reimbursement.txt'],
        'allowance': ['policy_finance_reimbursement.txt'],
        'training': ['policy_finance_reimbursement.txt'],
        'meal': ['policy_finance_reimbursement.txt'],
        'da': ['policy_finance_reimbursement.txt'],
        'daily allowance': ['policy_finance_reimbursement.txt'],
        'home office': ['policy_finance_reimbursement.txt'],
        'work from home': ['policy_finance_reimbursement.txt']
    }
    
    # Find relevant documents
    relevant_docs = set()
    for keyword, docs in keyword_mapping.items():
        if keyword in question_lower:
            relevant_docs.update(docs)
    
    # If no relevant documents found, use refusal
    if not relevant_docs:
        team = 'HR'  # Default
        return {
            'answer': REFUSAL_TEMPLATE.format(team=team),
            'source_document': None,
            'section': None,
            'answer_type': 'refusal'
        }
    
    # Search for answer in relevant documents
    best_match = None
    best_score = 0
    
    for doc_name in relevant_docs:
        if doc_name not in documents:
            continue
        
        doc = documents[doc_name]
        for section in doc['sections']:
            for clause in section['clauses']:
                clause_text_lower = clause['text'].lower()
                
                # Simple keyword matching score
                score = sum(1 for word in question_lower.split() if len(word) > 3 and word in clause_text_lower)
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        'document': doc_name,
                        'section': clause['number'],
                        'text': clause['text'],
                        'section_title': section['title']
                    }
    
    # If no good match found, use refusal
    if not best_match or best_score == 0:
        # Determine team based on relevant docs
        if 'policy_hr_leave.txt' in relevant_docs:
            team = 'HR'
        elif 'policy_it_acceptable_use.txt' in relevant_docs:
            team = 'IT'
        elif 'policy_finance_reimbursement.txt' in relevant_docs:
            team = 'Finance'
        else:
            team = 'the appropriate department'
        
        return {
            'answer': REFUSAL_TEMPLATE.format(team=team),
            'source_document': None,
            'section': None,
            'answer_type': 'refusal'
        }
    
    # Format answer with citation
    doc_short_name = best_match['document'].replace('policy_', '').replace('.txt', '').replace('_', ' ').title()
    answer = f"According to {doc_short_name} Policy section {best_match['section']}: {best_match['text']}"
    
    return {
        'answer': answer,
        'source_document': best_match['document'],
        'section': best_match['section'],
        'answer_type': 'citation'
    }


def main():
    """
    Main entry point for interactive policy Q&A CLI.
    """
    print("=" * 70)
    print("UC-X — Policy Document Q&A Agent")
    print("=" * 70)
    print("\nLoading policy documents...")
    
    # Define policy file paths
    policy_files = [
        '../data/policy-documents/policy_hr_leave.txt',
        '../data/policy-documents/policy_it_acceptable_use.txt',
        '../data/policy-documents/policy_finance_reimbursement.txt'
    ]
    
    try:
        documents = retrieve_documents(policy_files)
        
        # Count total sections
        total_sections = sum(len(doc['sections']) for doc in documents.values())
        total_clauses = sum(
            len(clause) 
            for doc in documents.values() 
            for section in doc['sections'] 
            for clause in [section['clauses']]
        )
        
        print(f"✓ Loaded {len(documents)} policy documents")
        print(f"✓ Indexed {total_sections} sections")
        print(f"✓ Ready to answer questions")
        print("\nAvailable policies:")
        print("  - HR Leave Policy (policy_hr_leave.txt)")
        print("  - IT Acceptable Use Policy (policy_it_acceptable_use.txt)")
        print("  - Finance Reimbursement Policy (policy_finance_reimbursement.txt)")
        print("\n" + "=" * 70)
        print("\nType your question (or 'quit' to exit):\n")
        
        while True:
            try:
                question = input("Q: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nExiting Policy Q&A Agent. Goodbye!")
                    break
                
                # Get answer
                result = answer_question(documents, question)
                
                print(f"\nA: {result['answer']}")
                
                if result['answer_type'] == 'citation':
                    print(f"   [Source: {result['source_document']}, Section {result['section']}]")
                
                print()
                
            except KeyboardInterrupt:
                print("\n\nExiting Policy Q&A Agent. Goodbye!")
                break
            except Exception as e:
                print(f"\nError processing question: {e}\n")
    
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading documents: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
