"""
UC-X app.py — Policy Document Q&A with No Cross-Document Blending
Implements RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Refusal template - exact wording required
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance."""


def retrieve_documents(policy_dir: str) -> Optional[Dict]:
    """
    Skill: retrieve_documents
    Loads all three policy documents and indexes by document name and section.
    
    Args:
        policy_dir: Directory path containing policy documents
        
    Returns:
        Dictionary with indexed content by document and section
    """
    policy_files = [
        'policy_hr_leave.txt',
        'policy_it_acceptable_use.txt',
        'policy_finance_reimbursement.txt'
    ]
    
    dir_path = Path(policy_dir)
    if not dir_path.exists():
        print(f"ERROR: Directory not found: {policy_dir}", file=sys.stderr)
        return None
        
    documents = {}
    metadata = {}
    
    for filename in policy_files:
        file_path = dir_path / filename
        if not file_path.exists():
            print(f"ERROR: Required policy file not found: {filename}", file=sys.stderr)
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract metadata
            doc_metadata = {}
            lines = content.split('\n')
            for line in lines[:10]:
                if 'Document Reference:' in line:
                    doc_metadata['reference'] = line.split(':', 1)[1].strip()
                if 'Version:' in line:
                    version_part = line.split('Version:', 1)[1]
                    if '|' in version_part:
                        doc_metadata['version'] = version_part.split('|')[0].strip()
                        if 'Effective:' in version_part:
                            doc_metadata['effective'] = version_part.split('Effective:', 1)[1].strip()
                            
            metadata[filename] = doc_metadata
            
            # Parse sections (X.Y format)
            sections = {}
            section_pattern = r'^(\d+\.\d+)\s+(.+?)$'
            
            current_section = None
            current_text = []
            
            for line in lines:
                match = re.match(section_pattern, line)
                if match:
                    # Save previous section
                    if current_section:
                        text = ' '.join(current_text).strip()
                        text = re.sub(r'\s+', ' ', text)
                        sections[current_section] = text
                    # Start new section
                    current_section = match.group(1)
                    current_text = [match.group(2)]
                elif current_section and line.strip() and not re.match(r'^═+', line) and not re.match(r'^\d+\.\s+[A-Z]', line):
                    current_text.append(line.strip())
                    
            # Save last section
            if current_section:
                text = ' '.join(current_text).strip()
                text = re.sub(r'\s+', ' ', text)
                sections[current_section] = text
                
            if not sections:
                print(f"ERROR: No valid sections found in {filename}", file=sys.stderr)
                return None
                
            documents[filename] = sections
            
        except Exception as e:
            print(f"ERROR: Failed to load {filename}: {str(e)}", file=sys.stderr)
            return None
            
    return {
        'documents': documents,
        'metadata': metadata
    }


def answer_question(question: str, doc_data: Dict, refusal_template: str) -> Dict:
    """
    Skill: answer_question
    Searches documents and returns single-source answer with citation OR refusal.
    
    Args:
        question: User's question
        doc_data: Indexed documents from retrieve_documents
        refusal_template: Exact refusal template to use
        
    Returns:
        Dictionary with answer, source_document, source_sections, citation
    """
    if not doc_data or 'documents' not in doc_data:
        return {
            'answer': 'ERROR: Invalid document data',
            'source_document': 'NONE',
            'source_sections': [],
            'citation': ''
        }
        
    documents = doc_data['documents']
    question_lower = question.lower()
    
    # Enhanced keyword mapping for better matching
    keyword_mappings = {
        'install': ['install', 'software', 'application', 'app', 'program', 'slack', 'teams'],
        'personal': ['personal', 'own', 'byod', 'bring your own'],
        'phone': ['phone', 'mobile', 'smartphone', 'device'],
        'laptop': ['laptop', 'work laptop', 'corporate laptop', 'computer'],
        'carry forward': ['carry forward', 'carry-forward', 'carryforward', 'unused leave', 'leftover'],
        'leave without pay': ['leave without pay', 'lwp', 'unpaid leave', 'approve', 'approves', 'approval'],
        'allowance': ['allowance', 'reimbursement', 'home office', 'wfh', 'work from home'],
        'da': ['da', 'daily allowance', 'meal', 'meals', 'receipts'],
        'work files': ['work files', 'files', 'data', 'documents', 'access'],
    }
    
    # Search for relevant sections across all documents
    matches = []
    
    for doc_name, sections in documents.items():
        for section_num, section_text in sections.items():
            section_lower = section_text.lower()
            
            # Calculate relevance score
            score = 0
            
            # Check for exact phrase matches (higher score)
            for key_phrase, alternatives in keyword_mappings.items():
                for alt in alternatives:
                    if alt in question_lower and alt in section_lower:
                        score += 3
                        
            # Check for individual word overlap
            question_words = set(re.findall(r'\b\w+\b', question_lower))
            section_words = set(re.findall(r'\b\w+\b', section_lower))
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'is', 'can', 'i', 'my', 'to', 'for', 'in', 'on', 'at', 'of', 'and', 'or', 'be', 'it', 'from', 'by', 'with', 'are', 'not', 'this', 'that', 'as', 'use', 'used'}
            question_words = question_words - stop_words
            section_words = section_words - stop_words
            
            common_words = question_words & section_words
            score += len(common_words)
            
            # Bonus for specific question types
            if 'personal' in question_lower and 'phone' in question_lower:
                if 'personal devices' in section_lower or 'byod' in section_lower:
                    score += 5
                    
            if 'install' in question_lower or 'software' in question_lower:
                if 'install software' in section_lower or 'without written approval' in section_lower:
                    score += 5
                    
            if 'carry forward' in question_lower or 'unused' in question_lower:
                if 'carry forward' in section_lower:
                    score += 5
                    
            if 'leave without pay' in question_lower or 'lwp' in question_lower:
                if 'lwp requires approval' in section_lower or 'department head and' in section_lower:
                    score += 5
                elif 'leave without pay' in section_lower:
                    score += 2
                    
            if 'da' in question_lower or 'daily allowance' in question_lower or 'meal' in question_lower:
                if 'da and meal receipts' in section_lower or 'cannot be claimed simultaneously' in section_lower:
                    score += 5
                    
            if 'allowance' in question_lower and ('home' in question_lower or 'office' in question_lower):
                if 'home office equipment allowance' in section_lower:
                    score += 5
            
            if score > 0:
                matches.append({
                    'document': doc_name,
                    'section': section_num,
                    'text': section_text,
                    'score': score
                })
                
    if not matches:
        # No relevant content found - use refusal template
        return {
            'answer': refusal_template,
            'source_document': 'NONE',
            'source_sections': [],
            'citation': ''
        }
        
    # Sort by score (highest first)
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Get top matches from SINGLE document (never blend)
    # Find the document with the highest scoring match
    doc_scores = {}
    for match in matches:
        doc_name = match['document']
        if doc_name not in doc_scores:
            doc_scores[doc_name] = []
        doc_scores[doc_name].append(match)
        
    # Pick the document with the best single match
    best_doc = max(doc_scores.keys(), key=lambda d: max(m['score'] for m in doc_scores[d]))
    best_matches = doc_scores[best_doc]
    
    # Get top sections from that single document (sorted by score)
    best_matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Use only high-scoring matches
    threshold = best_matches[0]['score'] * 0.6  # At least 60% of top score
    top_matches = [m for m in best_matches if m['score'] >= threshold][:3]
    
    if not top_matches or top_matches[0]['score'] < 3:
        # Not confident enough in the match
        return {
            'answer': refusal_template,
            'source_document': 'NONE',
            'source_sections': [],
            'citation': ''
        }
        
    # Build answer from single document
    answer_parts = []
    sections_used = []
    
    for match in top_matches:
        answer_parts.append(match['text'])
        sections_used.append(match['section'])
            
    # Format answer with citations
    answer_text = ' '.join(answer_parts)
    
    # Create citation
    doc_short = best_doc.replace('.txt', '')
    if len(sections_used) == 1:
        citation = f"[{doc_short} section {sections_used[0]}]"
    else:
        sections_str = ', '.join(sections_used)
        citation = f"[{doc_short} sections {sections_str}]"
        
    return {
        'answer': answer_text,
        'source_document': best_doc,
        'source_sections': sections_used,
        'citation': citation
    }


def main():
    """
    Main application entry point.
    Interactive CLI for policy document Q&A.
    """
    print("=" * 70)
    print("UC-X — Policy Document Q&A System")
    print("=" * 70)
    print()
    
    # Load documents
    policy_dir = "../data/policy-documents"
    print(f"Loading policy documents from: {policy_dir}")
    
    doc_data = retrieve_documents(policy_dir)
    if doc_data is None:
        print("ERROR: Failed to load policy documents", file=sys.stderr)
        sys.exit(1)
        
    print(f"✓ Loaded {len(doc_data['documents'])} policy documents:")
    for doc_name in doc_data['documents'].keys():
        section_count = len(doc_data['documents'][doc_name])
        print(f"  • {doc_name}: {section_count} sections")
    print()
    
    print("Type your questions (or 'quit' to exit)")
    print("-" * 70)
    print()
    
    # Interactive Q&A loop
    while True:
        try:
            question = input("Question: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
                
            # Answer the question
            result = answer_question(question, doc_data, REFUSAL_TEMPLATE)
            
            print()
            print("Answer:")
            print(result['answer'])
            print()
            
            if result['source_document'] != 'NONE':
                print(f"Source: {result['citation']}")
                print()
                
            print("-" * 70)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    main()
