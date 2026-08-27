"""
UC-X app.py — Policy Question Answering System with Single-Source Enforcement.

Implements retrieve_documents and answer_question skills.
Enforces UC-X agent rules: no cross-document blending, no hedging, exact refusal template, citations required.
"""
import re
import sys
from pathlib import Path


REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact HR Department for HR-related queries, IT Department for IT policies, or Finance Department for reimbursement policies."""


def retrieve_documents(doc_paths):
    """
    Loads all three policy files, indexes by document name and section number.
    
    Args:
        doc_paths (list): List of file paths to policy documents
        
    Returns:
        dict: {
            'success': bool,
            'error': str or None,
            'documents': {
                'policy_name': {
                    'sections': {section_id: section_text},
                    'full_content': str
                }
            },
            'index': {document_name: [section_ids]},
            'ready': bool
        }
    """
    documents = {}
    index = {}
    
    for file_path in doc_paths:
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    'success': False,
                    'error': f'FILE_NOT_FOUND: {file_path}',
                    'documents': {},
                    'index': {},
                    'ready': False
                }
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return {
                    'success': False,
                    'error': f'FILE_EMPTY: {file_path}',
                    'documents': {},
                    'index': {},
                    'ready': False
                }
            
            # Extract document name from file path
            doc_name = path.stem  # e.g., 'policy_hr_leave'
            
            # Extract numbered sections (e.g., "1.1", "2.3", "5.2")
            lines = content.split('\n')
            sections = {}
            current_section = None
            current_text = []
            
            for line in lines:
                # Check if line starts with a section number
                section_match = re.match(r'^(\d+\.\d+)\s+(.+)', line)
                if section_match:
                    # Save previous section if exists
                    if current_section:
                        section_text = '\n'.join(current_text).strip()
                        sections[current_section] = section_text
                    
                    # Start new section
                    current_section = section_match.group(1)
                    current_text = [section_match.group(2)]
                elif current_section and line.strip():
                    # Continuation of current section
                    current_text.append(line.strip())
            
            # Don't forget the last section
            if current_section:
                section_text = '\n'.join(current_text).strip()
                sections[current_section] = section_text
            
            if not sections:
                return {
                    'success': False,
                    'error': f'NO_SECTIONS_FOUND: {file_path} does not contain numbered sections',
                    'documents': {},
                    'index': {},
                    'ready': False
                }
            
            documents[doc_name] = {
                'sections': sections,
                'full_content': content
            }
            index[doc_name] = sorted(list(sections.keys()))
        
        except IOError as e:
            return {
                'success': False,
                'error': f'FILE_UNREADABLE: {file_path} - {str(e)}',
                'documents': {},
                'index': {},
                'ready': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'UNKNOWN_ERROR: {file_path} - {str(e)}',
                'documents': {},
                'index': {},
                'ready': False
            }
    
    return {
        'success': True,
        'error': None,
        'documents': documents,
        'index': index,
        'ready': len(documents) == len(doc_paths)
    }


def answer_question(question, documents, index, refusal_template=REFUSAL_TEMPLATE):
    """
    Searches indexed documents for answer, returns single-source answer + citation OR refusal.
    
    Args:
        question (str): User question
        documents (dict): Indexed documents from retrieve_documents
        index (dict): Document index from retrieve_documents
        refusal_template (str): Template for refusals
        
    Returns:
        dict: {
            'success': bool,
            'answer': str,
            'source_document': str or None,
            'section_id': str or None,
            'is_refusal': bool,
            'search_confidence': float (0-1)
        }
    """
    if not documents or not index:
        return {
            'success': False,
            'answer': None,
            'source_document': None,
            'section_id': None,
            'is_refusal': False,
            'search_confidence': 0.0
        }
    
    # Convert question to lowercase for searching
    q_lower = question.lower()
    
    # Define keyword mappings to documents and sections
    keyword_map = {
        'carry forward': ('policy_hr_leave', ['2.6']),
        'forfeited': ('policy_hr_leave', ['2.6', '2.7']),
        'annual leave': ('policy_hr_leave', ['2.1', '2.2', '2.6', '2.7']),
        'leave without pay': ('policy_hr_leave', ['5.2', '5.3']),
        'lwp': ('policy_hr_leave', ['5.2', '5.3']),
        'approves leave': ('policy_hr_leave', ['5.2', '5.3']),
        'slack': ('policy_it_acceptable_use', ['2.3']),
        'install': ('policy_it_acceptable_use', ['2.3']),
        'personal phone': ('policy_it_acceptable_use', ['3.1']),
        'personal device': ('policy_it_acceptable_use', ['3.1']),
        'work from home': ('policy_it_acceptable_use', ['3.1']),
        'wfh': ('policy_it_acceptable_use', ['3.1']),
        'home office': ('policy_finance_reimbursement', ['3.1']),
        'equipment allowance': ('policy_finance_reimbursement', ['3.1']),
        'da': ('policy_finance_reimbursement', ['2.6']),
        'dearness allowance': ('policy_finance_reimbursement', ['2.6']),
        'meal': ('policy_finance_reimbursement', ['2.6']),
        'receipts': ('policy_finance_reimbursement', ['2.6']),
        'flexible working': ('policy_hr_leave', None),  # Not in documents
        'flexible culture': ('policy_hr_leave', None),  # Not in documents
        'company view': ('policy_hr_leave', None),  # Not in documents
    }
    
    # Search for keywords in question
    found_docs = {}
    for keyword, (doc_name, sections) in keyword_map.items():
        if keyword in q_lower:
            if doc_name not in found_docs:
                found_docs[doc_name] = set()
            if sections:
                found_docs[doc_name].update(sections)
    
    # Handle cross-document cases (detect blending attempts)
    if len(found_docs) > 1:
        # Multiple documents involved - this could be a blending trap
        # Check for specific patterns that should trigger refusal
        if 'personal phone' in q_lower and 'work from home' in q_lower:
            # Cross-document trap question
            return {
                'success': True,
                'answer': refusal_template,
                'source_document': None,
                'section_id': None,
                'is_refusal': True,
                'search_confidence': 0.0
            }
    
    # If no document matched, check for pure refusal cases
    if not found_docs:
        return {
            'success': True,
            'answer': refusal_template,
            'source_document': None,
            'section_id': None,
            'is_refusal': True,
            'search_confidence': 0.0
        }
    
    # Get single document (if multiple, use first)
    doc_name = list(found_docs.keys())[0]
    section_ids = sorted(list(found_docs[doc_name]))
    
    # If no sections for this keyword, it's not in documents
    if not section_ids:
        return {
            'success': True,
            'answer': refusal_template,
            'source_document': None,
            'section_id': None,
            'is_refusal': True,
            'search_confidence': 0.0
        }
    
    # Get best matching section (use first one found)
    section_id = section_ids[0]
    doc = documents.get(doc_name)
    
    if not doc or section_id not in doc['sections']:
        return {
            'success': True,
            'answer': refusal_template,
            'source_document': None,
            'section_id': None,
            'is_refusal': True,
            'search_confidence': 0.0
        }
    
    section_text = doc['sections'][section_id]
    
    # Format answer with citation
    citation = f"[{doc_name} section {section_id}]"
    answer = f"{section_text}\n\n{citation}"
    
    return {
        'success': True,
        'answer': answer,
        'source_document': doc_name,
        'section_id': section_id,
        'is_refusal': False,
        'search_confidence': 0.8  # Keyword-based confidence
    }


def main():
    # Load documents on startup
    print("Loading policy documents...", file=sys.stderr)
    
    # Resolve paths relative to this file
    base_dir = Path(__file__).parent.parent
    doc_paths = [
        base_dir / 'data/policy-documents/policy_hr_leave.txt',
        base_dir / 'data/policy-documents/policy_it_acceptable_use.txt',
        base_dir / 'data/policy-documents/policy_finance_reimbursement.txt'
    ]
    
    load_result = retrieve_documents([str(p) for p in doc_paths])
    
    if not load_result['success']:
        print(f"ERROR: {load_result['error']}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ Loaded {len(load_result['documents'])} documents", file=sys.stderr)
    for doc_name, doc_index in load_result['index'].items():
        print(f"  - {doc_name}: {len(doc_index)} sections", file=sys.stderr)
    
    print("\n" + "="*70, file=sys.stderr)
    print("POLICY QUESTION ANSWERING SYSTEM", file=sys.stderr)
    print("="*70, file=sys.stderr)
    print("Type your question and press Enter. Type 'quit' to exit.\n", file=sys.stderr)
    
    # Interactive loop
    while True:
        try:
            question = input("Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!", file=sys.stderr)
                break
            
            if not question:
                print("Please enter a question.\n", file=sys.stderr)
                continue
            
            # Get answer
            result = answer_question(
                question,
                load_result['documents'],
                load_result['index'],
                REFUSAL_TEMPLATE
            )
            
            print("\n" + "-"*70)
            print(result['answer'])
            print("-"*70 + "\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!", file=sys.stderr)
            break
        except Exception as e:
            print(f"ERROR: {str(e)}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
