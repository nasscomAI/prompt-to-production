"""
UC-X app.py — Policy Document Q&A Assistant for Central Manufacturing Company (CMC)
Implements RICE framework with strict single-source answering and zero blending.
See README.md for run command and expected behaviour.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# Refusal template - must be used verbatim when question is not in documents
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact {team} for guidance."""

# Policy documents configuration
POLICY_DOCUMENTS = {
    "policy_hr_leave.txt": "HR",
    "policy_it_acceptable_use.txt": "IT", 
    "policy_finance_reimbursement.txt": "Finance"
}

DOCUMENTS_PATH = Path(__file__).parent / ".." / "data" / "policy-documents"


class PolicyDocumentIndex:
    """Indexes policy documents by document name and section number for single-source retrieval."""
    
    def __init__(self):
        self.index: Dict[str, Dict[str, str]] = {}  # {document_name: {section_num: content}}
        self.document_teams: Dict[str, str] = {}  # {document_name: team_name}
    
    def load_document(self, filepath: Path, document_name: str, team_name: str) -> None:
        """Load a single policy document and index by section number."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.document_teams[document_name] = team_name
            
            # Parse sections - assuming format like "2.1" or "Section 2.1" or "2.1."
            # This regex finds section patterns in the document
            section_pattern = r'(?:Section\s+)?(\d+\.\d+)[:\.]?\s*(.*?)(?=(?:Section\s+)?\d+\.\d+[:\.]?|$)'
            sections = re.findall(section_pattern, content, re.DOTALL | re.IGNORECASE)
            
            if sections:
                self.index[document_name] = {}
                for section_num, section_content in sections:
                    self.index[document_name][section_num] = section_content.strip()
            else:
                # If no sections found, store entire document as section 0
                self.index[document_name] = {"0": content}
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Required policy file not found: {filepath}")
        except Exception as e:
            raise Exception(f"Error loading {document_name}: {str(e)}")


def retrieve_documents() -> PolicyDocumentIndex:
    """
    Skill: retrieve_documents
    Loads all 3 CMC policy files and indexes their content by document name and section number.
    Returns: PolicyDocumentIndex with all documents indexed
    Raises: Error if any required file is missing
    """
    index = PolicyDocumentIndex()
    
    missing_files = []
    for doc_name, team_name in POLICY_DOCUMENTS.items():
        filepath = DOCUMENTS_PATH / doc_name
        if not filepath.exists():
            missing_files.append(doc_name)
        else:
            try:
                index.load_document(filepath, doc_name, team_name)
            except Exception as e:
                missing_files.append(f"{doc_name} ({str(e)})")
    
    if missing_files:
        raise FileNotFoundError(
            f"Cannot proceed with partial document set. Missing files: {', '.join(missing_files)}\n"
            f"Expected location: {DOCUMENTS_PATH}"
        )
    
    return index


def answer_question(question: str, index: PolicyDocumentIndex) -> str:
    """
    Skill: answer_question
    Searches indexed policy documents and returns single-source answer with citation OR refusal template.
    
    Enforcement rules:
    - Never combine claims from different documents
    - Never use hedging phrases
    - Always cite document name + section number
    - Use refusal template if not in documents or ambiguous
    
    Returns: Either formatted answer with citation OR refusal template
    """
    question_lower = question.lower()
    
    # Extract key phrases and important words
    # Remove common stop words for better matching
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'from', 'is', 'are', 'can', 'i', 'my', 'what', 'when', 'where', 'who', 'how', 'do', 'does', 'will', 'would', 'should'}
    
    question_words = set(re.findall(r'\b\w+\b', question_lower))
    important_words = question_words - stop_words
    
    # Search for relevant sections across all documents
    matches: List[Tuple[str, str, str, float]] = []  # (doc_name, section_num, content, relevance_score)
    
    for doc_name, sections in index.index.items():
        for section_num, content in sections.items():
            content_lower = content.lower()
            
            # Calculate word overlap
            content_words = set(re.findall(r'\b\w+\b', content_lower))
            common_important = important_words & content_words
            
            # Require at least 2 important word matches
            if len(common_important) >= 2:
                # Base score: ratio of matched words
                relevance = len(common_important) / len(important_words) if important_words else 0
                
                # Bonus for longer word matches (more specific)
                # Bonus for longer word matches (more specific)
                for word in common_important:
                    if len(word) > 5:
                        relevance += 0.05
                
                # Bonus for multi-word phrase matches
                # Check for 2-word combinations from question
                words_list = list(important_words)
                for i in range(len(words_list) - 1):
                    phrase = f"{words_list[i]} {words_list[i+1]}"
                    if phrase in content_lower:
                        relevance += 0.2
                
                matches.append((doc_name, section_num, content, min(relevance, 1.0)))
    
    if not matches:
        # Question not found in any document - use refusal template
        team = determine_relevant_team(question_lower)
        return REFUSAL_TEMPLATE.format(team=team)
    
    # Sort by relevance
    matches.sort(key=lambda x: x[3], reverse=True)
    
    # Quality threshold - if best match is weak, refuse
    if matches[0][3] < 0.25:
        team = determine_relevant_team(question_lower)
        return REFUSAL_TEMPLATE.format(team=team)
    
    # Check if top matches are from different documents (potential blending risk)
    if len(matches) > 1:
        top_doc = matches[0][0]
        second_doc = matches[1][0]
        top_score = matches[0][3]
        second_score = matches[1][3]
        
        # If similar relevance from different documents, this creates ambiguity
        if second_doc != top_doc and second_score > 0.3 and (top_score - second_score) < 0.15:
            # Ambiguity detected - refuse rather than blend
            team = determine_relevant_team(question_lower)
            return REFUSAL_TEMPLATE.format(team=team)
    
    # Return single-source answer with citation
    doc_name, section_num, content, _ = matches[0]
    
    # Extract most relevant sentence(s) from the section
    answer_text = extract_answer_from_section(content, question_lower)
    
    return f"According to {doc_name} section {section_num}, {answer_text}"


def extract_answer_from_section(content: str, question_lower: str) -> str:
    """Extract the most relevant sentence(s) from a section to answer the question."""
    sentences = re.split(r'[.!?]+', content)
    
    best_sentence = ""
    best_score = 0
    
    question_words = set(re.findall(r'\b\w+\b', question_lower))
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:  # Skip very short fragments
            continue
            
        sentence_lower = sentence.lower()
        sentence_words = set(re.findall(r'\b\w+\b', sentence_lower))
        
        common = question_words & sentence_words
        if len(common) > best_score:
            best_score = len(common)
            best_sentence = sentence
    
    return best_sentence if best_sentence else content[:200].strip() + "..."


def determine_relevant_team(question_lower: str) -> str:
    """Determine which team to contact based on question keywords."""
    if any(word in question_lower for word in ['leave', 'vacation', 'remote', 'work from home', 'wfh']):
        return "HR"
    elif any(word in question_lower for word in ['computer', 'laptop', 'software', 'install', 'device', 'phone', 'access', 'password']):
        return "IT"
    elif any(word in question_lower for word in ['expense', 'reimbursement', 'claim', 'allowance', 'receipt', 'finance']):
        return "Finance"
    else:
        return "HR"  # Default to HR for general queries


def validate_no_hedging(answer: str) -> None:
    """Validate that answer contains no hedging phrases - raises assertion error if found."""
    hedging_phrases = [
        "while not explicitly covered",
        "typically",
        "generally understood",
        "it is common practice",
        "usually",
        "in most cases",
        "it appears",
        "it seems",
        "may be",
        "might be"
    ]
    
    answer_lower = answer.lower()
    for phrase in hedging_phrases:
        if phrase in answer_lower:
            raise AssertionError(f"Hedging phrase detected in answer: '{phrase}'")


def main():
    """Interactive CLI for policy Q&A."""
    print("=" * 70)
    print("CMC Policy Document Q&A Assistant")
    print("=" * 70)
    print()
    
    # Initialize - load and index documents
    try:
        print("Loading policy documents...")
        index = retrieve_documents()
        print(f"✓ Loaded {len(index.index)} policy documents")
        for doc_name in index.index.keys():
            section_count = len(index.index[doc_name])
            print(f"  - {doc_name}: {section_count} sections")
        print()
    except FileNotFoundError as e:
        print(f"ERROR: {str(e)}")
        print("\nCannot start without all required policy documents.")
        return
    except Exception as e:
        print(f"ERROR: Failed to load documents: {str(e)}")
        return
    
    print("Type your questions (or 'quit' to exit)")
    print("-" * 70)
    print()
    
    while True:
        try:
            question = input("Question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            # Get answer
            answer = answer_question(question, index)
            
            # Validate no hedging (self-check)
            try:
                validate_no_hedging(answer)
            except AssertionError as e:
                print(f"\n⚠ SYSTEM ERROR: {str(e)}")
                print("This should never happen - please report this bug.\n")
                continue
            
            print(f"\nAnswer: {answer}\n")
            print("-" * 70)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nERROR: {str(e)}\n")


if __name__ == "__main__":
    main()
