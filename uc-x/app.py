"""
UC-X — Policy Compliance Bot: Ask My Documents

Interactive CLI that retrieves cited answers from three core municipal policies
while strictly avoiding cross-document blending and hedged hallucination.

Policies indexed:
1. policy_hr_leave.txt — Employee leave entitlements and obligations
2. policy_it_acceptable_use.txt — IT device and resource usage rules
3. policy_finance_reimbursement.txt — Expense reimbursement guidelines

Core principles:
- NO claims blended across documents
- EVERY answer cited with document name + section number
- NO hedging phrases ("typically", "generally", "while not explicitly...")
- EXACT verbatim refusal template for out-of-scope questions
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# Verbatim refusal template (per README.md)
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# Hedging phrases that are strictly forbidden
FORBIDDEN_HEDGES = {
    "while not explicitly covered",
    "typically",
    "generally",
    "it is generally understood",
    "standard practice",
    "commonly",
    "usually",
    "can usually",
    "may typically",
    "it is common",
    "appears to",
    "seems to",
}

# Document metadata
DOCUMENTS = {
    "policy_hr_leave.txt": {
        "display_name": "policy_hr_leave.txt",
        "path": "../data/policy-documents/policy_hr_leave.txt",
        "category": "hr",
    },
    "policy_it_acceptable_use.txt": {
        "display_name": "policy_it_acceptable_use.txt",
        "path": "../data/policy-documents/policy_it_acceptable_use.txt",
        "category": "it",
    },
    "policy_finance_reimbursement.txt": {
        "display_name": "policy_finance_reimbursement.txt",
        "path": "../data/policy-documents/policy_finance_reimbursement.txt",
        "category": "finance",
    },
}


@dataclass
class PolicySection:
    """Represents an indexed policy section"""
    document_name: str
    section_number: str
    full_text: str
    keywords: List[str]


class PolicyIndex:
    """Maintains indexed knowledge base of policy documents"""
    
    def __init__(self):
        self.sections: List[PolicySection] = []
        self.documents_loaded = set()
    
    def load_document(self, file_path: str, doc_name: str) -> None:
        """
        Loads and indexes a policy document by section numbers.
        
        Args:
            file_path: Path to policy .txt file
            doc_name: Canonical document name for citations
        
        Raises:
            FileNotFoundError if file not found
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise FileNotFoundError(f"Failed to read {doc_name}: {str(e)}")
        
        # Parse sections by numbered clauses (e.g., "2.3 text...")
        lines = content.split('\n')
        current_section = None
        current_text = []
        
        for line in lines:
            # Match section headers like "2.3 ", "3.1 ", etc.
            match = re.match(r'^(\d+\.\d+)\s+(.+)$', line.strip())
            
            if match:
                # Save previous section if exists
                if current_section:
                    full_text = ' '.join(current_text).strip()
                    if full_text:
                        keywords = self._extract_keywords(full_text)
                        section = PolicySection(
                            document_name=doc_name,
                            section_number=current_section,
                            full_text=full_text,
                            keywords=keywords
                        )
                        self.sections.append(section)
                
                current_section = match.group(1)
                current_text = [match.group(2)]
            elif current_section and line.strip():
                # Continue accumulating text
                if not re.match(r'^═+$|^[A-Z\s]+POLICY|^[A-Z\s]+DEPARTMENT', line):
                    current_text.append(line.strip())
        
        # Don't forget the last section
        if current_section:
            full_text = ' '.join(current_text).strip()
            if full_text:
                keywords = self._extract_keywords(full_text)
                section = PolicySection(
                    document_name=doc_name,
                    section_number=current_section,
                    full_text=full_text,
                    keywords=keywords
                )
                self.sections.append(section)
        
        self.documents_loaded.add(doc_name)
        print(f"Indexed {doc_name}: {len([s for s in self.sections if s.document_name == doc_name])} sections")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extracts searchable keywords from section text"""
        # Simple keyword extraction: split on whitespace, lowercase, filter stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'be', 'and', 'or', 'not', 'as', 'at', 'by', 'for', 'in', 'of', 'to', 'with', 'from', 'on'}
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]
    
    def search(self, query: str, limit: int = 10) -> List[PolicySection]:
        """
        Searches indexed sections for relevant matches.
        Returns sections ranked by keyword overlap with query.
        
        Args:
            query: Natural language question
            limit: Maximum results to return
        
        Returns:
            List of PolicySection objects ranked by relevance
        """
        query_keywords = set(self._extract_keywords(query))
        
        if not query_keywords:
            return []
        
        # Score each section by keyword overlap
        scored_sections = []
        for section in self.sections:
            section_keywords = set(section.keywords)
            overlap = len(query_keywords & section_keywords)
            
            if overlap > 0:
                scored_sections.append((section, overlap))
        
        # Sort by score (descending) then by document order
        scored_sections.sort(key=lambda x: (-x[1], self.sections.index(x[0])))
        
        return [section for section, score in scored_sections[:limit]]


def retrieve_documents(policy_dir: str = "data/policy-documents") -> PolicyIndex:
    """
    Ingests and indexes the three core policy files, maintaining a 
    mapping of content to specific section numbers and filenames.
    
    Args:
        policy_dir: Directory containing policy .txt files
    
    Returns:
        PolicyIndex object — a searchable knowledge base partitioned by document
    
    Error handling:
        If any of the three mandatory files are missing, the system fails 
        to initialize and alerts the user.
    """
    
    index = PolicyIndex()
    
    # Mandatory documents that must be present
    mandatory_docs = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]
    
    base_path = Path(policy_dir)
    missing_docs = []
    
    for doc_name in mandatory_docs:
        file_path = base_path / doc_name
        
        if not file_path.exists():
            missing_docs.append(doc_name)
    
    if missing_docs:
        error_msg = (
            f"INITIALIZATION FAILED: Missing mandatory policy files:\n"
            f"{', '.join(missing_docs)}\n"
            f"System cannot proceed without all three policies."
        )
        raise FileNotFoundError(error_msg)
    
    # Load all documents
    for doc_name in mandatory_docs:
        file_path = base_path / doc_name
        index.load_document(str(file_path), doc_name)
    
    return index


def answer_question(query: str, index: PolicyIndex) -> str:
    """
    Performs a high-precision search across indexed documents to find 
    a single-source answer.
    
    Core enforcement:
    - NO blending of claims from multiple documents
    - EVERY factual claim cited with [Document Name] and [Section Number]
    - NO hedging phrases
    - EXACT verbatim refusal if question not covered
    
    Args:
        query: User question
        index: PolicyIndex knowledge base
    
    Returns:
        Response string with direct answer + citation OR verbatim refusal
    
    Error handling:
        If search returns results from multiple documents that would blend,
        provides separate distinct sections for each document context.
    """
    
    # Search for relevant sections
    results = index.search(query, limit=15)
    
    if not results:
        return REFUSAL_TEMPLATE
    
    # Group results by document to detect cross-document blending
    by_document = {}
    for section in results:
        if section.document_name not in by_document:
            by_document[section.document_name] = []
        by_document[section.document_name].append(section)
    
    # If results come from exactly one document, provide direct answer
    if len(by_document) == 1:
        doc_name = list(by_document.keys())[0]
        top_sections = by_document[doc_name][:3]
        
        if not top_sections:
            return REFUSAL_TEMPLATE
        
        # Build response with citations
        response_parts = []
        for section in top_sections:
            response_parts.append(
                f"{section.full_text}\n"
                f"[{section.document_name}, Section {section.section_number}]"
            )
        
        response = "\n\n".join(response_parts)
        
        # Validate no hedging
        response_lower = response.lower()
        for hedge in FORBIDDEN_HEDGES:
            if hedge in response_lower:
                # Remove the hedging language
                for word in FORBIDDEN_HEDGES:
                    response = re.sub(
                        r'\b' + re.escape(word) + r'\b',
                        '', 
                        response, 
                        flags=re.IGNORECASE
                    )
        
        return response.strip()
    
    # Multiple documents matched — check for direct blending need
    # Special handling: if query touches multiple policies, provide separate answers
    response_parts = []
    
    for doc_name in sorted(by_document.keys()):
        doc_sections = by_document[doc_name][:2]  # Top 2 from each doc
        doc_response = []
        
        for section in doc_sections:
            doc_response.append(
                f"{section.full_text}\n"
                f"[{section.document_name}, Section {section.section_number}]"
            )
        
        if doc_response:
            response_parts.append("---\n" + "\n\n".join(doc_response))
    
    if response_parts:
        # Prefix indicating separate policy contexts
        return (
            "This question touches multiple policy documents. "
            "Here are the relevant sections:\n\n" + 
            "\n".join(response_parts)
        )
    
    return REFUSAL_TEMPLATE


def interactive_cli(index: PolicyIndex) -> None:
    """
    Interactive command-line interface for policy queries.
    
    Accepts questions and returns cited answers or refusal template.
    Type 'exit' or 'quit' to terminate.
    """
    
    print("\n" + "=" * 70)
    print("MUNICIPAL POLICY COMPLIANCE BOT — Interactive Query System")
    print("=" * 70)
    print("\nType your question to search the policy documents.")
    print("All answers are cited with document name and section number.")
    print("Type 'exit' or 'quit' to terminate.\n")
    
    while True:
        try:
            query = input("Your question: ").strip()
            
            if not query:
                print("Please enter a question.\n")
                continue
            
            if query.lower() in ['exit', 'quit']:
                print("\nThank you for using the Policy Compliance Bot. Goodbye.\n")
                break
            
            # Get answer
            answer = answer_question(query, index)
            print(f"\nAnswer:\n{answer}\n")
        
        except KeyboardInterrupt:
            print("\n\nThank you for using the Policy Compliance Bot. Goodbye.\n")
            break
        except Exception as e:
            print(f"Error processing query: {str(e)}\n")


def main():
    """
    Entry point for the Policy Compliance Bot.
    
    Loads all three mandatory policy documents and launches interactive CLI.
    """
    
    try:
        print("Initializing Policy Compliance Bot...\n")
        
        # Resolve path relative to script location
        script_dir = Path(__file__).parent.parent
        policy_dir = script_dir / "data" / "policy-documents"
        
        # Retrieve and index documents
        index = retrieve_documents(str(policy_dir))
        
        print(f"\nSuccessfully loaded {len(index.documents_loaded)} policy documents")
        print(f"Indexed {len(index.sections)} total sections\n")
        
        # Launch interactive CLI
        interactive_cli(index)
    
    except FileNotFoundError as e:
        print(f"\nFATAL ERROR: {str(e)}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nFATAL ERROR: Unexpected error: {str(e)}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
