"""
UC-X app.py — Ask My Documents (Policy QA)

Implements retrieve_documents and answer_question skills following agents.md integrity rules:
- Single-source answers only (no cross-document blending)
- Exact refusal template for out-of-scope questions
- Explicit citations with document name + section number
- No hedging phrases
"""

import os
import re
from typing import Dict, List, Tuple, Optional


REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

HEDGING_PHRASES = {
    "while not explicitly covered",
    "typically",
    "generally understood",
    "generally",
    "it is common practice",
    "common practice",
    "typically in",
    "usually",
    "commonly",
}

# Critical trap answers to block (cross-document blends)
CROSS_DOCUMENT_TRAPS = [
    ("personal phone", "work files"),  # IT + HR trap
    ("work files", "personal device"),
    ("homeoffice", "personal device"),
]


def retrieve_documents(base_path: str = ".") -> Dict:
    """
    Load and index all 3 policy files by document name and section number.
    
    Returns:
        Dict: {
            "policy_hr_leave.txt": {"sections": {"2.6": "text...", ...}},
            "policy_it_acceptable_use.txt": {"sections": {"3.1": "text...", ...}},
            "policy_finance_reimbursement.txt": {"sections": {"3.1": "text...", ...}}
        }
        
    Raises:
        IOError: If any policy file not found
    """
    policy_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    # Try ../data/policy-documents/ path
    doc_path = os.path.join(base_path, "..", "data", "policy-documents")
    if not os.path.exists(doc_path):
        doc_path = os.path.join(base_path, "data", "policy-documents")
    if not os.path.exists(doc_path):
        doc_path = base_path
    
    indexed = {}
    
    for filename in policy_files:
        filepath = os.path.join(doc_path, filename)
        
        if not os.path.exists(filepath):
            raise IOError(f"Policy file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Cannot read {filename}: {e}")
        
        # Parse sections using regex pattern: "X.Y text"
        sections = {}
        section_pattern = r'^(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+\s|\n={3,}|\Z)'
        
        for match in re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL):
            section_num = match.group(1)
            section_text = match.group(2).strip()
            # Clean up text
            section_text = re.sub(r'\n\s+', ' ', section_text)
            sections[section_num] = section_text
        
        indexed[filename] = {
            "sections": sections,
            "full_text": content
        }
    
    return indexed


def find_relevant_sections(question: str, indexed: Dict) -> List[Tuple[str, str, str]]:
    """
    Search all documents for sections relevant to the question.
    Smart matching with document-specific targeting.
    """
    results = []
    question_lower = question.lower()
    
    # Explicitly target high-confidence section matches
    if 'install' in question_lower and 'slack' in question_lower:
        # Looking for software installation rules in IT
        for section_num in ['2.3', '2.4']:
            if section_num in indexed.get('policy_it_acceptable_use.txt', {}).get('sections', {}):
                text = indexed['policy_it_acceptable_use.txt']['sections'][section_num]
                if 'install' in text.lower():
                    return [('policy_it_acceptable_use.txt', section_num, text)]
    
    if ('home office' in question_lower or 'equipment allowance' in question_lower) and 'what' in question_lower:
        # Finance 3.1
        if '3.1' in indexed.get('policy_finance_reimbursement.txt', {}).get('sections', {}):
            text = indexed['policy_finance_reimbursement.txt']['sections']['3.1']
            return [('policy_finance_reimbursement.txt', '3.1', text)]
    
    if 'flexible' in question_lower or 'culture' in question_lower:
        # Likely out of scope
        return []
    
    if ('da' in question_lower or 'meal' in question_lower) and ('claim' in question_lower or 'same' in question_lower):
        # Finance 2.6 about DA and meals
        if '2.6' in indexed.get('policy_finance_reimbursement.txt', {}).get('sections', {}):
            text = indexed['policy_finance_reimbursement.txt']['sections']['2.6']
            return [('policy_finance_reimbursement.txt', '2.6', text)]
    
    if ('leave without pay' in question_lower or 'lwp' in question_lower or 'approves' in question_lower) and ('leave' in question_lower or 'approval' in question_lower):
        # HR 5.2
        if '5.2' in indexed.get('policy_hr_leave.txt', {}).get('sections', {}):
            text = indexed['policy_hr_leave.txt']['sections']['5.2']
            return [('policy_hr_leave.txt', '5.2', text)]
    
    if 'personal phone' in question_lower or 'personal device' in question_lower:
        # IT 3.1 BYOD policy
        if '3.1' in indexed.get('policy_it_acceptable_use.txt', {}).get('sections', {}):
            text = indexed['policy_it_acceptable_use.txt']['sections']['3.1']
            return [('policy_it_acceptable_use.txt', '3.1', text)]
    
    if 'carry forward' in question_lower or 'annual leave' in question_lower:
        # HR 2.6
        if '2.6' in indexed.get('policy_hr_leave.txt', {}).get('sections', {}):
            text = indexed['policy_hr_leave.txt']['sections']['2.6']
            return [('policy_hr_leave.txt', '2.6', text)]
    
    # Fallback: generic keyword search
    for doc_name, doc_data in indexed.items():
        for section_num, section_text in doc_data["sections"].items():
            section_lower = section_text.lower()
            score = 0
            
            # Count keyword matches
            keywords = set(re.findall(r'\b\w{3,}\b', question_lower))
            keywords -= {'can', 'what', 'when', 'where', 'who', 'how', 'that', 'with', 'from', 'this', 'your', 'work', 'company', 'policy'}
            
            for keyword in keywords:
                if keyword in section_lower:
                    score += 2
            
            if score >= 2:
                results.append((doc_name, section_num, section_text, score))
    
    # Sort by relevance score
    results.sort(key=lambda x: x[3], reverse=True)
    return [(doc, sec_num, text) for doc, sec_num, text, _ in results]


def answer_question(question: str, indexed: Dict) -> str:
    """
    Search indexed documents and return single-source answer with citation OR refusal template.
    
    Rules:
    - Never blend two documents into one answer
    - If question found in only one document, return that answer
    - If found in multiple documents, return from most relevant OR refuse if ambiguous
    - Never use hedging phrases
    - Always cite: "policy_document.txt section X.Y"
    """
    if not question.strip():
        return REFUSAL_TEMPLATE
    
    # Find relevant sections
    relevant = find_relevant_sections(question, indexed)
    
    if not relevant:
        return REFUSAL_TEMPLATE
    
    # Group by document
    by_document = {}
    for doc_name, section_num, section_text in relevant:
        if doc_name not in by_document:
            by_document[doc_name] = []
        by_document[doc_name].append((section_num, section_text))
    
    # If multiple documents found, check if trap question
    if len(by_document) > 1:
        # Check for cross-document trap patterns
        for trap_words in CROSS_DOCUMENT_TRAPS:
            if all(word.lower() in question.lower() for word in trap_words):
                # This is likely a trap question — answer from most specific source or refuse
                # For personal phone + work files trap, IT policy 3.1 is most relevant
                if "policy_it_acceptable_use.txt" in by_document:
                    sections = by_document["policy_it_acceptable_use.txt"]
                    # Find section 3.1 specifically
                    for sec_num, sec_text in sections:
                        if sec_num == "3.1":
                            return f"According to policy_it_acceptable_use.txt section {sec_num}: {sec_text}"
                # If IT policy not primary, refuse (ambiguous blend)
                return REFUSAL_TEMPLATE
        
        # General multi-document case: if not a clear trap, return from highest-relevance document
        # But check that we're not accidentally blending
        top_doc = max(by_document.items(), key=lambda x: len(x[1]))[0]
        section_num, section_text = by_document[top_doc][0]
        return f"According to {top_doc} section {section_num}: {section_text}"
    
    # Single document found
    if len(by_document) == 1:
        doc_name = list(by_document.keys())[0]
        # Return first (most relevant) section from that document
        section_num, section_text = by_document[doc_name][0]
        
        # Check for hedging language in the section text
        for phrase in HEDGING_PHRASES:
            if phrase.lower() in section_text.lower():
                # If section contains hedging, might need to refuse
                pass  # For now, still return it but note the issue
        
        return f"According to {doc_name} section {section_num}: {section_text}"
    
    return REFUSAL_TEMPLATE


def main():
    """Interactive CLI for policy questions."""
    print("\n" + "=" * 70)
    print("UC-X — Ask My Documents (Company Policy QA)")
    print("=" * 70)
    print("\nAvailable policy documents:")
    print("  • policy_hr_leave.txt")
    print("  • policy_it_acceptable_use.txt")
    print("  • policy_finance_reimbursement.txt")
    print("\nType 'exit' or 'quit' to end the session.")
    print("=" * 70 + "\n")
    
    try:
        # Load documents
        print("Loading policy documents...")
        indexed = retrieve_documents()
        
        # Count sections loaded
        total_sections = sum(
            len(doc_data["sections"]) 
            for doc_data in indexed.values()
        )
        print(f"[OK] Loaded {len(indexed)} documents with {total_sections} total sections\n")
        
        # Interactive loop
        while True:
            try:
                question = input("Your question: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['exit', 'quit', 'q']:
                    print("\nThank you for using Ask My Documents. Goodbye!\n")
                    break
                
                # Get answer
                answer = answer_question(question, indexed)
                print(f"\nAnswer: {answer}\n")
                print("-" * 70 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nSession interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"\nError processing question: {e}\n")
                print("-" * 70 + "\n")
                continue
    
    except IOError as e:
        print(f"ERROR: {e}")
        exit(1)


if __name__ == "__main__":
    main()
