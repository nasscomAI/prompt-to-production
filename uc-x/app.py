"""
UC-X app.py — Policy document Q&A.
Built using agents.md and skills.md.
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DATA_FILES = [
    os.path.join('..', 'data', 'policy-documents', 'policy_hr_leave.txt'),
    os.path.join('..', 'data', 'policy-documents', 'policy_it_acceptable_use.txt'),
    os.path.join('..', 'data', 'policy-documents', 'policy_finance_reimbursement.txt'),
]

STOP_WORDS = {
    'the', 'is', 'in', 'at', 'of', 'for', 'and', 'a', 'to', 'can', 'i', 'my', 'me',
    'be', 'on', 'with', 'from', 'do', 'not', 'are', 'this', 'that', 'any', 'as',
    'it', 'or', 'by', 'your', 'within', 'which', 'only', 'into'
}


def retrieve_documents(file_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """Loads all policy text files and indexes them by document name and section number."""
    documents: Dict[str, Dict[str, str]] = {}

    for path in file_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f'Policy file not found: {path}')

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        doc_name = os.path.basename(path)
        sections: Dict[str, str] = {}
        current_section = None
        buffer: List[str] = []

        for line in lines:
            stripped = line.strip()
            match = re.match(r'^(\d+\.\d+)\s+(.*)', stripped)
            if match:
                if current_section is not None:
                    sections[current_section] = ' '.join(buffer).strip()
                current_section = match.group(1)
                buffer = [match.group(2).strip()]
            elif current_section and stripped:
                buffer.append(stripped)

        if current_section is not None:
            sections[current_section] = ' '.join(buffer).strip()

        if not sections:
            raise ValueError(f'No numbered sections found in {doc_name}.')

        documents[doc_name] = sections

    return documents


def normalize_text(text: str) -> List[str]:
    normalized = re.sub(r'[^a-z0-9 ]+', ' ', text.lower())
    return [token for token in normalized.split() if token and token not in STOP_WORDS]


def score_section(query_tokens: List[str], section_text: str) -> int:
    section_tokens = set(normalize_text(section_text))
    return sum(1 for token in query_tokens if token in section_tokens)


def answer_question(question: str, documents: Dict[str, Dict[str, str]]) -> str:
    """Searches indexed documents and returns a single-source answer or the exact refusal template."""
    query_tokens = normalize_text(question)
    if not query_tokens:
        return REFUSAL_TEMPLATE

    scores: List[Tuple[str, str, int]] = []

    for doc_name, sections in documents.items():
        for section_id, section_text in sections.items():
            score = score_section(query_tokens, section_text)
            if score > 0:
                scores.append((doc_name, section_id, score))

    if not scores:
        return REFUSAL_TEMPLATE

    scores.sort(key=lambda item: item[2], reverse=True)
    top_score = scores[0][2]
    top_matches = [item for item in scores if item[2] == top_score]

    # If top score appears in multiple documents, refuse to avoid blending.
    unique_docs = {doc for doc, _, _ in top_matches}
    if len(unique_docs) > 1:
        return REFUSAL_TEMPLATE

    # If multiple sections in same doc have equal best score, choose most specific section by section number.
    top_doc = top_matches[0][0]
    top_sections = [item for item in top_matches if item[0] == top_doc]
    top_sections.sort(key=lambda item: item[1])
    selected_section = top_sections[0]
    doc_name, section_id, _ = selected_section
    section_text = documents[doc_name][section_id]

    return f"{section_text} ({doc_name}, section {section_id})"


def interactive_mode(documents: Dict[str, Dict[str, str]]):
    print('Policy Q&A CLI. Type your question or ENTER to quit.')
    while True:
        try:
            question = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting.')
            return

        if not question:
            print('Exiting.')
            return

        answer = answer_question(question, documents)
        print(answer)
        print()


def main():
    parser = argparse.ArgumentParser(description='UC-X Document Q&A')
    parser.add_argument('--docs', nargs='*', help='Optional document paths to load')
    args = parser.parse_args()

    file_paths = args.docs if args.docs else DATA_FILES
    try:
        documents = retrieve_documents(file_paths)
    except Exception as exc:
        print(f'Error loading documents: {exc}')
        sys.exit(1)

    interactive_mode(documents)

if __name__ == '__main__':
    main()
