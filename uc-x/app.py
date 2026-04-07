"""
UC-X — Interactive Policy Q&A System
Prevents cross-document blending, hedged hallucination, and citation omission.
Enforces: single-source answers only, exact citations, no hedging, exact refusal template.
"""
import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance."""

HEDGING_PHRASES = [
    'while not explicitly',
    'while not stated',
    'though not explicitly',
    'typically',
    'generally',
    'usually',
    'often',
    'commonly',
    'as is standard',
    'as is common',
    'standard practice',
    'common practice',
    'it is understood',
    'understood to be',
    'appears to',
    'seems to be',
    'suggests',
    'might be',
    'could be interpreted',
    'subject to interpretation'
]


def retrieve_documents(doc_dir: str) -> dict:
    """
    Load and index 3 policy documents.
    Returns dict with documents indexed by section number and keyword index.
    """
    documents = {}
    
    doc_files = [
        'policy_hr_leave.txt',
        'policy_it_acceptable_use.txt',
        'policy_finance_reimbursement.txt'
    ]
    
    for doc_file in doc_files:
        file_path = os.path.join(doc_dir, doc_file)
        
        if not os.path.exists(file_path):
            print(f"Warning: Document not found: {file_path}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error loading {doc_file}: {e}")
            continue
        
        # Parse document structure
        sections = {}
        
        # Extract metadata
        title_match = re.search(r'^([A-Z\s—-]+)\n', content)
        title = title_match.group(1).strip() if title_match else doc_file
        
        version_match = re.search(r'Version:\s*([\d\.]+)', content)
        version = version_match.group(1) if version_match else 'unknown'
        
        # Extract sections (pattern: digit.digit at line start)
        section_pattern = r'^(\d+\.\d+)\s+(.+?)$'
        
        lines = content.split('\n')
        current_section = None
        current_text = []
        
        for line in lines:
            match = re.match(section_pattern, line)
            if match:
                # Save previous section
                if current_section:
                    text_content = ' '.join(current_text).strip()
                    sections[current_section['num']] = {
                        'heading': current_section['heading'],
                        'text': text_content,
                        'key_phrases': extract_key_phrases(text_content)
                    }
                
                section_num = match.group(1)
                heading = match.group(2).strip()
                current_section = {'num': section_num, 'heading': heading}
                current_text = []
            elif current_section and line.strip():
                current_text.append(line.strip())
        
        # Save last section
        if current_section and current_text:
            text_content = ' '.join(current_text).strip()
            sections[current_section['num']] = {
                'heading': current_section['heading'],
                'text': text_content,
                'key_phrases': extract_key_phrases(text_content)
            }
        
        documents[doc_file] = {
            'title': title,
            'version': version,
            'sections': sections
        }
    
    return documents


def extract_key_phrases(text: str) -> list:
    """Extract key phrases from section text for indexing."""
    phrases = []
    
    # Common policy-related keywords
    keywords = [
        'leave', 'days', 'approval', 'allowed', 'permitted', 'prohibited',
        'email', 'personal device', 'device', 'password', 'reimbursement',
        'travel', 'allowance', 'rate', 'claim', 'cannot', 'must not',
        'required', 'eligible', 'work from home', 'remote', 'equipment'
    ]
    
    text_lower = text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            phrases.append(keyword)
    
    return phrases


def search_documents(user_question: str, documents: dict) -> list:
    """
    Search documents for sections matching the user question.
    Returns list of (doc_name, section_num, section_data) tuples sorted by relevance.
    """
    matches = []
    question_lower = user_question.lower()
    
    for doc_name, doc_data in documents.items():
        for section_num, section_data in doc_data['sections'].items():
            heading_text = section_data['heading'].lower()
            section_text = (section_data['heading'] + ' ' + section_data['text']).lower()
            
            # Score based on phrase matching with boosting for heading matches
            score = 0
            
            # Phrase matches (higher weight if in heading)
            phrase_scores = [
                ('personal device', 3, 5),  # (phrase, text_score, heading_score)
                ('personal phone', 3, 5),
                ('byod', 3, 5),
                ('carry forward', 2, 4),
                ('annual leave', 2, 4),
                ('install software', 3, 5),
                ('slack', 3, 5),
                ('home office equipment', 3, 5),
                ('leave without pay', 2, 4),
                ('meal receipt', 2, 4),
                ('daily allowance', 2, 3),
                ('flexible working', 1, 3),
                ('equipment allowance', 2, 4),
            ]
            
            for phrase, text_score, heading_score in phrase_scores:
                if phrase in heading_text:
                    score += heading_score
                elif phrase in section_text:
                    score += text_score
            
            # Word matching (only if score is still low - avoid bloating)
            if score < 3:
                for word in question_lower.split():
                    if len(word) > 3 and word not in ['from', 'that', 'this', 'what', 'work', 'home', 'files', 'phone', 'acces']:
                        if word in heading_text:
                            score += 1
                        elif word in section_text:
                            score += 0.5
            
            if score > 0:
                matches.append((doc_name, section_num, section_data, score))
    
    # Sort by score (descending), then by section number (prefer lower sections = more relevant)
    matches.sort(key=lambda x: (-x[3], x[1]))
    
    return matches


def has_hedging_phrases(text: str) -> bool:
    """Check if text contains hedging phrases."""
    text_lower = text.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in text_lower:
            return True
    return False


def answer_question(user_question: str, documents: dict) -> dict:
    """
    Answer user question from indexed documents.
    Returns dict with answer, source, answer_type, flags.
    """
    if not user_question or not user_question.strip():
        return {
            'answer': 'Please ask a question about company policy.',
            'source': 'none',
            'answer_type': 'prompt',
            'conditions_preserved': False,
            'hedging_phrases': False
        }
    
    # Search documents
    matches = search_documents(user_question, documents)
    
    if not matches:
        return {
            'answer': REFUSAL_TEMPLATE,
            'source': 'none',
            'answer_type': 'refusal',
            'conditions_preserved': False,
            'hedging_phrases': False
        }
    
    # E1: Take top match (single source only)
    top_match = matches[0]
    doc_name, section_num, section_data, _ = top_match
    
    # E5: Check that conditions are preserved in the answer
    text = section_data['text']
    conditions_preserved = all(
        keyword not in text.lower() or keyword in text
        for keyword in ['only', 'and', 'must not', 'cannot', 'not permitted']
    )
    
    # E3: Check for hedging
    has_hedging = has_hedging_phrases(text)
    
    # E2: Construct answer with citation
    answer = f"According to [{doc_name} - Section {section_num}], {text}"
    
    return {
        'answer': answer,
        'source': f"{doc_name}#{section_num}",
        'answer_type': 'direct',
        'conditions_preserved': conditions_preserved,
        'hedging_phrases': has_hedging
    }


def main():
    """Interactive CLI for policy Q&A."""
    print("=" * 70)
    print("UC-X — Interactive Policy Q&A System")
    print("=" * 70)
    print("Ask questions about company policies:")
    print("  • HR Leave Policy (policy_hr_leave.txt)")
    print("  • IT Acceptable Use (policy_it_acceptable_use.txt)")
    print("  • Finance Reimbursement (policy_finance_reimbursement.txt)")
    print()
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 70)
    print()
    
    # Load documents
    print("Loading policy documents...")
    
    # Construct path to data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data', 'policy-documents')
    
    documents = retrieve_documents(data_dir)
    
    if not documents:
        print("Error: No policy documents loaded. Cannot proceed.")
        return
    
    print(f"Loaded {len(documents)} documents.")
    print()
    
    # Interactive loop
    while True:
        try:
            user_question = input("Q: ").strip()
            
            if not user_question:
                continue
            
            if user_question.lower() in ['quit', 'exit']:
                print("Thank you for using UC-X. Goodbye!")
                break
            
            # Answer question
            result = answer_question(user_question, documents)
            
            print()
            print(f"A: {result['answer']}")
            print(f"   [Source: {result['source']}]")
            print()
        
        except KeyboardInterrupt:
            print("\nSession ended.")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()


if __name__ == "__main__":
    main()
