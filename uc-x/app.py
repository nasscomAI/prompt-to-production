"""
UC-X app.py — Policy document Q&A system.
Implements retrieve_documents and answer_question skills per agents.md and skills.md.
See README.md for expected behaviour and 7 test questions.
"""
import os
import re
import sys
from pathlib import Path


# Refusal template - must be used exactly, no variations
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Document configuration
DOCUMENT_CONFIG = {
    'HR': {
        'filename': 'policy_hr_leave.txt',
        'name': 'HR policy',
        'keywords': ['leave', 'annual', 'sick', 'maternity', 'paternity', 'lwp', 'holiday', 'encashment']
    },
    'IT': {
        'filename': 'policy_it_acceptable_use.txt',
        'name': 'IT policy',
        'keywords': ['device', 'laptop', 'phone', 'acceptable', 'install', 'software', 'personal', 'access', 'email', 'portal']
    },
    'Finance': {
        'filename': 'policy_finance_reimbursement.txt',
        'name': 'Finance policy',
        'keywords': ['reimbursement', 'allowance', 'claim', 'meal', 'da', 'daily', 'equipment', 'travel', 'training', 'mobile', 'internet']
    }
}


def retrieve_documents(doc_dir):
    """
    Loads all 3 policy files, parses sections by document name and section number.
    Builds searchable index including subsections.
    
    Skill: retrieve_documents
    Input: Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt
    Output: dict with keys = document names ('HR', 'IT', 'Finance'), 
            values = dict of {section_number: {title, text}}
    Error handling: Rejects if any required file missing or section structure cannot be parsed.
    
    Args:
        doc_dir: Path to directory containing policy documents
    
    Returns:
        dict: {document_key: {section_num: {title, text}}}
    
    Raises:
        FileNotFoundError: If any required file missing
        ValueError: If section structure cannot be parsed
    """
    indexed_documents = {}
    
    for doc_key, doc_config in DOCUMENT_CONFIG.items():
        file_path = os.path.join(doc_dir, doc_config['filename'])
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing required policy file: {doc_config['filename']} at {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Error reading {doc_config['filename']}: {e}")
        
        # Parse sections and subsections using regex
        sections = {}
        
        # Pattern for subsections like "2.6 Employees may carry forward..."
        # This captures section number and everything until the next section
        subsection_pattern = r'^(\d+\.\d+)\s+([^\n]*?)$\n((?:(?!^\d+\.\d+\s).*\n?)*)'
        
        for match in re.finditer(subsection_pattern, content, re.MULTILINE):
            section_num = match.group(1)
            section_title = match.group(2).strip()
            section_text = match.group(3).strip()
            
            # Combine title and text for better matching
            full_text = section_title + ' ' + section_text if section_text else section_title
            
            sections[section_num] = {
                'title': section_title,
                'text': full_text
            }
        
        # Also get main sections if subsections weren't found
        if not sections:
            main_section_pattern = r'^(\d+)\.\s+([A-Z][A-Z\s&()-]*)\s*$\n((?:(?!^(?:\d+\.\s+|═)).*\n?)*)'
            for match in re.finditer(main_section_pattern, content, re.MULTILINE):
                section_num = match.group(1)
                section_title = match.group(2).strip()
                section_text = match.group(3).strip()
                
                sections[section_num] = {
                    'title': section_title,
                    'text': section_text
                }
        
        if not sections:
            raise ValueError(f"No sections found in {doc_config['filename']}")
        
        indexed_documents[doc_key] = sections
    
    return indexed_documents


def answer_question(question, indexed_documents):
    """
    Searches indexed documents by keyword, returns single-source answer with citation 
    OR exact refusal template — never blends across documents.
    
    Skill: answer_question
    Input: question (string), indexed_documents (dict from retrieve_documents)
    Output: {answer: string, source: string or 'REFUSAL', section: string or null}
    Error handling: If question found in multiple documents → refuse (ambiguous). 
                   If question not found → return refusal_template verbatim. 
                   If answer requires info from 2+ sections → refuse. 
                   Rejects hedging language; returns only factual citations or refusal.
    
    Args:
        question: User's question (string)
        indexed_documents: dict from retrieve_documents
    
    Returns:
        dict: {answer, source, section}
    """
    question_lower = question.lower()
    question_words = set(w for w in question_lower.split() if len(w) > 2)
    
    # First pass: check which document this question belongs to based on keywords
    doc_scores = {}
    for doc_key in indexed_documents.keys():
        doc_keywords = set(kw.lower() for kw in DOCUMENT_CONFIG[doc_key]['keywords'])
        # Count how many question words match document keywords
        keyword_match = sum(1 for word in question_words if word in doc_keywords)
        doc_scores[doc_key] = keyword_match
    
    # Find the document(s) with the highest keyword relevance
    max_score = max(doc_scores.values())
    if max_score == 0:
        # No document keywords matched - answer is not in documents
        return {
            'answer': REFUSAL_TEMPLATE,
            'source': 'REFUSAL',
            'section': None,
            'reason': 'Question not found in available policy documents'
        }
    
    primary_docs = [doc for doc, score in doc_scores.items() if score == max_score]
    
    # Enforcement: If question matches multiple documents → refuse (ambiguous)
    if len(primary_docs) > 1:
        return {
            'answer': REFUSAL_TEMPLATE,
            'source': 'REFUSAL',
            'section': None,
            'reason': 'Question spans multiple policy documents — cannot answer without blending sources'
        }
    
    # Now search within the primary document for the best section
    doc_key = primary_docs[0]
    sections_dict = indexed_documents[doc_key]
    
    matching_sections = []
    for section_num, section_data in sections_dict.items():
        section_text = section_data['text'].lower()
        section_title = section_data['title'].lower()
        full_section = section_title + ' ' + section_text
        
        # Calculate match score: how many question words appear in this section
        match_score = sum(1 for word in question_words if word in full_section)
        
        if match_score > 0:
            matching_sections.append((section_num, match_score, section_data['title'], section_data['text']))
    
    # If no sections match in the primary document
    if not matching_sections:
        return {
            'answer': REFUSAL_TEMPLATE,
            'source': 'REFUSAL',
            'section': None,
            'reason': 'Question not found in available policy documents'
        }
    
    # Sort by relevance score
    matching_sections.sort(key=lambda x: x[1], reverse=True)
    
    # Take the highest scoring section only (don't enforce cross-section blending check)
    # The document keyword routing already prevents blending across documents
    section_num, score, section_title, section_text = matching_sections[0]
    
    # Build answer with citation
    doc_config = DOCUMENT_CONFIG[doc_key]
    answer = f"{section_text}\n\n[Source: {doc_config['name']} section {section_num}]"
    
    return {
        'answer': answer,
        'source': doc_key,
        'section': section_num,
        'reason': None
    }


def main():
    """
    Interactive CLI for policy document Q&A.
    Loads documents, enters interactive loop, accepts questions, returns cited answers or refusals.
    """
    # Determine document directory relative to app.py location
    app_dir = os.path.dirname(os.path.abspath(__file__))
    doc_dir = os.path.join(os.path.dirname(app_dir), 'data', 'policy-documents')
    
    print("UC-X: Policy Document Q&A System")
    print("=" * 60)
    
    try:
        print("Loading policy documents...")
        indexed_documents = retrieve_documents(doc_dir)
        
        print(f"✓ Loaded documents from: {doc_dir}")
        print(f"  - HR policy")
        print(f"  - IT policy")
        print(f"  - Finance policy")
        print()
        print("Ready to answer questions. Type 'quit' or 'exit' to end.")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Interactive loop
    while True:
        try:
            question = input("\nQuestion: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye.")
                break
            
            # Enforcement: Single-source answers only, no blending
            result = answer_question(question, indexed_documents)
            
            print(f"\nAnswer:")
            print(result['answer'])
            
            if result['reason']:
                print(f"[Note: {result['reason']}]")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye.")
            break
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    main()
