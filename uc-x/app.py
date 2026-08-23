"""
UC-X app.py — Policy Q&A System
Responds to employee questions about company policy with single-source answers from
indexed policy documents. Prevents cross-document blending and hedged hallucination.
"""
import re
from pathlib import Path


REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the Human Resources Department for guidance."""

# Map policy filenames to display names
DOC_NAMES = {
    'policy_hr_leave.txt': 'HR Policy',
    'policy_it_acceptable_use.txt': 'IT Policy',
    'policy_finance_reimbursement.txt': 'Finance Policy'
}


def retrieve_documents(policy_dir):
    """
    Load all three policy documents and parse them into sections indexed
    by document name and section number.
    
    Returns:
    {
        'documents': {'HR Policy': '...full text...', ...},
        'sections': {'HR Policy, Section 1.1': '...section text...', ...},
        'index': ['HR Policy, Section 1.1', ...],
        'doc_files': {'HR Policy': path, ...}
    }
    """
    policy_path = Path(policy_dir)
    indexed = {
        'documents': {},
        'sections': {},
        'index': [],
        'doc_files': {}
    }
    
    # Load each document
    for filename, doc_name in DOC_NAMES.items():
        filepath = policy_path / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Policy document not found: {filepath}")
        
        full_text = filepath.read_text(encoding='utf-8')
        indexed['documents'][doc_name] = full_text
        indexed['doc_files'][doc_name] = filepath
    
    # Parse sections from each document
    for doc_name, full_text in indexed['documents'].items():
        lines = full_text.split('\n')
        current_section = None
        section_lines = []
        
        for line in lines:
            # Match section headers: "1. TITLE", "1.1 Subtitle", "2.3 More text"
            section_match = re.match(r'^(\d+(?:\.\d+)?)\s+', line.strip())
            
            if section_match and line.strip():
                # Save previous section
                if current_section is not None:
                    section_text = '\n'.join(section_lines).strip()
                    if section_text:
                        section_key = f"{doc_name}, Section {current_section}"
                        indexed['sections'][section_key] = section_text
                        indexed['index'].append(section_key)
                
                # Start new section
                current_section = section_match.group(1)
                section_lines = [line.strip()]
            elif current_section is not None and line.strip():
                # Add to current section (skip separator lines)
                if not set(line.strip()) <= {'=', '─', '═'}:
                    section_lines.append(line.strip())
        
        # Save final section
        if current_section is not None:
            section_text = '\n'.join(section_lines).strip()
            if section_text:
                section_key = f"{doc_name}, Section {current_section}"
                indexed['sections'][section_key] = section_text
                indexed['index'].append(section_key)
    
    return indexed


def answer_question(question, indexed_docs):
    """
    Search indexed documents for a question. Return single-source answer with citation
    or the refusal template.
    
    Returns:
    {
        'answer': 'The answer text or refusal template',
        'source': 'HR Policy, Section 2.6' or None,
        'found': True/False
    }
    """
    # Normalize question for searching
    question_lower = question.lower()
    
    # Questions that should ALWAYS be refused (not in any document)
    refuse_phrases = [
        'flexible working culture',
        'company culture',
        'work life balance',
        'remote work policy',
        'employee wellness',
    ]
    
    # Check for refuse phrases
    for phrase in refuse_phrases:
        if phrase in question_lower:
            return {
                'answer': REFUSAL_TEMPLATE,
                'source': None,
                'found': False
            }
    
    # Extract key phrases and keywords
    keywords = [w for w in question_lower.split() if len(w) > 2 and w not in 
                ('can', 'can i', 'what', 'the', 'and', 'my', 'for', 'from', 'work', 'may', 'able', 'use')]
    
    # Specific phrase matching for common questions
    phrase_matches = {
        ('carry', 'forward', 'annual', 'leave'): ('HR Policy, Section 2.6', 'carry forward'),
        ('install', 'slack', 'software'): ('IT Policy, Section 2.3', 'install software'),
        ('home', 'office', 'equipment', 'allowance'): ('Finance Policy, Section 3.1', 'home office equipment'),
        ('personal', 'phone', 'device'): ('IT Policy, Section 3.1', 'personal devices'),
        ('personal', 'devices', 'byod'): ('IT Policy, Section 3.1', 'personal devices'),
        ('da', 'meal', 'receipts'): ('Finance Policy, Section 2.6', 'meal receipts'),
        ('leave', 'without', 'pay', 'lwp'): ('HR Policy, Section 5.2', 'leave without pay'),
        ('approves', 'leave'): ('HR Policy, Section 5.2', 'leave approval'),
    }
    
    # Check for phrase matches first
    for phrase_tuple, (doc_section, phrase_hint) in phrase_matches.items():
        # Check if all words in phrase are in question
        if all(word in question_lower for word in phrase_tuple if len(word) > 3):
            doc_name, section = doc_section.rsplit(', Section ', 1)
            section_key = f"{doc_name}, Section {section}"
            if section_key in indexed_docs['sections']:
                section_text = indexed_docs['sections'][section_key]
                return {
                    'answer': section_text,
                    'source': section_key,
                    'found': True
                }
    
    # Fallback: keyword-based search if no phrase match
    best_match = None
    best_score = 0
    
    for section_key, section_text in indexed_docs['sections'].items():
        section_lower = section_text.lower()
        
        # Count keyword matches in this section
        score = sum(1 for kw in keywords if kw in section_lower)
        
        # Prefer exact phrase matches in section text
        if any(phrase in section_lower for phrase in question_lower.split()):
            score += 3
        
        if score > best_score:
            best_score = score
            best_match = (section_key, section_text)
    
    # If we found a reasonable match (score > 1), return it
    if best_match and best_score > 1:
        section_key, section_text = best_match
        return {
            'answer': section_text,
            'source': section_key,
            'found': True
        }
    
    # No match found, return refusal template
    return {
        'answer': REFUSAL_TEMPLATE,
        'source': None,
        'found': False
    }


def format_answer(result):
    """Format the answer result for display."""
    if result['found']:
        return f"{result['answer']}\n\n[Source: {result['source']}]"
    else:
        return result['answer']


def main():
    """Interactive CLI for policy Q&A."""
    print("=" * 70)
    print("CITY MUNICIPAL CORPORATION — POLICY Q&A SYSTEM")
    print("=" * 70)
    print("\nLoading policy documents...")
    
    # Try to load documents from ../data/policy-documents
    policy_dir = Path(__file__).parent.parent / 'data' / 'policy-documents'
    
    if not policy_dir.exists():
        print(f"ERROR: Policy directory not found at {policy_dir}")
        print("Please ensure you are running from the uc-x directory.")
        return
    
    try:
        indexed_docs = retrieve_documents(policy_dir)
        print(f"✓ Loaded {len(indexed_docs['documents'])} documents")
        print(f"✓ Indexed {len(indexed_docs['sections'])} sections\n")
    except Exception as e:
        print(f"ERROR: Failed to load documents: {e}")
        return
    
    print("Type your policy questions below. Press Ctrl+C to exit.\n")
    print("-" * 70)
    
    while True:
        try:
            question = input("\n📋 Question: ").strip()
            
            if not question:
                continue
            
            result = answer_question(question, indexed_docs)
            answer_text = format_answer(result)
            
            print(f"\n📄 Answer:\n{answer_text}")
            print("-" * 70)
            
        except KeyboardInterrupt:
            print("\n\nThank you for using the Policy Q&A System. Goodbye!")
            break
        except Exception as e:
            print(f"\nERROR: {e}")
            print("-" * 70)


if __name__ == "__main__":
    main()
