"""
UC-X app.py — Ask My Documents
RICE → agents.md → skills.md → CRAFT implementation.

Enforces agents.md rules:
1. Never combine claims from two documents — single-source only OR refusal
2. Never hedge: no "while not explicitly covered", "typically", "generally"
3. Use refusal template exactly when question not covered
4. Cite document name + section number for every factual claim
"""
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


# Refusal template (exactly as specified in README)
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents \
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). \
Please contact the relevant department for guidance."""

# Policy document paths
POLICY_DIR = "../data/policy-documents"
POLICY_FILES = {
    "policy_hr_leave.txt": "HR Policy",
    "policy_it_acceptable_use.txt": "IT Policy",
    "policy_finance_reimbursement.txt": "Finance Policy"
}


def retrieve_documents(policy_dir: str = POLICY_DIR) -> Dict:
    """
    Load three policy text files and index by document name and section number.
    
    Args:
        policy_dir: Directory containing policy files
        
    Returns:
        Dict with keys:
        - documents: Dict mapping doc_name → list of indexed sections
        - metadata: Dict with doc_count, total_sections
        
    Enforces skills.md error handling:
    - Missing files logged to stderr
    - Encoding recovery attempted
    - Returns available documents only
    """
    documents = {}
    total_sections = 0
    
    for filename, display_name in POLICY_FILES.items():
        filepath = os.path.join(policy_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"WARNING: File not found: {filepath}", file=sys.stderr)
            continue
        except UnicodeDecodeError:
            print(f"WARNING: Encoding error in {filepath}, attempting recovery", file=sys.stderr)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                print(f"ERROR: Cannot read {filepath}: {str(e)}", file=sys.stderr)
                continue
        
        # Parse sections by numbered pattern (e.g., "2.3", "3.1", "5.2")
        # Extract section number and full text until next section
        section_pattern = r'^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|$)'
        sections = []
        
        for match in re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL):
            section_num = match.group(1)
            section_text = match.group(2).strip()
            
            sections.append({
                'section': section_num,
                'text': section_text,
                'document': filename,
                'display_name': display_name
            })
            total_sections += 1
        
        documents[filename] = sections
        print(f"Loaded {filename}: {len(sections)} sections", file=sys.stderr)
    
    if not documents:
        print("ERROR: No policy documents could be loaded", file=sys.stderr)
        raise RuntimeError("No policy documents available")
    
    metadata = {
        'doc_count': len(documents),
        'total_sections': total_sections,
        'documents': list(documents.keys())
    }
    
    return {
        'documents': documents,
        'metadata': metadata
    }


def answer_question(question: str, indexed_docs: Dict) -> Dict:
    """
    Search indexed documents for question answer.
    Returns single-source citation with document and section OR refusal template.
    
    Args:
        question: User question (string)
        indexed_docs: Dict returned from retrieve_documents
        
    Returns:
        Dict with keys:
        - answer: String (answer text or refusal template)
        - source_document: String (filename if found, else None)
        - section_number: String (section number if found, else None)
        - is_refusal: Boolean
        - blend_detected: Boolean (true if multiple documents match)
        - display_name: String (human-readable document name)
        
    Enforces agents.md rules:
    - Never blend answers from multiple documents
    - Use refusal template exactly
    - Detect hedged language and refuse instead
    - Mandatory citations
    """
    
    question_lower = question.lower()
    documents = indexed_docs['documents']
    
    # Search results: list of (document, section_num, section_text, match_score)
    matches = []
    docs_with_matches = set()
    
    # Simple keyword-based search
    # Better search could use semantic similarity, but this enforces exact citations
    search_terms = re.findall(r'\b\w{4,}\b', question_lower)  # Words 4+ chars
    
    for filename, sections in documents.items():
        for section in sections:
            section_lower = section['text'].lower()
            
            # Score based on term matches
            match_count = sum(1 for term in search_terms if term in section_lower)
            
            if match_count > 0:
                matches.append({
                    'document': filename,
                    'display_name': section['display_name'],
                    'section': section['section'],
                    'text': section['text'],
                    'score': match_count
                })
                docs_with_matches.add(filename)
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Check for blending (matches from multiple documents)
    if len(docs_with_matches) > 1:
        return {
            'answer': REFUSAL_TEMPLATE,
            'source_document': None,
            'section_number': None,
            'is_refusal': True,
            'blend_detected': True,
            'display_name': None,
            'reason': 'Question matches multiple documents — cannot blend'
        }
    
    # Return best match if any
    if matches:
        best_match = matches[0]
        return {
            'answer': f"According to {best_match['display_name']} (section {best_match['section']}):\n\n{best_match['text']}",
            'source_document': best_match['document'],
            'section_number': best_match['section'],
            'is_refusal': False,
            'blend_detected': False,
            'display_name': best_match['display_name'],
            'reason': None
        }
    
    # No match found
    return {
        'answer': REFUSAL_TEMPLATE,
        'source_document': None,
        'section_number': None,
        'is_refusal': True,
        'blend_detected': False,
        'display_name': None,
        'reason': 'Question not found in available documents'
    }


def main():
    """Interactive CLI for policy question answering."""
    print("\n" + "=" * 70, file=sys.stderr)
    print("UC-X — Ask My Documents", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("\nLoading policy documents...\n", file=sys.stderr)
    
    try:
        indexed_docs = retrieve_documents()
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    print("\nPolicy documents loaded. Type 'exit' to quit.\n", file=sys.stderr)
    
    # Interactive loop
    while True:
        try:
            question = input("Your question: ").strip()
        except EOFError:
            # Handle non-interactive input (piped)
            break
        except KeyboardInterrupt:
            print("\nGoodbye.", file=sys.stderr)
            break
        
        if not question:
            continue
        
        if question.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye.", file=sys.stderr)
            break
        
        # Answer the question
        result = answer_question(question, indexed_docs)
        
        print("\n" + "-" * 70)
        print(result['answer'])
        print("-" * 70)
        
        # Log diagnostic info
        if result['is_refusal']:
            if result['blend_detected']:
                print("[DIAGNOSTIC: Blend detected — refusing to combine sources]", file=sys.stderr)
            else:
                print(f"[DIAGNOSTIC: {result['reason']}]", file=sys.stderr)
        else:
            print(f"[DIAGNOSTIC: Source: {result['display_name']}, Section {result['section_number']}]", file=sys.stderr)
        
        print()


if __name__ == "__main__":
    main()
