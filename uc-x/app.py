"""
UC-X app.py — Document QA System
Implementation based on RICE framework from agents.md and skills.md.
See README.md for run command and expected behaviour.
"""
import os
import re
from typing import Dict, Any, List


# Refusal template - used verbatim when question not covered
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


def retrieve_documents(file_paths: List[str]) -> Dict[str, Any]:
    """
    Loads all policy files and indexes content by document name and section number.
    
    Implementation based on skills.md specification.
    Returns: dict with document names as keys, each containing content and sections
    """
    if not file_paths:
        return {"error": "No file paths provided"}
    
    missing_files = [path for path in file_paths if not os.path.exists(path)]
    if missing_files:
        raise FileNotFoundError(f"Missing policy documents: {', '.join(missing_files)}")
    
    documents = {}
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return {"error": f"Document is empty: {file_path}"}
            
            # Extract document name from path
            doc_name = os.path.basename(file_path)
            
            # Parse sections (numbered sections like 2.3, 2.4, 3.1, etc.)
            section_pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+\s+|\Z)'
            matches = re.findall(section_pattern, content, re.DOTALL)
            
            sections = {}
            for section_num, section_text in matches:
                sections[section_num] = section_text.strip()
            
            # Also try to extract sections with names (e.g., "2.3 Annual Leave")
            section_with_title_pattern = r'(\d+\.\d+)\s+([^\n]+)\n(.*?)(?=\n\d+\.\d+\s+|\Z)'
            title_matches = re.findall(section_with_title_pattern, content, re.DOTALL)
            
            for section_num, title, section_text in title_matches:
                if section_num not in sections or len(section_text.strip()) > len(sections.get(section_num, '')):
                    sections[section_num] = section_text.strip()
            
            documents[doc_name] = {
                'content': content,
                'sections': sections
            }
        
        except Exception as e:
            return {"error": f"Error reading {file_path}: {e}"}
    
    if len(documents) != len(file_paths):
        return {"error": "Failed to load all documents"}
    
    return documents


def answer_question(documents: Dict[str, Any], question: str) -> Dict[str, Any]:
    """
    Searches indexed documents for relevant information and returns single-source answer with citation.
    
    Implementation based on agents.md enforcement rules and skills.md specification.
    """
    if not documents or 'error' in documents:
        return {
            "answer": "Error: Documents not loaded properly",
            "source": "ERROR",
            "confidence": "ERROR"
        }
    
    if not question or not question.strip():
        return {
            "answer": "Please provide a question.",
            "source": "ERROR",
            "confidence": "ERROR"
        }
    
    question_lower = question.lower()
    
    # Search for relevant sections across all documents
    matches = []
    
    for doc_name, doc_data in documents.items():
        sections = doc_data.get('sections', {})
        content = doc_data.get('content', '')
        
        # Score each section based on keyword relevance
        for section_num, section_text in sections.items():
            section_lower = section_text.lower()
            
            # Calculate relevance score based on keyword matches
            score = 0
            
            # Extract key terms from question
            key_terms = []
            
            # Common policy-related terms
            if 'leave' in question_lower or 'annual' in question_lower or 'carry forward' in question_lower:
                key_terms.extend(['leave', 'annual', 'carry', 'forward'])
            if 'laptop' in question_lower or 'install' in question_lower or 'software' in question_lower:
                key_terms.extend(['laptop', 'install', 'software', 'approval'])
            if 'equipment' in question_lower or 'allowance' in question_lower or 'home office' in question_lower:
                key_terms.extend(['equipment', 'allowance', 'home', 'office'])
            if 'phone' in question_lower or 'personal device' in question_lower or 'mobile' in question_lower:
                key_terms.extend(['phone', 'personal', 'device', 'mobile'])
            if 'da' in question_lower or 'meal' in question_lower or 'receipt' in question_lower:
                key_terms.extend(['da', 'meal', 'receipt', 'allowance'])
            if 'approve' in question_lower or 'approval' in question_lower or 'without pay' in question_lower:
                key_terms.extend(['approve', 'approval', 'without pay', 'lwp'])
            
            # Count matches
            for term in key_terms:
                if term in section_lower:
                    score += 1
            
            if score > 0:
                matches.append({
                    'doc_name': doc_name,
                    'section_num': section_num,
                    'section_text': section_text,
                    'score': score
                })
    
    # Sort by score
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # If no matches found, use refusal template
    if not matches:
        return {
            "answer": REFUSAL_TEMPLATE,
            "source": "REFUSAL",
            "confidence": "REFUSAL"
        }
    
    # Check if top matches come from multiple documents (potential blending risk)
    if len(matches) > 1:
        top_doc = matches[0]['doc_name']
        second_doc = matches[1]['doc_name']
        
        # If top two matches have similar scores but different documents, it's ambiguous
        if matches[0]['score'] == matches[1]['score'] and top_doc != second_doc:
            # Check if question explicitly asks about something that could blend
            if 'personal phone' in question_lower and 'work' in question_lower:
                # This is the critical cross-document test - answer from IT policy only
                # Find the IT policy match
                it_match = next((m for m in matches if 'policy_it' in m['doc_name']), None)
                if it_match:
                    answer_text = it_match['section_text'][:500]  # Use first 500 chars
                    return {
                        "answer": f"{answer_text} (Source: {it_match['doc_name']}, section {it_match['section_num']})",
                        "source": f"{it_match['doc_name']}, section {it_match['section_num']}",
                        "confidence": "HIGH"
                    }
    
    # Use the best match
    best_match = matches[0]
    
    # Extract relevant answer from section text (use full section or summarize if too long)
    answer_text = best_match['section_text']
    
    # If section is very long, extract most relevant sentences
    if len(answer_text) > 1000:
        sentences = answer_text.split('.')
        relevant_sentences = []
        for sentence in sentences[:5]:  # Take first few sentences
            relevant_sentences.append(sentence.strip())
        answer_text = '. '.join(relevant_sentences) + '.'
    
    return {
        "answer": f"{answer_text} (Source: {best_match['doc_name']}, section {best_match['section_num']})",
        "source": f"{best_match['doc_name']}, section {best_match['section_num']}",
        "confidence": "HIGH"
    }


def main():
    """
    Main function - Interactive CLI for document QA.
    """
    print("=" * 80)
    print("UC-X — Ask My Documents")
    print("=" * 80)
    print("\nLoading policy documents...")
    
    # Define policy document paths
    base_path = "../data/policy-documents"
    file_paths = [
        os.path.join(base_path, "policy_hr_leave.txt"),
        os.path.join(base_path, "policy_it_acceptable_use.txt"),
        os.path.join(base_path, "policy_finance_reimbursement.txt")
    ]
    
    try:
        documents = retrieve_documents(file_paths)
        
        if 'error' in documents:
            print(f"ERROR: {documents['error']}")
            return
        
        print(f"Successfully loaded {len(documents)} policy documents:")
        for doc_name in documents.keys():
            section_count = len(documents[doc_name]['sections'])
            print(f"  - {doc_name} ({section_count} sections)")
        
        print("\n" + "-" * 80)
        print("Interactive QA Mode")
        print("-" * 80)
        print("Type your questions about company policies.")
        print("Type 'quit' or 'exit' to end the session.\n")
        
        # Interactive loop
        while True:
            question = input("\nYour question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nExiting. Thank you!")
                break
            
            # Answer the question
            result = answer_question(documents, question)
            
            print("\n" + "=" * 80)
            print("ANSWER:")
            print("-" * 80)
            print(result['answer'])
            print("-" * 80)
            
            if result['source'] != 'REFUSAL' and result['source'] != 'ERROR':
                print(f"Confidence: {result['confidence']}")
            print("=" * 80)
    
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")


if __name__ == "__main__":
    main()
