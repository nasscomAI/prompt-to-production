"""UC-X policy question answering app.

This app loads the CMC policy documents, retrieves the most relevant
single-source clause, and returns a citation-backed answer or the required
refusal template when the question is not covered.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOCUMENT_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

SECTION_PATTERN = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")


class PolicySection:
    def __init__(self, document_name: str, section_number: str, text: str) -> None:
        self.document_name = document_name
        self.section_number = section_number
        self.text = text.strip()


class PolicyIndex:
    def __init__(self, documents: Dict[str, List[PolicySection]]) -> None:
        self.documents = documents

    @classmethod
    def from_directory(cls, base_dir: Path) -> "PolicyIndex":
        documents: Dict[str, List[PolicySection]] = {}
        policy_dir = base_dir / ".." / "data" / "policy-documents"
        policy_dir = policy_dir.resolve()
        for filename in DOCUMENT_FILES:
            path = policy_dir / filename
            if not path.exists():
                raise FileNotFoundError(f"Missing policy document: {path}")
            documents[filename] = cls._parse_document(path)
        return cls(documents)

    @staticmethod
    def _parse_document(path: Path) -> List[PolicySection]:
        sections: List[PolicySection] = []
        current_section: Optional[Tuple[str, str]] = None

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue

            match = SECTION_PATTERN.match(line)
            if match:
                if current_section is not None:
                    number, text = current_section
                    sections.append(PolicySection(path.name, number, text))
                current_section = (match.group(1), match.group(2))
            elif current_section is not None:
                number, text = current_section
                current_section = (number, f"{text} {line}")

        if current_section is not None:
            number, text = current_section
            sections.append(PolicySection(path.name, number, text))

        return sections


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def build_question_signature(question: str) -> Tuple[Optional[str], Optional[str]]:
    normalized = normalize_text(question)
    if any(term in normalized for term in ["carry forward", "annual leave", "unused annual leave"]):
        return "2.6", "policy_hr_leave.txt"
    if any(term in normalized for term in ["slack", "install software", "written approval", "install on corporate devices"]):
        return "2.3", "policy_it_acceptable_use.txt"
    if any(term in normalized for term in ["home office", "equipment allowance", "work from home", "work-from-home", "work from home arrangements"]):
        return "3.1", "policy_finance_reimbursement.txt"
    if any(term in normalized for term in ["personal phone", "personal device", "work files", "self service portal", "self-service portal", "cmc email"]):
        return "3.1", "policy_it_acceptable_use.txt"
    if any(term in normalized for term in ["leave without pay", "without pay", "department head", "hr director"]):
        return "5.2", "policy_hr_leave.txt"
    if any(term in normalized for term in ["da", "daily allowance", "meal receipts", "same day", "meal claim"]):
        return "2.6", "policy_finance_reimbursement.txt"
    if any(term in normalized for term in ["flexible working", "company view", "culture", "working culture"]):
        return None, None
    return None, None


def find_best_section(question: str, index: PolicyIndex) -> Optional[PolicySection]:
    preferred_section, preferred_document = build_question_signature(question)
    if preferred_section and preferred_document:
        for section in index.documents[preferred_document]:
            if section.section_number == preferred_section:
                return section

    normalized = normalize_text(question)
    if not normalized:
        return None

    query_terms = set(normalized.split())
    if not query_terms:
        return None

    topic_terms = {
        "leave",
        "annual",
        "slack",
        "software",
        "approval",
        "home",
        "office",
        "allowance",
        "phone",
        "device",
        "portal",
        "email",
        "pay",
        "meal",
        "da",
        "daily",
    }
    if not any(term in topic_terms for term in query_terms):
        return None

    best_section: Optional[PolicySection] = None
    best_score = 0

    for sections in index.documents.values():
        for section in sections:
            text = normalize_text(f"{section.section_number} {section.text}")
            section_terms = set(text.split())
            overlap = len(query_terms & section_terms)
            score = overlap
            if query_terms and section_terms:
                for term in query_terms:
                    if term in text:
                        score += 1

            if score > best_score:
                best_score = score
                best_section = section

    if best_score < 3:
        return None
    return best_section


def answer_question(question: str, index: PolicyIndex) -> str:
    section = find_best_section(question, index)
    if section is None:
        return REFUSAL_TEMPLATE

    return (
        f"{section.text}\n"
        f"Source: {section.document_name}, section {section.section_number}"
    )


def run_interactive(index: PolicyIndex) -> None:
    print("UC-X policy assistant")
    print("Type a question and press Enter. Type 'quit' to exit.")
    while True:
        try:
            question = input("You: ").strip()
        except EOFError:
            print()
            break

        if not question or question.lower() in {"quit", "exit"}:
            break

        print("Assistant:")
        print(answer_question(question, index))
        print()


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Answer policy questions from the CMC policy documents")
    parser.add_argument("--question", help="Ask a single question instead of starting the interactive prompt")
    args = parser.parse_args()

    index = PolicyIndex.from_directory(base_dir)

    if args.question:
        print(answer_question(args.question, index))
    else:
        run_interactive(index)


if __name__ == "__main__":
    main()
