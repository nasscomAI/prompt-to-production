"""
UC-X app.py — Policy Question Answerer
Implemented using agents.md and skills.md.
"""
import os
import re

def retrieve_documents(file_paths: list) -> dict:
    """
    Loads all 3 policy files, indexes by document name and section number.
    Returns: {'doc_name': {'section': 'text', ...}, ...}
    """
    documents = {}
    for path in file_paths:
        doc_name = os.path.basename(path)
        sections = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                current_section = None
                current_text = []
                for line in f:
                    line = line.strip()
                    if line and line[0].isdigit() and len(line) > 2 and line[1] == '.' and line[2].isdigit():
                        if current_section:
                            sections[current_section] = ' '.join(current_text).strip()
                        parts = line.split(' ', 1)
                        current_section = parts[0]
                        current_text = [parts[1] if len(parts) > 1 else '']
                    elif current_section:
                        current_text.append(line)
                if current_section:
                    sections[current_section] = ' '.join(current_text).strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Document {path} not found")
        documents[doc_name] = sections
    return documents

def answer_question(question: str, documents: dict) -> str:
    """
    Searches indexed documents, returns single-source answer + citation OR refusal.
    """
    question_lower = question.lower()
    question_words = [re.sub(r'[^\w]', '', word) for word in question_lower.split() if len(word) > 2]
    matches = []
    
    print(f"Documents: {len(documents)}")
    for doc_name, sections in documents.items():
        print(f"Doc: {doc_name}, sections: {len(sections)}")
        for sec_num, text in sections.items():
            text_lower = text.lower()
            match_count = sum(1 for word in question_words if word in text_lower)
            if match_count > 0:
                matches.append((match_count, doc_name, sec_num, text))
    
    print(f"Matches: {len(matches)}")
    if matches:
        # Sort by match_count descending
        matches.sort(reverse=True)
        best_match = matches[0]
        match_count, doc, sec, text = best_match
        return f"According to {doc} section {sec}: {text}"
    else:
        refusal = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
        return refusal

def main():
    file_paths = [
        '../data/policy-documents/policy_hr_leave.txt',
        '../data/policy-documents/policy_it_acceptable_use.txt',
        '../data/policy-documents/policy_finance_reimbursement.txt'
    ]
    
    documents = retrieve_documents(file_paths)
    
    print("Policy Question Answerer")
    print("Ask questions about company policies. Type 'quit' to exit.")
    
    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() == 'quit':
            break
        answer = answer_question(question, documents)
        print(f"Answer: {answer}")

if __name__ == "__main__":
    main()
