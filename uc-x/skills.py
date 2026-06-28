import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from config import POLICY_DOCUMENTS, REFUSAL_TEMPLATE, HEDGING_PHRASES


@dataclass
class Answer:
    """Response object from answer_question skill"""
    success: bool
    answer: Optional[str] = None
    source: Optional[str] = None
    refusal_reason: Optional[str] = None


class DocumentRetrieval:
    """Skill: retrieve_documents — Load and index policy files"""
    
    def __init__(self):
        self.index: Dict[str, Dict[str, str]] = {}
    
    def load_documents(self) -> Dict[str, Dict[str, str]]:
        """
        Load all policy documents and index by section number.
        
        Returns:
            {document_name → {section_id → section_text}}
        
        Raises:
            FileNotFoundError: If any policy document is missing
        """
        self.index = {}
        
        for doc_name, doc_path in POLICY_DOCUMENTS.items():
            if not os.path.exists(doc_path):
                raise FileNotFoundError(
                    f"Policy document not found: {doc_path}\n"
                    f"Required files: {list(POLICY_DOCUMENTS.keys())}"
                )
            
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse sections: assume format "section X.Y: content"
            sections = self._parse_sections(content)
            self.index[doc_name] = sections
        
        return self.index
    
    def _parse_sections(self, content: str) -> Dict[str, str]:
        """
        Parse document into sections by section number pattern.
        Pattern: "section X.Y" or "X.Y:" at start of line
        """
        sections = {}
        section_pattern = r'^(?:section\s+)?(\d+\.\d+)[\s:]*(.+?)(?=^(?:section\s+)?\d+\.\d+\s|$)'
        
        matches = re.finditer(
            section_pattern,
            content,
            re.MULTILINE | re.DOTALL | re.IGNORECASE
        )
        
        for match in matches:
            section_id = match.group(1)
            section_text = match.group(2).strip()
            sections[section_id] = section_text
        
        return sections
    
    def get_index(self) -> Dict[str, Dict[str, str]]:
        """Return the loaded index"""
        if not self.index:
            raise RuntimeError(
                "Document index not loaded. Call load_documents() first."
            )
        return self.index


class AnswerGeneration:
    """Skill: answer_question — Search and answer from single source or refuse"""
    
    def __init__(self, doc_index: Dict[str, Dict[str, str]]):
        self.doc_index = doc_index
    
    def answer_question(self, question: str) -> Answer:
        """
        Search indexed documents for answer. Return single-source answer + citation
        or refusal template.
        
        Args:
            question: User's policy question
        
        Returns:
            Answer object with success status, answer text, and source citation
        """
        # Normalize question
        question_lower = question.lower().strip()
        
        # Search across all documents
        matches = self._search_documents(question_lower)
        
        if not matches:
            return Answer(
                success=False,
                refusal_reason=REFUSAL_TEMPLATE
            )
        
        if len(matches) > 1:
            # Multiple documents match — cross-document blend risk
            return Answer(
                success=False,
                refusal_reason=REFUSAL_TEMPLATE
            )
        
        # Single source found
        doc_name, section_id, section_text = matches[0]
        
        # Check for hedging language in answer
        if self._contains_hedging(section_text):
            return Answer(
                success=False,
                refusal_reason=REFUSAL_TEMPLATE
            )
        
        source_citation = f"{doc_name} section {section_id}"
        
        return Answer(
            success=True,
            answer=section_text,
            source=source_citation
        )
    
    def _search_documents(self, question: str) -> List[Tuple[str, str, str]]:
        """
        Search all documents for relevant sections.
        
        Returns:
            List of (doc_name, section_id, section_text) tuples
        """
        matches = []
        
        for doc_name, sections in self.doc_index.items():
            for section_id, section_text in sections.items():
                # Simple keyword matching (can be upgraded to TF-IDF or embeddings)
                if self._is_relevant(question, section_text):
                    matches.append((doc_name, section_id, section_text))
        
        return matches
    
    def _is_relevant(self, question: str, section_text: str) -> bool:
        """
        Determine if section text is relevant to question.
        Uses keyword matching with minimum threshold.
        """
        section_lower = section_text.lower()
        
        # Extract key terms from question (min 4 chars)
        key_terms = [
            word for word in question.split()
            if len(word) > 3 and word not in ['that', 'this', 'what', 'when', 'where']
        ]
        
        if not key_terms:
            return False
        
        # Match if at least 50% of key terms appear in section
        matches = sum(1 for term in key_terms if term in section_lower)
        return matches >= len(key_terms) * 0.5
    
    def _contains_hedging(self, text: str) -> bool:
        """Check if text contains prohibited hedging language"""
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in HEDGING_PHRASES)


class Agent:
    """Main Agent class — orchestrates retrieval and answer generation"""
    
    def __init__(self):
        self.retrieval = DocumentRetrieval()
        self.answerer = None
        self._initialized = False
    
    def initialize(self):
        """Load documents and set up answerer"""
        try:
            index = self.retrieval.load_documents()
            self.answerer = AnswerGeneration(index)
            self._initialized = True
            print("✓ Agent initialized. Documents loaded and indexed.")
        except FileNotFoundError as e:
            print(f"✗ Initialization failed: {e}")
            raise
    
    def query(self, question: str) -> str:
        """
        Answer a policy question.
        
        Args:
            question: User's policy question
        
        Returns:
            Formatted answer string (with citation or refusal)
        """
        if not self._initialized:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        answer = self.answerer.answer_question(question)
        
        if answer.success:
            return f"{answer.answer}\n\n[Source: {answer.source}]"
        else:
            return answer.refusal_reason
