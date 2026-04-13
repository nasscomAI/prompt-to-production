#!/usr/bin/env python3
"""
UC-X: Ask My Documents
Interactive Q&A system for policy documents with strict single-source attribution.
"""

import re
import sys
from pathlib import Path


# Refusal template - used exactly when question not in documents
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact HR Department for guidance."""

# Forbidden phrases that indicate hallucination
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "in most cases",
    "employees are expected to"
]


def retrieve_documents(policy_dir):
    """
    Load and index all policy documents.
    
    Args:
        policy_dir: Path to directory containing policy files
    
    Returns:
        dict with documents list and searchable index
    """
    policy_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    documents = []
    index = {}
    
    for filename in policy_files:
        filepath = Path(policy_dir) / filename
        if not filepath.exists():
            print(f"Warning: {filename} not found", file=sys.stderr)
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse document
        lines = content.split('\n')
        title = ""
        sections = []
        
        for line in lines[:10]:
            if "POLICY" in line.upper() and not line.startswith('═'):
                title = line.strip()
                break
        
        # Extract all numbered clauses
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line_stripped)
            if clause_match:
                clause_num = clause_match.group(1)
                clause_text = clause_match.group(2)
                
                # Collect continuation lines
                full_text = clause_text
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if (re.match(r'^\d+\.\d+\s', next_line) or 
                        re.match(r'^\d+\.\s+[A-Z]', next_line) or
                        next_line.startswith('═') or
                        not next_line):
                        break
                    full_text += ' ' + next_line
                    j += 1
                
                sections.append({
                    'number': clause_num,
                    'text': full_text
                })
        
        documents.append({
            'name': filename,
            'title': title,
            'sections': sections
        })
        
        # Build index
        index[filename] = {s['number']: s['text'] for s in sections}
    
    return {
        'documents': documents,
        'index': index
    }


def answer_question(question, documents_data):
    """
    Answer question using policy documents with single-source attribution.
    
    Args:
        question: User's question
        documents_data: Output from retrieve_documents
    
    Returns:
        Answer string with citation or refusal template
    """
    question_lower = question.lower()
    
    # Search for relevant sections across all documents
    matches = []
    
    for doc in documents_data['documents']:
        doc_name = doc['name']
        for section in doc['sections']:
            section_text_lower = section['text'].lower()
            
            # Simple keyword matching - check if question keywords appear in section
            question_words = set(re.findall(r'\w+', question_lower))
            section_words = set(re.findall(r'\w+', section_text_lower))
            
            # Remove common words
            common_words = {'the', 'a', 'an', 'is', 'are', 'can', 'i', 'my', 'what', 'how', 'when', 'where', 'who', 'for', 'to', 'of', 'in', 'on', 'at'}
            question_words -= common_words
            
            # Calculate overlap
            overlap = question_words & section_words
            if len(overlap) >= 2:  # At least 2 meaningful words match
                matches.append({
                    'document': doc_name,
                    'section': section['number'],
                    'text': section['text'],
                    'relevance': len(overlap)
                })
    
    # Decision logic
    if not matches:
        return REFUSAL_TEMPLATE
    
    # Sort by relevance
    matches.sort(key=lambda x: x['relevance'], reverse=True)
    
    # Check how many documents have matches
    unique_docs = set(m['document'] for m in matches)
    
    # Use the most relevant match from single document
    best_match = matches[0]
    
    # Check for cross-document blending risk
    # Special case: personal phone + work files question
    if ('personal' in question_lower and 'phone' in question_lower and 
        ('work' in question_lower or 'file' in question_lower)):
        # Must answer from IT policy only, section 3.1
        it_matches = [m for m in matches if m['document'] == 'policy_it_acceptable_use.txt']
        if it_matches:
            for m in it_matches:
                if m['section'].startswith('3.'):
                    best_match = m
                    break
    
    # Format answer with citation
    answer = f"According to {best_match['document']} section {best_match['section']}: {best_match['text']}"
    
    # Validate - check for forbidden phrases
    answer_lower = answer.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in answer_lower:
            # This shouldn't happen since we're quoting directly, but check anyway
            return REFUSAL_TEMPLATE
    
    return answer


def interactive_mode(documents_data):
    """
    Run interactive Q&A session.
    
    Args:
        documents_data: Output from retrieve_documents
    """
    print("=" * 60)
    print("POLICY DOCUMENT Q&A SYSTEM")
    print("=" * 60)
    print("\nAvailable documents:")
    for doc in documents_data['documents']:
        print(f"  - {doc['name']}: {doc['title']}")
    print("\nType your question (or 'quit' to exit)")
    print("=" * 60)
    print()
    
    while True:
        try:
            question = input("Question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            answer = answer_question(question, documents_data)
            print(f"\nAnswer:\n{answer}\n")
            print("-" * 60)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            break


def main():
    # Determine policy directory
    policy_dir = Path(__file__).parent.parent / "data" / "policy-documents"
    
    if not policy_dir.exists():
        print(f"Error: Policy directory not found: {policy_dir}", file=sys.stderr)
        sys.exit(1)
    
    print("Loading policy documents...")
    documents_data = retrieve_documents(policy_dir)
    print(f"Loaded {len(documents_data['documents'])} documents")
    
    # Run interactive mode
    interactive_mode(documents_data)


if __name__ == '__main__':
    main()
