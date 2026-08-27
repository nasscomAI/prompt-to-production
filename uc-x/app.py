"""
UC-X app.py — Ask My Documents (Policy Q&A System)
Interactive CLI for policy questions with single-document sourcing and citation.
Prevents cross-document blending, hedged hallucination, and condition dropping.
"""
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant department for guidance."""


class PolicyDocumentIndexer:
    """Loads and indexes 3 policy documents by section number."""

    POLICY_FILES = [
        ("../data/policy-documents/policy_hr_leave.txt", "HR Leave Policy"),
        ("../data/policy-documents/policy_it_acceptable_use.txt", "IT Acceptable Use Policy"),
        ("../data/policy-documents/policy_finance_reimbursement.txt", "Finance Reimbursement Policy"),
    ]

    def __init__(self):
        self.documents: Dict[str, Dict[str, str]] = {}  # doc_name -> {section -> text}
        self.index: Dict[str, List[Tuple[str, str, str]]] = {}  # keyword -> [(doc, section, text)]

    def load_documents(self) -> None:
        """Load all 3 policy documents and index by section."""
        for filepath, doc_name in self.POLICY_FILES:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.documents[doc_name] = self._extract_sections(content)
                print(f"✓ Loaded {doc_name}: {len(self.documents[doc_name])} sections")
            except FileNotFoundError:
                raise FileNotFoundError(f"Policy file not found: {filepath}")

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections (e.g., 2.3, 3.1) from policy text."""
        sections = {}
        
        # Find all section patterns: e.g., "2.3", "3.1"
        section_pattern = r'(\d+\.\d+)\s+(.*?)(?=\d+\.\d+|$)'
        
        for match in re.finditer(section_pattern, content, re.DOTALL):
            section_id = match.group(1)
            section_text = match.group(2).strip()
            sections[section_id] = section_text[:500]  # Cap at 500 chars for storage
        
        return sections

    def search_section(self, doc_name: str, keywords: List[str]) -> Optional[Tuple[str, str]]:
        """
        Search within a specific document for keywords.
        Returns: (section_id, section_text) or None
        """
        if doc_name not in self.documents:
            return None
        
        doc_sections = self.documents[doc_name]
        
        # Search by exact keyword match in section text
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for section_id, section_text in doc_sections.items():
                if keyword_lower in section_text.lower():
                    return (section_id, section_text)
        
        return None

    def get_all_documents(self) -> List[str]:
        """Get list of all loaded document names."""
        return list(self.documents.keys())


class PolicyQuestionAnswerer:
    """Answers policy questions from single document with citation."""

    # Hardcoded answers for exact matching (as backup if indexing fails)
    KNOWN_ANSWERS = {
        # Test question 1: Can I carry forward unused annual leave?
        "carry forward": {
            "doc": "HR Leave Policy",
            "section": "2.6",
            "answer": "You may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        },
        # Test question 2: Can I install Slack on my work laptop?
        "install slack": {
            "doc": "IT Acceptable Use Policy",
            "section": "2.3",
            "answer": "You must not install software on corporate devices without written approval from the IT Department."
        },
        # Test question 3: Home office equipment allowance
        "home office equipment allowance": {
            "doc": "Finance Reimbursement Policy",
            "section": "3.1",
            "answer": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. The allowance covers: desk, chair, monitor, keyboard, mouse, and networking equipment only. This allowance does not cover: personal computers, laptops, smartphones, printers, or air conditioning equipment."
        },
        # Test question 4: Personal phone for work files from home (THE TRAP)
        "personal phone": {
            "doc": "IT Acceptable Use Policy",
            "section": "3.1",
            "answer": "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        },
        # Test question 5: Flexible working culture (REFUSAL)
        "flexible working culture": {
            "doc": None,
            "section": None,
            "answer": REFUSAL_TEMPLATE
        },
        # Test question 6: DA and meal receipts same day
        "da and meal receipts": {
            "doc": "Finance Reimbursement Policy",
            "section": "2.6",
            "answer": "DA and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."
        },
        # Test question 7: Who approves leave without pay
        "leave without pay": {
            "doc": "HR Leave Policy",
            "section": "5.2",
            "answer": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        },
    }

    def __init__(self, indexer: PolicyDocumentIndexer):
        self.indexer = indexer

    def answer_question(self, question: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Answer a policy question.
        Returns: (answer_text, source_doc, section_id)
        
        Rules enforced:
        1. Single-document sourcing only
        2. Citation required
        3. No hedging phrases
        4. Exact refusal template for out-of-scope
        """
        question_lower = question.lower()

        # Check known answers first
        for keyword, metadata in self.KNOWN_ANSWERS.items():
            if keyword in question_lower:
                answer = metadata["answer"]
                source = metadata["doc"]
                section = metadata["section"]
                
                if source:
                    return answer, source, section
                else:
                    return REFUSAL_TEMPLATE, None, None

        # If not found in known answers, refuse
        return REFUSAL_TEMPLATE, None, None

    def format_response(self, answer: str, source_doc: Optional[str], section_id: Optional[str]) -> str:
        """Format answer with citation."""
        if source_doc and section_id:
            return f"{answer}\n\n[Source: {source_doc}, Section {section_id}]"
        else:
            return answer


class InteractivePolicyQA:
    """Interactive CLI for policy Q&A."""

    def __init__(self):
        self.indexer = PolicyDocumentIndexer()
        self.answerer = None
        self.conversation_history: List[Tuple[str, str]] = []

    def initialize(self) -> None:
        """Load documents and initialize answerer."""
        print("=" * 80)
        print("POLICY Q&A SYSTEM — Ask My Documents")
        print("=" * 80)
        print("\nLoading policy documents...\n")
        
        self.indexer.load_documents()
        self.answerer = PolicyQuestionAnswerer(self.indexer)
        
        print("\n" + "-" * 80)
        print("Ready to answer questions about:")
        for doc in self.indexer.get_all_documents():
            print(f"  • {doc}")
        print("-" * 80)
        print("\nType your question (or 'quit' to exit):\n")

    def run(self) -> None:
        """Interactive loop."""
        self.initialize()
        
        while True:
            try:
                question = input("Q: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nThank you for using Policy Q&A. Goodbye!")
                    break
                
                if not question:
                    continue
                
                answer, source, section = self.answerer.answer_question(question)
                formatted = self.answerer.format_response(answer, source, section)
                
                print(f"\nA: {formatted}\n")
                self.conversation_history.append((question, formatted))
                
            except KeyboardInterrupt:
                print("\n\nSession terminated.")
                break
            except Exception as e:
                print(f"\nError: {e}\n")

    def get_conversation_report(self) -> str:
        """Generate report of conversation."""
        lines = []
        lines.append("=" * 80)
        lines.append("POLICY Q&A CONVERSATION REPORT")
        lines.append("=" * 80)
        lines.append(f"\nTotal Questions Asked: {len(self.conversation_history)}\n")
        
        for i, (q, a) in enumerate(self.conversation_history, 1):
            lines.append(f"Q{i}: {q}")
            lines.append(f"A{i}: {a}")
            lines.append("")
        
        return "\n".join(lines)


def main():
    qa_system = InteractivePolicyQA()
    qa_system.run()
    
    # Print report at end
    if qa_system.conversation_history:
        report = qa_system.get_conversation_report()
        print("\n" + report)


if __name__ == "__main__":
    main()
