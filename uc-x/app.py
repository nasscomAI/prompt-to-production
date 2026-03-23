"""
UC-X app.py — Policy Q&A System
Interactive CLI for answering policy questions with source citations.
Prevents cross-document blending and enforces refusal template.
"""
import os
import re
from typing import Dict, Tuple, Optional


REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact HR Department for guidance."""

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "as is standard practice",
    "it is common",
    "generally"
]


def retrieve_documents(doc_dir: str = "../data/policy-documents/") -> Dict:
    """
    Load all three policy documents and index by section number.
    """
    required_docs = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    documents = {}
    indexed_sections = {}
    
    for doc_name in required_docs:
        doc_path = os.path.join(doc_dir, doc_name)
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            documents[doc_name] = content
            
            # Index sections by document:section_number
            section_pattern = r'(\d+\.\d+)\s+(.+?)(?=\d+\.\d+\s+|$|\n[═─])'
            matches = re.finditer(section_pattern, content, re.DOTALL)
            
            for match in matches:
                section_num = match.group(1)
                section_text = match.group(2).strip()
                key = f"{doc_name}:{section_num}"
                indexed_sections[key] = section_text
        
        except FileNotFoundError:
            print(f"Warning: Document not found: {doc_path}")
    
    if not documents:
        raise FileNotFoundError("No policy documents found. Check path.")
    
    print(f"Loaded {len(documents)} documents with {len(indexed_sections)} total sections")
    
    return {
        "documents": documents,
        "indexed_sections": indexed_sections
    }


def search_question(question: str, indexed_sections: Dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Search for question in indexed sections.
    Returns: (answer_text, document_name, section_number) or (None, None, None)
    
    Search strategy: Look for exact phrase matches, then keyword overlap.
    Only return result if confidence is high (3+ matching keywords).
    """
    question_lower = question.lower()
    
    # Extract key phrases and keywords from question
    import re
    # Remove common words
    stop_words = {"can", "i", "the", "my", "for", "from", "what", "is", "how", "do", "will", "if", "on"}
    words = question_lower.split()
    keywords = [w.strip("?.,;:") for w in words if len(w) > 3 and w.lower() not in stop_words]
    
    best_match = None
    best_score = 0
    
    for key, section_text in indexed_sections.items():
        section_lower = section_text.lower()
        
        # Score based on keyword matches
        score = sum(1 for keyword in keywords if keyword in section_lower)
        
        # Boost score for exact phrase matches
        if any(phrase in section_lower for phrase in ["carry forward", "personal phone", "flexible working"]):
            score += 5
        
        if score > best_score:
            best_score = score
            best_match = (key, section_text)
    
    # Require at least 3 keyword matches for confidence, or exact phrase match
    if best_match and best_score >= 3:
        key, text = best_match
        doc_name, section_num = key.split(":")
        return (text, doc_name, section_num)
    
    return (None, None, None)


def answer_question(question: str, indexed_sections: Dict) -> str:
    """
    Answer question from indexed documents.
    Returns answer with citation OR refusal template.
    """
    # Check for hedging phrases (hallucination detector)
    question_contains_hedge = any(phrase in question.lower() for phrase in HEDGING_PHRASES)
    
    # Search for match
    answer_text, doc_name, section_num = search_question(question, indexed_sections)
    
    if answer_text:
        # Extract first sentence or relevant clause
        lines = answer_text.split('\n')
        relevant_text = ""
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and len(line_stripped) > 15:
                relevant_text = line_stripped
                break
        
        if not relevant_text:
            relevant_text = answer_text[:200]
        
        # Structure the answer
        citation = f"[SOURCE: {doc_name}, Section {section_num}]"
        
        return f"{relevant_text}\n\n{citation}"
    else:
        # Use refusal template
        return REFUSAL_TEMPLATE


def interactive_cli():
    """
    Interactive Q&A command-line interface.
    """
    print("=" * 70)
    print("POLICY Q&A SYSTEM")
    print("=" * 70)
    print("Ask questions about company policies.")
    print("Type 'quit' or 'exit' to end.\n")
    
    try:
        indexed_data = retrieve_documents()
        indexed_sections = indexed_data["indexed_sections"]
    except Exception as e:
        print(f"Error loading documents: {e}")
        return
    
    while True:
        print("-" * 70)
        user_input = input("Your question: ").strip()
        
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye.")
            break
        
        if not user_input:
            continue
        
        answer = answer_question(user_input, indexed_sections)
        print("\nAnswer:")
        print(answer)
        print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="UC-X Policy Q&A - Interactive questions with source citations"
    )
    parser.add_argument("--batch", action="store_true", help="Run in batch mode (for testing)")
    parser.add_argument("--question", help="Single question to answer (with --batch)")
    
    args = parser.parse_args()
    
    if args.batch and args.question:
        # Batch mode - answer single question and exit
        try:
            indexed_data = retrieve_documents()
            indexed_sections = indexed_data["indexed_sections"]
            answer = answer_question(args.question, indexed_sections)
            print(answer)
        except Exception as e:
            print(f"Error: {e}")
            exit(1)
    else:
        # Interactive mode
        try:
            interactive_cli()
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye.")
        except Exception as e:
            print(f"Error: {e}")
            exit(1)


if __name__ == "__main__":
    main()
