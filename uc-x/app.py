#!/usr/bin/env python3
"""
UC-X: Policy Document Q&A Agent
Answers questions using only three policy documents with single-source citations.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

DOCUMENT_NAMES = [
    "policy_hr_leave",
    "policy_it_acceptable_use",
    "policy_finance_reimbursement",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally speaking",
    "in most cases",
    "as a general rule",
    "commonly",
    "usually",
    "standard practice",
]


def retrieve_documents(file_paths: List[str]) -> Dict[str, Any]:
    """
    Loads all three policy files and indexes content by document name and section number.
    """
    indexed_corpus = {}

    for file_path, doc_name in zip(file_paths, DOCUMENT_NAMES):
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {file_path}")

        if path.suffix.lower() != ".txt":
            raise ValueError(f"File must be .txt: {file_path}")

        content = path.read_text(encoding="utf-8")
        sections = {}
        parse_warnings = []

        lines = content.split("\n")
        current_section = None
        current_text = []

        for line in lines:
            section_match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
            if section_match:
                if current_section is not None:
                    if current_section in sections:
                        parse_warnings.append(f"Duplicate section {current_section} in {doc_name}, keeping last")
                    sections[current_section] = " ".join(current_text).strip()
                current_section = section_match.group(1)
                current_text = [section_match.group(2)]
            elif current_section is not None and line.strip():
                stripped = line.strip()
                if not stripped.startswith("═══") and not re.match(r"^\d+\.\s", stripped):
                    current_text.append(stripped)

        if current_section is not None:
            if current_section in sections:
                parse_warnings.append(f"Duplicate section {current_section} in {doc_name}, keeping last")
            sections[current_section] = " ".join(current_text).strip()

        if not sections:
            parse_warnings.append(f"No sections parsed from {doc_name}")

        indexed_corpus[doc_name] = {
            "sections": sections,
            "parse_warnings": parse_warnings,
        }

    return {"indexed_corpus": indexed_corpus}


def check_hedging(text: str) -> List[str]:
    """Check for hedging phrases in the answer."""
    violations = []
    text_lower = text.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in text_lower:
            violations.append(phrase)
    return violations


def score_relevance(question: str, section_text: str) -> float:
    """Score relevance of a section to a question."""
    question_words = set(re.findall(r"\b\w+\b", question))
    section_words = set(re.findall(r"\b\w+\b", section_text))

    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "what", "when", "where", "who", "why", "how", "my", "your", "his", "her", "its", "our", "their", "me", "him", "us", "them", "from", "use", "when", "can", "am", "are"}

    domain_common = {"work", "home", "personal", "access", "employee", "approved", "arrangement", "policy", "section", "may", "must", "shall", "will", "only", "not", "per", "rs", "days", "within", "claim", "reimbursement", "entitled", "require", "requires", "required", "mandatory", "prohibited", "allowed", "permitted", "eligible", "approval", "approve", "submit", "submitted", "submission"}

    question_keywords = question_words - stopwords
    section_keywords = section_words - stopwords

    if not question_keywords:
        return 0.0

    overlap = question_keywords & section_keywords

    specific_matches = overlap - domain_common
    common_matches = overlap & domain_common

    score = len(specific_matches) * 2 + len(common_matches) * 1
    return float(score)


def find_relevant_sections(question: str, indexed_corpus: Dict[str, Any]) -> List[Tuple[str, str, str, float]]:
    """
    Find sections relevant to the question across all documents with scores.
    Returns list of (doc_name, section_num, section_text, score).
    """
    question_lower = question.lower()
    scored = []

    for doc_name, doc_data in indexed_corpus.items():
        sections = doc_data.get("sections", {})
        for section_num, section_text in sections.items():
            score = score_relevance(question_lower, section_text.lower())
            if score >= 2.0:
                scored.append((doc_name, section_num, section_text, score))

    scored.sort(key=lambda x: x[3], reverse=True)

    return scored


def extract_answer(question: str, doc_name: str, section_num: str, section_text: str) -> str:
    """Extract a direct answer from the section text."""
    return section_text


def answer_question(question: str, indexed_corpus: Dict[str, Any]) -> Dict[str, Any]:
    """
    Searches indexed documents for a single-source answer; returns cited response or exact refusal template.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    scored = find_relevant_sections(question, indexed_corpus)

    if not scored:
        return {"refusal": True, "template": REFUSAL_TEMPLATE}

    # Check if top sections come from multiple documents
    top_score = scored[0][3]
    top_sections = [s for s in scored if s[3] == top_score]
    top_doc_names = set(s[0] for s in top_sections)

    if len(top_doc_names) > 1:
        return {"refusal": True, "template": REFUSAL_TEMPLATE}

    # Take the highest-scoring section from the single top document
    doc_name = scored[0][0]
    section_num = scored[0][1]
    section_text = scored[0][2]

    answer = extract_answer(question, doc_name, section_num, section_text)

    hedging = check_hedging(answer)
    if hedging:
        return {"refusal": True, "template": REFUSAL_TEMPLATE}

    return {
        "answer": answer,
        "source_document": doc_name + ".txt",
        "source_section": section_num,
    }


def print_answer(response: Dict[str, Any]):
    """Print the answer in the required format."""
    if response.get("refusal"):
        print(response["template"])
    else:
        print(f"Answer: {response['answer']}")
        print(f"Source: {response['source_document']} section {response['source_section']}")


def main():
    try:
        dataset = retrieve_documents(POLICY_FILES)
        indexed_corpus = dataset["indexed_corpus"]

        for doc_name, doc_data in indexed_corpus.items():
            for warning in doc_data.get("parse_warnings", []):
                print(f"WARNING: {warning}", file=sys.stderr)

        print("Policy Q&A Agent ready. Type 'exit' to quit.")
        print("Documents loaded:", ", ".join(DOCUMENT_NAMES))
        print()

        while True:
            try:
                question = input("Question: ").strip()
                if question.lower() in ("exit", "quit", "q"):
                    break
                if not question:
                    continue

                response = answer_question(question, indexed_corpus)
                print_answer(response)
                print()

            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()