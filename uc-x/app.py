"""
UC-X — Ask My Documents
Policy Question-Answering System with Strict Single-Source Enforcement
"""

import os
import re
from pathlib import Path


# Refusal template - exact wording required by enforcement rules
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """
    Skill: retrieve_documents
    Loads all 3 policy files and indexes them by document name and section number.
    
    Returns:
        dict: Indexed document structure with document name as key, containing sections
        str: Error message if any file cannot be loaded
    """
    policy_dir = Path(__file__).parent.parent / "data" / "policy-documents"
    policy_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    indexed_docs = {}
    
    for filename in policy_files:
        filepath = policy_dir / filename
        
        # Error handling: check if file exists and is readable
        if not filepath.exists():
            return None, f"Error: Policy file '{filename}' not found at {filepath}"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return None, f"Error: Could not read policy file '{filename}': {str(e)}"
        
        # Parse sections using section number pattern (e.g., "1.1", "2.3")
        sections = {}
        section_pattern = r'^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|\Z)'
        
        matches = list(re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL))
        
        if not matches:
            # Error handling: file lacks section numbers
            indexed_docs[filename] = {
                "warning": "File lacks section numbers, indexed as full document",
                "full_content": content
            }
        else:
            for match in matches:
                section_num = match.group(1)
                section_content = match.group(2).strip()
                sections[section_num] = section_content
            
            indexed_docs[filename] = {
                "sections": sections,
                "full_content": content
            }
    
    return indexed_docs, None


def answer_question(question, indexed_docs):
    """
    Skill: answer_question
    Searches indexed documents and returns a single-source answer with citation
    OR the refusal template if the question is not covered.
    
    Args:
        question (str): User question about company policy
        indexed_docs (dict): Indexed documents from retrieve_documents
    
    Returns:
        str: Answer with citation OR refusal template
    """
    # Error handling: check for empty or non-policy questions
    if not question or len(question.strip()) < 3:
        return REFUSAL_TEMPLATE
    
    question_lower = question.lower()
    
    # Track matches across documents to detect cross-document scenarios
    matches_by_doc = {}
    
    for doc_name, doc_data in indexed_docs.items():
        if "sections" not in doc_data:
            continue
        
        doc_matches = []
        sections = doc_data["sections"]
        
        for section_num, section_content in sections.items():
            section_lower = section_content.lower()
            
            # Simple keyword matching - check if question keywords appear in section
            question_keywords = set(re.findall(r'\b\w+\b', question_lower))
            # Remove common words
            stop_words = {'can', 'i', 'the', 'a', 'an', 'is', 'are', 'what', 'when', 'how', 'do', 'does', 
                         'my', 'for', 'to', 'from', 'on', 'in', 'at', 'of', 'and', 'or'}
            question_keywords = question_keywords - stop_words
            
            if len(question_keywords) == 0:
                continue
            
            # Count keyword matches
            match_count = sum(1 for kw in question_keywords if kw in section_lower)
            
            if match_count >= 2:  # Require at least 2 keyword matches
                doc_matches.append({
                    'section': section_num,
                    'content': section_content,
                    'match_count': match_count
                })
        
        if doc_matches:
            # Sort by match count
            doc_matches.sort(key=lambda x: x['match_count'], reverse=True)
            matches_by_doc[doc_name] = doc_matches
    
    # Enforcement: If question matches content in multiple documents, answer from most specific single source only
    if len(matches_by_doc) > 1:
        # Check if this is a cross-document blending scenario
        # For ambiguous cases, return refusal template
        best_doc = max(matches_by_doc.items(), key=lambda x: x[1][0]['match_count'])
        doc_name = best_doc[0]
        best_match = best_doc[1][0]
        
        # If match counts are similar across documents, it's ambiguous - refuse
        match_counts = [matches[0]['match_count'] for matches in matches_by_doc.values()]
        if max(match_counts) - min(match_counts) <= 1:
            return REFUSAL_TEMPLATE
        
        # Otherwise, answer from the single best source
        answer = f"{best_match['content']}\n\n[{doc_name}, section {best_match['section']}]"
        return answer
    
    elif len(matches_by_doc) == 1:
        # Single document match - safe to answer
        doc_name = list(matches_by_doc.keys())[0]
        best_match = matches_by_doc[doc_name][0]
        answer = f"{best_match['content']}\n\n[{doc_name}, section {best_match['section']}]"
        return answer
    
    else:
        # No matches found - use refusal template
        return REFUSAL_TEMPLATE


def main():
    """
    Interactive CLI for policy question-answering system.
    """
    print("=" * 70)
    print("UC-X — Ask My Documents")
    print("Company Policy Question-Answering System")
    print("=" * 70)
    print()
    
    # Load and index documents
    print("Loading policy documents...")
    indexed_docs, error = retrieve_documents()
    
    if error:
        print(f"\n{error}")
        print("Cannot proceed without all policy documents.")
        return
    
    print(f"✓ Loaded {len(indexed_docs)} policy documents")
    for doc_name in indexed_docs.keys():
        if "sections" in indexed_docs[doc_name]:
            section_count = len(indexed_docs[doc_name]["sections"])
            print(f"  - {doc_name}: {section_count} sections indexed")
        else:
            print(f"  - {doc_name}: {indexed_docs[doc_name].get('warning', 'loaded')}")
    
    print()
    print("=" * 70)
    print("Ask questions about company policies.")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 70)
    print()
    
    # Interactive question loop
    while True:
        try:
            question = input("Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using the policy Q&A system.")
                break
            
            if not question:
                continue
            
            # Get answer using the answer_question skill
            answer = answer_question(question, indexed_docs)
            
            print()
            print("Answer:")
            print("-" * 70)
            print(answer)
            print("-" * 70)
            print()
        
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye.")
            break
        except Exception as e:
            print(f"\nError processing question: {str(e)}")
            print()


if __name__ == "__main__":
    main()
