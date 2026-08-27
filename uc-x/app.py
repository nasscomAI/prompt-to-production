"""
UC-X app.py — Document Question-Answering Agent Implementation.
Implements agents.md (Document QA Agent) and skills.md (retrieve_documents, answer_question).
See README.md for run command and expected behaviour.
"""
import re
from pathlib import Path


# Refusal template - exact wording from README
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

HEDGING_PHRASES = [
    "while not explicitly",
    "typically",
    "generally",
    "generally understood",
    "it is common practice",
    "usually",
    "often",
    "likely",
    "probably"
]


def retrieve_documents(file_paths):
    """
    Skill: retrieve_documents
    Loads all 3 policy documents and indexes by document name and section number.
    
    Args:
        file_paths (list): List of file paths to policy documents
    
    Returns:
        dict: {"policy_name": {"section_number": section_text, ...}, ...}
        Example: {"policy_hr_leave.txt": {"2.6": "Max 5 days carry-forward...", ...}}
    
    Raises:
        FileNotFoundError: If file not found
        ValueError: If no numbered sections detected
    """
    indexed_docs = {}
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Policy file not found: {file_path}")
        
        # Extract document name from path
        doc_name = Path(file_path).name
        
        # Extract numbered sections (e.g., "2.6", "5.2", "3.1")
        section_pattern = r'^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|$)'
        matches = re.findall(section_pattern, content, re.MULTILINE | re.DOTALL)
        
        if not matches:
            raise ValueError(f"No numbered clauses detected in {doc_name}")
        
        # Store sections by document
        indexed_docs[doc_name] = {}
        for section_num, section_text in matches:
            indexed_docs[doc_name][section_num] = section_text.strip()
    
    return indexed_docs


def answer_question(question, indexed_docs):
    """
    Skill: answer_question
    Searches indexed documents for answer, returns single-source answer with citation OR refusal.
    
    Args:
        question (str): User's policy question
        indexed_docs (dict): Output from retrieve_documents
    
    Returns:
        dict: {
            "answer": string (answer text or REFUSAL_TEMPLATE),
            "source": "document_name + section_number" or "REFUSAL",
            "cited": boolean
        }
    """
    
    # Search all documents for matching content
    matches = []
    
    for doc_name, sections in indexed_docs.items():
        for section_num, section_text in sections.items():
            # Simple keyword matching (case-insensitive)
            question_lower = question.lower()
            section_lower = section_text.lower()
            
            # Check if key terms from question appear in section
            words = [w for w in question_lower.split() if len(w) > 3]
            match_count = sum(1 for word in words if word in section_lower)
            
            if match_count >= 1:  # At least one keyword match
                matches.append({
                    'doc': doc_name,
                    'section': section_num,
                    'text': section_text,
                    'relevance': match_count
                })
    
    # Sort by relevance
    matches.sort(key=lambda x: x['relevance'], reverse=True)
    
    if not matches:
        # Question not in documents - use refusal template
        return {
            "answer": REFUSAL_TEMPLATE,
            "source": "REFUSAL",
            "cited": False
        }
    
    # Check for multi-document matches (potential blending)
    unique_docs = set(m['doc'] for m in matches)
    if len(unique_docs) > 1:
        # Multiple documents mentioned - potential blending risk
        # Use only the highest relevance match (single source constraint)
        best_match = matches[0]
    else:
        best_match = matches[0]
    
    # Build answer with citation
    answer = f"{best_match['text']}\n\n[Source: {best_match['doc']} Section {best_match['section']}]"
    
    return {
        "answer": answer,
        "source": f"{best_match['doc']} Section {best_match['section']}",
        "cited": True
    }


def main():
    """
    Interactive CLI for policy Q&A.
    Loads documents on startup, accepts questions, returns cited answers or refusal.
    """
    
    # Policy document paths (relative to uc-x folder)
    policy_files = [
        '../data/policy-documents/policy_hr_leave.txt',
        '../data/policy-documents/policy_it_acceptable_use.txt',
        '../data/policy-documents/policy_finance_reimbursement.txt'
    ]
    
    try:
        # Skill 1: Load and index documents
        print("Loading policy documents...")
        indexed_docs = retrieve_documents(policy_files)
        
        print(f"✓ Loaded {len(indexed_docs)} documents")
        for doc_name, sections in indexed_docs.items():
            print(f"  - {doc_name}: {len(sections)} sections")
        
        print("\n" + "="*60)
        print("Policy Question-Answering System")
        print("="*60)
        print("Type your policy questions below. Type 'exit' to quit.\n")
        
        # Interactive loop
        while True:
            question = input("Your question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\nThank you for using the policy Q&A system.")
                break
            
            if not question:
                print("Please enter a question.\n")
                continue
            
            # Skill 2: Answer question
            result = answer_question(question, indexed_docs)
            
            print(f"\n{result['answer']}")
            print("-" * 60 + "\n")
    
    except (FileNotFoundError, ValueError) as e:
        print(f"✗ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
