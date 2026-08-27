"""
UC-X — Policy Q&A Chatbot
Answers questions about company policy using three documents.
Builds on RICE principles from agents.md and skills.md.
"""
import os
import re
from typing import Dict, List, Optional

# Exact refusal template
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Keywords that indicate refusal topics
REFUSAL_TOPICS = [
    "culture", "values", "mission", "vision", "strategy", "general",
    "typical", "standard practice", "usually", "commonly", "often",
    "not sure", "maybe", "possibly", "might be", "unclear"
]

# Document paths
DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]


def retrieve_documents(base_path: str) -> Dict[str, Dict[str, str]]:
    """
    Load all three policy documents and index by section number.
    """
    documents = {}
    
    for doc_name in DOCUMENTS:
        doc_path = os.path.join(base_path, doc_name)
        
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"Document not found: {doc_name}")
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            raise ValueError(f"Document is empty: {doc_name}")
        
        # Parse sections
        sections = {}
        current_section = None
        current_text = []
        
        for line in content.split('\n'):
            # Check for section header (e.g., "2.6 Employees may carry...")
            section_match = re.match(r'^(\d+\.\d+)\s+(.*)', line.strip())
            if section_match:
                # Save previous section
                if current_section:
                    sections[current_section] = ' '.join(current_text)
                
                current_section = section_match.group(1)
                current_text = [section_match.group(2)]
            elif current_section:
                current_text.append(line.strip())
        
        # Save last section
        if current_section:
            sections[current_section] = ' '.join(current_text)
        
        documents[doc_name] = sections
    
    return documents


def _find_relevant_section(documents: Dict, question: str) -> List[tuple]:
    """
    Find sections in all documents that are relevant to the question.
    Returns list of (doc_name, section_num, text) tuples.
    """
    question_lower = question.lower()
    relevant = []
    
    for doc_name, sections in documents.items():
        for section_num, text in sections.items():
            # Simple keyword matching
            text_lower = text.lower()
            question_words = set(question_lower.split())
            text_words = set(text_lower.split())
            
            # Check for word overlap
            common = question_words & text_words
            # Filter out common stopwords
            stopwords = {'the', 'a', 'an', 'is', 'are', 'can', 'i', 'my', 'to', 'for', 'on', 'in', 'at', 'do', 'does', 'what', 'how', 'when', 'where', 'why'}
            meaningful_common = common - stopwords
            
            if len(meaningful_common) >= 2:
                relevant.append((doc_name, section_num, text))
    
    return relevant


def _check_refusal(question: str) -> bool:
    """Check if question should trigger refusal."""
    question_lower = question.lower()
    
    # Check for topics not covered in policies
    for topic in REFUSAL_TOPICS:
        if topic in question_lower:
            # Check if there's relevant content in documents
            return True
    
    return False


def answer_question(question: str, documents: Dict) -> Dict:
    """
    Answer a question using the policy documents.
    """
    # Find relevant sections
    relevant = _find_relevant_section(documents, question)
    
    # Check for refusal
    if not relevant or _check_refusal(question):
        # But verify if there's actual relevant content
        if not relevant:
            return {
                'answer': REFUSAL_TEMPLATE,
                'source': 'REFUSAL',
                'section': None,
                'is_refusal': True
            }
    
    # Find the best match (most keyword overlap)
    best_match = None
    best_score = 0
    
    question_lower = question.lower()
    question_words = set(question_lower.split())
    stopwords = {'the', 'a', 'an', 'is', 'are', 'can', 'i', 'my', 'to', 'for', 'on', 'in', 'at', 'do', 'does', 'what', 'how', 'when', 'where', 'why'}
    meaningful_qwords = question_words - stopwords
    
    for doc_name, section_num, text in relevant:
        text_lower = text.lower()
        text_words = set(text_lower.split())
        
        # Calculate relevance score
        common = meaningful_qwords & text_words
        score = len(common)
        
        if score > best_score:
            best_score = score
            best_match = (doc_name, section_num, text)
    
    if best_match:
        doc_name, section_num, text = best_match
        
        # Build answer with citation
        answer = f"According to {doc_name} section {section_num}: {text[:200]}..."
        if len(text) > 200:
            answer += f" [truncated - see full policy for details]"
        
        return {
            'answer': answer,
            'source': doc_name,
            'section': section_num,
            'is_refusal': False
        }
    
    # No relevant content found
    return {
        'answer': REFUSAL_TEMPLATE,
        'source': 'REFUSAL',
        'section': None,
        'is_refusal': True
    }


def main():
    print("UC-X Policy Q&A Chatbot")
    print("=" * 50)
    print("Available policies: HR Leave, IT Acceptable Use, Finance Reimbursement")
    print("Type 'quit' or 'exit' to end.\n")
    
    # Load documents
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(script_dir), 'data', 'policy-documents')
    
    try:
        documents = retrieve_documents(data_path)
        print(f"Loaded {len(documents)} policy documents.\n")
    except Exception as e:
        print(f"Error loading documents: {e}")
        return
    
    # Interactive loop
    while True:
        try:
            question = input("You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            result = answer_question(question, documents)
            
            print(f"\nBot: {result['answer']}")
            
            if result['is_refusal']:
                print("(Refusal template used - question not covered in policies)")
            
            print()
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
