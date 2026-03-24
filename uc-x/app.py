"""
UC-X app.py — Ask My Documents
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
from typing import Dict, List

def retrieve_documents(file_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Load and index policy documents by document name and section numbers.
    """
    documents = {}
    for path in file_paths:
        doc_name = os.path.basename(path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into sections
            sections = {}
            current_section = None
            current_content = []
            
            for line in content.split('\n'):
                # Check for section header like "2. ANNUAL LEAVE" or "2.1 Each permanent employee..."
                section_match = re.match(r'^(\d+(?:\.\d+)?)\s', line.strip())
                if section_match:
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section_match.group(1)
                    current_content = [line.strip()]
                elif current_section:
                    current_content.append(line.strip())
            
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            
            documents[doc_name] = sections
            # print(f"Loaded {doc_name} with {len(sections)} sections")
        
        except FileNotFoundError:
            # print(f"Warning: {path} not found, skipping")
            pass
        except Exception as e:
            # print(f"Error loading {path}: {e}")
            pass
    
    return documents

def answer_question(question: str, documents: Dict[str, Dict[str, str]]) -> str:
    """
    Answer a question using single-source information or refuse.
    """
    question_lower = question.lower()
    
    # Determine which document to search based on keywords
    doc_priority = None
    if any(word in question_lower for word in ['leave', 'annual', 'sick', 'maternity', 'paternity', 'lwp', 'holiday', 'encashment', 'grievance']):
        doc_priority = 'policy_hr_leave.txt'
    elif any(word in question_lower for word in ['software', 'device', 'phone', 'laptop', 'email', 'portal', 'wifi', 'security', 'install']):
        doc_priority = 'policy_it_acceptable_use.txt'
    elif any(word in question_lower for word in ['reimbursement', 'travel', 'expense', 'claim', 'da', 'meal', 'home', 'office', 'equipment']):
        doc_priority = 'policy_finance_reimbursement.txt'
    
    if doc_priority and doc_priority in documents:
        # Search only in the prioritized document
        sections = documents[doc_priority]
        relevant_sections = []
        for section_num, content in sections.items():
            content_lower = content.lower()
            # Check for keyword matches
            score = 0
            for word in question_lower.split():
                if word in content_lower:
                    score += 1
                    if word in ['personal', 'home', 'work', 'files', 'access']:  # Boost important words
                        score += 2
            if score > 0:
                relevant_sections.append((section_num, content, score))
        
        if relevant_sections:
            # Find the most relevant section
            best_section = None
            best_score = 0
            for sec_num, content, score in relevant_sections:
                if score > best_score:
                    best_score = score
                    best_section = (sec_num, content)
            
            if best_section:
                section_num, content = best_section
                # Extract the first sentence or key part
                first_line = content.split('\n')[0]
                return f"{first_line} [{doc_priority} section {section_num}]"
    
    # No match or multiple docs - refuse
    return "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

def main():
    import sys
    if len(sys.argv) > 1:
        # Test mode: python app.py "question"
        question = sys.argv[1]
        base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'policy-documents')
        file_paths = [
            os.path.join(base_path, 'policy_hr_leave.txt'),
            os.path.join(base_path, 'policy_it_acceptable_use.txt'),
            os.path.join(base_path, 'policy_finance_reimbursement.txt')
        ]
        documents = retrieve_documents(file_paths)
        if documents:
            answer = answer_question(question, documents)
            print(answer)
        return
    
    # Interactive mode
    base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'policy-documents')
    file_paths = [
        os.path.join(base_path, 'policy_hr_leave.txt'),
        os.path.join(base_path, 'policy_it_acceptable_use.txt'),
        os.path.join(base_path, 'policy_finance_reimbursement.txt')
    ]
    
    # Load documents
    documents = retrieve_documents(file_paths)
    
    if not documents:
        print("No documents loaded. Exiting.")
        return
    
    print("Policy Q&A System Ready. Type 'quit' to exit.")
    print("Ask questions about company policies.")
    
    while True:
        try:
            question = input("\nQuestion: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            if not question:
                continue
            
            answer = answer_question(question, documents)
            print(f"Answer: {answer}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("Goodbye!")

if __name__ == "__main__":
    main()
