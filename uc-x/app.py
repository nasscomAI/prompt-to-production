import os
import re
from pathlib import Path
from typing import Dict, Tuple


# Hardcoded refusal template (from README)
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Banned hedging phrases that indicate hallucination
BANNED_PHRASES = [
    "while not explicitly covered",
    "while not explicitly",
    "typically",
    "generally understood",
    "it is common practice",
    "commonly understood",
    "generally",
    "may be",
]

# Document file names for reference
DOC_NAMES = {
    "hr": "policy_hr_leave.txt",
    "it": "policy_it_acceptable_use.txt",
    "finance": "policy_finance_reimbursement.txt",
}


def retrieve_documents(base_path: str = "../data/policy-documents") -> Dict:
    """
    Load all three policy documents and index them by section number.
    
    Args:
        base_path: Path to the policy-documents folder
        
    Returns:
        Indexed document structure: { 'HR': { '2.6': text, ... }, 'IT': { '3.1': text, ... }, ... }
    """
    documents = {}
    
    for doc_key, doc_filename in DOC_NAMES.items():
        file_path = os.path.join(base_path, doc_filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Policy document not found: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Error reading {doc_filename}: {str(e)}")
        
        # Index by section number (e.g., "2.6", "3.1", "5.2")
        sections = {}
        
        # Find all section patterns like "2.6", "3.1", "5.2", etc.
        # Split content on section headers (e.g., "2.6")
        section_pattern = r"^(\d+\.\d+)\s+"
        
        lines = content.split("\n")
        current_section = None
        current_text = []
        
        for line in lines:
            section_match = re.match(section_pattern, line)
            if section_match:
                # Save previous section if exists
                if current_section:
                    sections[current_section] = "\n".join(current_text).strip()
                
                # Start new section
                current_section = section_match.group(1)
                current_text = [line.replace(f"{current_section} ", "", 1)]
            elif current_section:
                current_text.append(line)
        
        # Save final section
        if current_section:
            sections[current_section] = "\n".join(current_text).strip()
        
        # Map to document type
        if doc_key == "hr":
            doc_type = "HR"
        elif doc_key == "it":
            doc_type = "IT"
        else:
            doc_type = "Finance"
        
        documents[doc_type] = sections
    
    return documents


def answer_question(question: str, documents: Dict) -> str:
    """
    Search indexed documents for single-source answers.
    
    Prevents cross-document blending, bans hedging language, and returns
    cited answers or refusal template.
    
    Args:
        question: User question (string)
        documents: Indexed document structure from retrieve_documents()
        
    Returns:
        Single answer with citation OR refusal template
    """
    
    if not question or not question.strip():
        return "Please ask a question about company policy."
    
    question_lower = question.lower()
    
    # Map keywords to specific document sections
    # Format: keyword -> (doc_type, section_number or None for multi-section search)
    keyword_to_section = {
        # HR questions
        "carry forward": ("HR", "2.6"),
        "carry forward": ("HR", "2.6"),
        "forfeited": ("HR", "2.6"),
        "without pay": ("HR", "5.2"),
        "lwp": ("HR", "5.2"),
        "leave without pay": ("HR", "5.2"),
        "approves leave": ("HR", "5.2"),
        "approval": ("HR", None),  # Multiple sections
        
        # IT questions
        "install slack": ("IT", "2.3"),
        "slack": ("IT", "2.3"),
        "personal phone": ("IT", "3.1"),
        "personal device": ("IT", "3.1"),
        "work files": ("IT", "3.1"),
        
        # Finance questions
        "equipment allowance": ("Finance", "3.1"),
        "home office": ("Finance", "3.1"),
        "da": ("Finance", "2.6"),
        "meal receipt": ("Finance", "2.6"),
        "claim": ("Finance", None),  # Multiple sections
    }
    
    # Find which document(s) might contain the answer
    matched_doc = None
    matched_section = None
    
    for keyword, (doc_type, section) in keyword_to_section.items():
        if keyword in question_lower:
            matched_doc = doc_type
            matched_section = section
            break
    
    # Fallback: basic keyword routing if no specific map match
    if matched_doc is None:
        hr_keywords = ["leave", "annual", "carry", "absent", "vacation", "approval", "lwp"]
        it_keywords = ["install", "phone", "device", "personal", "laptop", "slack", "email", "access", "file"]
        finance_keywords = ["allowance", "equipment", "receipt", "da", "meal", "claim", "reimburs"]
        
        doc_matches = []
        for keyword in hr_keywords:
            if keyword in question_lower:
                doc_matches.append("HR")
                break
        
        for keyword in it_keywords:
            if keyword in question_lower:
                doc_matches.append("IT")
                break
        
        for keyword in finance_keywords:
            if keyword in question_lower:
                doc_matches.append("Finance")
                break
        
        # Remove duplicates
        doc_matches = list(dict.fromkeys(doc_matches))
        
        # Cross-document blending detection
        if len(doc_matches) > 1:
            return ("This question may require information from multiple policy documents. "
                    "Please ask a more specific question focusing on one area "
                    "(HR leave, IT policy, or Finance reimbursement).")
        
        if len(doc_matches) == 0:
            return REFUSAL_TEMPLATE
        
        matched_doc = doc_matches[0]
    
    # If still no document, return refusal
    if matched_doc is None:
        return REFUSAL_TEMPLATE
    
    sections = documents.get(matched_doc, {})
    
    # If specific section is known, return it
    if matched_section:
        if matched_section in sections:
            section_text = sections[matched_section]
            
            # Check for hedging phrases
            for banned_phrase in BANNED_PHRASES:
                if banned_phrase in section_text.lower():
                    return (f"This answer requires clarification. "
                           "Please contact [relevant team] for guidance.")
            
            return f"{matched_doc} policy section {matched_section}: {section_text}"
    
    # Otherwise, search through all sections in the document for best match
    keywords = [w for w in question_lower.split() if len(w) > 2]
    
    best_match = None
    best_score = 0
    best_section = None
    
    for section_num in sorted(sections.keys()):
        section_text = sections[section_num].lower()
        
        # Score based on keyword matches
        score = sum(1 for keyword in keywords if keyword in section_text)
        
        if score > best_score:
            best_score = score
            best_match = sections[section_num]
            best_section = section_num
    
    # If no good match found, return refusal
    if best_score == 0:
        return REFUSAL_TEMPLATE
    
    # Check for hedging phrases in selected answer
    for banned_phrase in BANNED_PHRASES:
        if banned_phrase in best_match.lower():
            return (f"This answer requires clarification. "
                   "Please contact [relevant team] for guidance.")
    
    return f"{matched_doc} policy section {best_section}: {best_match}"


def format_welcome():
    """Display welcome message."""
    return """
╔════════════════════════════════════════════════════════════════╗
║           UC-X — Policy Document Question Answerer            ║
║                  Ask About Company Policies                   ║
╚════════════════════════════════════════════════════════════════╝

Available policies:
  - HR Leave Policy (policy_hr_leave.txt)
  - IT Acceptable Use Policy (policy_it_acceptable_use.txt)
  - Finance Reimbursement Policy (policy_finance_reimbursement.txt)

Type your question and press Enter.
Type 'quit' or 'exit' to end the session.
Type 'help' for example questions.

────────────────────────────────────────────────────────────────
"""


def format_help():
    """Display example questions."""
    return """
Example questions you can ask:

1. Can I carry forward unused annual leave?
2. Can I install Slack on my work laptop?
3. What is the home office equipment allowance?
4. Can I use my personal phone to access work files from home?
5. What is the company view on flexible working culture?
6. Can I claim DA and meal receipts on the same day?
7. Who approves leave without pay?

────────────────────────────────────────────────────────────────
"""


def main():
    """Interactive CLI for policy document Q&A."""
    
    print(format_welcome())
    
    # Load documents at startup
    try:
        print("Loading policy documents...")
        documents = retrieve_documents()
        print(f"✓ Successfully loaded 3 policy documents\n")
    except (FileNotFoundError, IOError) as e:
        print(f"Error: One or more policy documents are missing or unreadable.")
        print(f"The system requires all three policy files to operate.")
        print(f"Details: {str(e)}")
        return
    
    # Interactive loop
    while True:
        try:
            question = input("\n📋 Your question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ["quit", "exit", "q"]:
                print("\nThank you for using UC-X Policy Q&A. Goodbye!")
                break
            
            if question.lower() == "help":
                print(format_help())
                continue
            
            # Get answer
            answer = answer_question(question, documents)
            
            print(f"\n📝 Answer:\n{answer}")
            print("─" * 64)
        
        except KeyboardInterrupt:
            print("\n\nSession ended by user. Goodbye!")
            break
        except Exception as e:
            print(f"\nError processing question: {str(e)}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
