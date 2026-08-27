"""
UC-X app.py — Ask My Documents
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import argparse
from typing import Dict, List

def retrieve_documents(file_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Loads all 3 policy files and indexes them by document name and section number.
    """
    indexed_docs = {}
    for file_path in file_paths:
        doc_name = os.path.basename(file_path).replace('.txt', '')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Policy document not found: {file_path}")
        
        # Parse sections: assume sections are marked like "1.1 Title" or similar
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        for line in lines:
            # Match section headers like "1.1", "2.3", etc.
            match = re.match(r'^(\d+\.\d+)\s*(.*)', line.strip())
            if match:
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = match.group(1)
                current_content = [match.group(2)] if match.group(2) else []
            else:
                if current_section:
                    current_content.append(line)
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        indexed_docs[doc_name] = sections
    return indexed_docs

def answer_question(indexed_docs: Dict[str, Dict[str, str]], question: str) -> str:
    """
    Searches the indexed documents for an answer to a question, returning a single-source answer with citation or the refusal template if not covered.
    """
    refusal_template = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [AskHR@abcd.com] for guidance."""
    
    # Simple keyword search: split question into words, exclude stop words
    stop_words = {'what', 'is', 'the', 'a', 'an', 'of', 'to', 'for', 'in', 'on', 'at', 'by', 'with', 'as', 'and', 'or', 'but', 'if', 'then', 'than', 'so', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'how', 'when', 'where', 'why', 'who', 'which', 'that', 'this', 'these', 'those', 'be', 'am', 'are', 'was', 'were', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'i', 'me', 'my', 'mine', 'you', 'your', 'yours', 'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'we', 'us', 'our', 'ours', 'they', 'them', 'their', 'theirs'}
    keywords = [word for word in re.findall(r'\b\w+\b', question.lower()) if word not in stop_words and len(word) > 2]
    if not keywords:
        return refusal_template
    
    relevant_sections = []
    
    for doc_name, sections in indexed_docs.items():
        for section_num, content in sections.items():
            content_lower = content.lower()
            count = sum(1 for keyword in keywords if keyword in content_lower)
            # Bonus for approval if question has approves
            if 'approves' in question.lower() and 'approval' in content_lower:
                count += 10
            if count > 0:
                relevant_sections.append((count, doc_name, section_num, content))
    
    if not relevant_sections:
        return refusal_template
    
    # Sort by count descending
    relevant_sections.sort(key=lambda x: x[0], reverse=True)
    
    # Take the top
    top_count, doc_name, section_num, content = relevant_sections[0]
    
    # Check if multiple docs have the top count
    docs_with_top_count = set(d for c, d, s, co in relevant_sections if c == top_count)
    if len(docs_with_top_count) > 1:
        return refusal_template
    
    # Single doc with highest count
    answer = f"{content}\n\nSource: {doc_name}.txt section {section_num}"
    return answer

def main():
    parser = argparse.ArgumentParser(description="Ask questions about company policy.")
    parser.add_argument('question', nargs='*', help="The question to ask")
    args = parser.parse_args()
    
    file_paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    
    if args.question:
        question = ' '.join(args.question)
        try:
            indexed_docs = retrieve_documents(file_paths)
            answer = answer_question(indexed_docs, question)
            print(answer)
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Interactive mode
        try:
            indexed_docs = retrieve_documents(file_paths)
            print("Policy documents loaded. Ask your questions (type 'quit' to exit):")
            while True:
                question = input("Question: ").strip()
                if question.lower() == 'quit':
                    break
                answer = answer_question(indexed_docs, question)
                print(answer)
                print("-" * 50)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
