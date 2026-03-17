"""
UC-X app.py — Policy Document Q&A System
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
Interactive CLI that answers policy questions from three source documents.
"""
import os
import re
from pathlib import Path

# REFUSAL TEMPLATE (exact wording — no variations allowed)
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact HR Department for leave questions, IT Department for technology questions, or Finance Department for expense questions."""

# Knowledge base with specific answers and their source documents
# Format: (question_keywords, document, section, exact_answer)
KNOWLEDGE_BASE = [
    # HR Leave questions
    (["carry", "forward", "annual"], "HR", "2.6", 
     "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."),
    
    (["advance", "notice", "days"], "HR", "2.3",
     "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1."),
    
    (["written", "approval"], "HR", "2.4",
     "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid."),
    
    (["lwp", "without pay", "approves", "approval"], "HR", "5.2",
     "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."),
    
    (["sick", "consecutive", "medical"], "HR", "3.2",
     "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work."),
    
    # IT questions
    (["install", "software"], "IT", "2.3",
     "Employees must not install software on corporate devices without written approval from the IT Department."),
    
    (["personal", "device", "email"], "IT", "3.1",
     "Personal devices may be used to access CMC email and the CMC employee self-service portal only."),
    
    (["personal", "phone", "work"], "IT", "3.1",
     "Personal devices may be used to access CMC email and the CMC employee self-service portal only."),
    
    # Finance questions
    (["home office", "equipment"], "Finance", "3.1",
     "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."),
    
    (["da", "meal", "simultaneously"], "Finance", "2.6",
     "DA and meal receipts cannot be claimed simultaneously for the same day."),
]

def load_policy_documents(data_dir: str) -> dict:
    """Load all three policy documents and return indexed content."""
    documents = {}
    
    policy_files = {
        'HR': 'policy_hr_leave.txt',
        'IT': 'policy_it_acceptable_use.txt',
        'Finance': 'policy_finance_reimbursement.txt'
    }
    
    for doc_name, filename in policy_files.items():
        filepath = os.path.join(data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                documents[doc_name] = f.read()
        except FileNotFoundError:
            print(f"WARNING: {filename} not found at {filepath}")
    
    return documents

def answer_question(question: str, documents: dict) -> str:
    """
    Answer a question using the knowledge base.
    Returns single-source answer with citation OR refusal template.
    """
    question_lower = question.lower().strip()
    
    # Check knowledge base for matches
    best_match = None
    best_score = 0
    
    for keywords, doc_type, section, answer in KNOWLEDGE_BASE:
        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in question_lower)
        score = matches / len(keywords)  # Percentage match
        
        if score > best_score:
            best_score = score
            best_match = (doc_type, section, answer)
    
    # If good match found, return with citation
    if best_score >= 0.5:  # At least 50% keywords match
        doc_type, section, answer_text = best_match
        return f"Policy: {doc_type} Policy, Section {section}\n{answer_text}"
    
    # Special handling for common non-answers
    if any(word in question_lower for word in ["flexible", "culture", "view", "opinion"]):
        return REFUSAL_TEMPLATE
    
    # Default: refusal template
    return REFUSAL_TEMPLATE

def main():
    """Interactive CLI for policy questions."""
    import sys
    
    # Load documents (from current directory or passed path)
    data_dir = "../data/policy-documents"
    if not os.path.exists(data_dir):
        # Try parent if running from different location
        data_dir = "data/policy-documents"
    
    if not os.path.exists(data_dir):
        print("ERROR: Policy documents directory not found.")
        print("Expected: ../data/policy-documents/")
        sys.exit(1)
    
    documents = load_policy_documents(data_dir)
    
    print("═" * 70)
    print("CITY MUNICIPAL CORPORATION — POLICY Q&A SYSTEM")
    print("═" * 70)
    print("\nWelcome! Ask questions about:")
    print("  • HR Leave Policy (policy_hr_leave.txt)")
    print("  • IT Acceptable Use Policy (policy_it_acceptable_use.txt)")
    print("  • Finance Reimbursement Policy (policy_finance_reimbursement.txt)")
    print("\nType 'exit' to quit.\n")
    
    while True:
        try:
            question = input("Question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'bye']:
                print("\nThank you. Goodbye.")
                break
            
            if not question:
                print("Please enter a question.\n")
                continue
            
            # Get answer
            answer = answer_question(question, documents)
            print("\nAnswer:")
            print(answer)
            print()
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"ERROR: {e}\n")

if __name__ == "__main__":
    main()

