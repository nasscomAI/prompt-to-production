"""
UC-X app.py — Policy Document Q&A System
Implements retrieve_documents and answer_question skills per skills.md
Enforces agents.md constraints: no blending, exact citations, strict refusal
"""

import re
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional, List

# Constants
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

HEDGING_PHRASES = {
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is often",
    "usually",
    "generally",
    "in practice",
    "may be",
    "might be"
}


def retrieve_documents() -> Dict[str, Dict[str, str]]:
    """
    Load and index all three policy documents by document name and section number.
    Returns: indexed_documents dict {document_name: {section_id: section_text}}
    Raises: FileNotFoundError if any policy file is missing or unreadable
    """
    base_dir = Path(__file__).parent.parent / "data" / "policy-documents"
    indexed = {}

    for filename in POLICY_FILES:
        filepath = base_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Policy file missing: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read {filename}: {e}")

        # Parse document into sections by section number
        sections = _parse_sections(content)
        indexed[filename] = sections

    return indexed


def _parse_sections(content: str) -> Dict[str, str]:
    """
    Parse document content into sections by section number.
    Detects patterns: "section X.Y:", "[X.Y]", "X.Y:", line starting with "X.Y"
    Returns: {section_id: section_text}
    """
    sections = {}
    current_section = None
    section_lines = []

    for line in content.split('\n'):
        # Match section headers: "section 2.6", "[2.6]", "2.6:", etc.
        match = re.match(r'(?:section\s+)?(\d+\.\d+)\s*[:\-]?\s*(.*)', line, re.IGNORECASE)

        if match:
            section_num = match.group(1)
            rest_of_line = match.group(2)

            # Save previous section
            if current_section and section_lines:
                sections[current_section] = '\n'.join(section_lines).strip()

            # Start new section
            current_section = section_num
            section_lines = [rest_of_line] if rest_of_line.strip() else []
        elif current_section is not None:
            section_lines.append(line)

    # Save final section
    if current_section and section_lines:
        sections[current_section] = '\n'.join(section_lines).strip()

    # Store full document for fallback
    sections['_full'] = content

    return sections


def search_indexed_documents(
    question: str,
    indexed: Dict[str, Dict[str, str]]
) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
    """
    Search indexed documents for answer to question.
    Returns: (answer_text, doc_name, source_citation, found)

    - found=True: answer found in single document
    - found=False: question not in documents OR spans multiple documents (ambiguous)

    Enforces: no blending across documents, exact citations, refusal on ambiguity
    """
    question_lower = question.lower()
    keyword_search = _extract_keywords(question_lower)

    # Search across all documents and sections
    matches = []  # (doc_name, section_id, section_text, relevance_score)

    for doc_name, sections in indexed.items():
        for section_id, section_text in sections.items():
            if section_id == '_full':
                continue

            # Calculate relevance score based on keyword matches
            score = 0
            text_lower = section_text.lower()

            for keyword in keyword_search:
                score += text_lower.count(keyword)

            if score > 0:
                matches.append((doc_name, section_id, section_text, score))

    if not matches:
        return None, None, None, False

    matches.sort(key=lambda x: x[3], reverse=True)

    top_doc, top_section, top_text, top_score = matches[0]

    documents_with_matches = set()
    for doc, _, _, score in matches:
        if score >= top_score * 0.6:  # 60% of top score threshold
            documents_with_matches.add(doc)

    if len(documents_with_matches) > 1:
        # Multiple documents match significantly — ambiguous, refuse
        return None, None, None, False

    # Valid single-source match
    citation = f"{top_doc}.{top_section}"
    return top_text, top_doc, citation, True


def _extract_keywords(question: str) -> List[str]:
    """Extract meaningful keywords from question for search."""
    stop_words = {
        'can', 'i', 'what', 'is', 'the', 'do', 'my', 'me', 'on', 'in', 'at',
        'to', 'for', 'a', 'an', 'and', 'or', 'if', 'how', 'when', 'where',
        'who', 'which', 'will', 'would', 'should', 'could', 'have', 'has',
        'be', 'are', 'am', 'was', 'were', 'that', 'this', 'with', 'from'
    }

    words = re.findall(r'\b\w+\b', question.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords


def answer_question(question: str, indexed: Dict) -> Tuple[str, str]:
    """
    Answer a question from indexed documents.
    Returns: (answer, answer_type) where answer_type is "answer" or "refusal"

    Enforces agents.md rules:
    - No blending across documents
    - No hedging phrases in output
    - Exact refusal template when not found
    - Required citations for all answers
    """

    answer_text, doc_name, citation, found = search_indexed_documents(question, indexed)

    if not found:
        # Question not covered in documents — use refusal template exactly
        return REFUSAL_TEMPLATE, "refusal"

    # Check for hedging phrases in answer (anti-hallucination)
    # If answer contains hedging, treat as uncertain and refuse
    answer_lower = answer_text.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in answer_lower:
            # Contains hedging language — refuse rather than guess
            return REFUSAL_TEMPLATE, "refusal"

    # Format answer with required citation
    formatted_answer = f"{answer_text}\n\n[Source: {citation}]"

    return formatted_answer, "answer"


def main():
    parser_description = "UC-X: Ask My Documents — Policy Document Q&A System"

    print("=" * 70)
    print(parser_description)
    print("=" * 70)
    print("\nLoading policy documents...")

    # Load and index documents
    try:
        indexed = retrieve_documents()
        doc_count = sum(len(sections) - 1 for sections in indexed.values())  # Exclude _full
        print(f"✓ Loaded {len(indexed)} policy documents with {doc_count} sections\n")
    except (FileNotFoundError, IOError) as e:
        print(f"ERROR: {e}")
        print(f"\nExpected policy files in: {Path(__file__).parent.parent / 'data' / 'policy-documents'}")
        return 1

    print("Type questions about company policies (HR, IT, Finance).")
    print("Type 'quit' or 'exit' to exit.\n")

    # Interactive CLI loop
    while True:
        try:
            question = input("Q: ").strip()

            if question.lower() in ('quit', 'exit', 'q'):
                print("\nThank you for using UC-X. Goodbye!")
                break

            if not question:
                continue

            answer, _ = answer_question(question, indexed)

            print(f"\n{answer}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"ERROR: {e}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
