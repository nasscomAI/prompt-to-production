"""
UC-X app.py — Interactive policy Q&A.
Implements skills from uc-x/skills.md and enforcement from uc-x/agents.md.
"""
import os
import re
from typing import Dict, List

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(file_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """Loads all 3 policy files, indexes by document name and section number."""
    indexed = {}
    
    for path in file_paths:
        doc_name = os.path.basename(path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            sections = {}
            current_section = None
            current_lines = []
            for line in content.split('\n'):
                line = line.strip()
                m = re.match(r'^(\d+\.\d+)\s+(.+)', line)
                if m:
                    if current_section:
                        sections[current_section] = '\n'.join(current_lines).strip()
                    current_section = m.group(1)
                    current_lines = [m.group(2)]
                elif current_section:
                    current_lines.append(line)
            if current_section:
                sections[current_section] = '\n'.join(current_lines).strip()
            indexed[doc_name] = sections
        except Exception as e:
            print(f"Error loading {doc_name}: {e}")
            indexed[doc_name] = {}
    return indexed

def answer_question(question: str, indexed_docs: Dict[str, Dict[str, str]]) -> str:
    """Searches indexed documents, returns single-source answer + citation OR refusal template."""
    question_lower = question.lower()
    keywords = re.findall(r'\b\w+\b', question_lower)
    matches = {}
    
    for doc_name, sections in indexed_docs.items():
        best_section = None
        best_count = 0
        best_text = ""
        for section, text in sections.items():
            text_lower = text.lower()
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > best_count:
                best_count = count
                best_section = section
                best_text = text
        if best_count > 0:
            matches[doc_name] = [(best_section, best_text)]
    
    if not matches:
        return REFUSAL_TEMPLATE
    
    if len(matches) > 1:
        # Multiple docs match, refuse to avoid blending
        return REFUSAL_TEMPLATE
    
    # Single doc match
    doc_name = list(matches.keys())[0]
    doc_matches = matches[doc_name]
    # Pick the first matching section
    section, text = doc_matches[0]
    answer = f"{text}\n\nSource: {doc_name} section {section}"
    return answer

def main():
    file_paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    indexed_docs = retrieve_documents(file_paths)
    
    print("UC-X Policy Q&A. Type your question or 'quit' to exit.")
    while True:
        question = input("Question: ").strip()
        if question.lower() == 'quit':
            break
        answer = answer_question(question, indexed_docs)
        print(f"Answer: {answer}\n")

if __name__ == "__main__":
    main()
