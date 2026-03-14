"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os

def answer_policy_question(question: str) -> str:
    """
    Takes a user question and provides an answer based solely on the content of the policy documents, using direct quotes or the refusal template if not covered.
    """
    base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'policy-documents')
    docs = {}
    doc_names = ['policy_hr_leave.txt', 'policy_it_acceptable_use.txt', 'policy_finance_reimbursement.txt']
    for doc in doc_names:
        path = os.path.join(base_path, doc)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                docs[doc] = f.read()
        except FileNotFoundError:
            docs[doc] = ''
    
    question_lower = question.lower()
    for doc_name, content in docs.items():
        content_lower = content.lower()
        if question_lower in content_lower:
            # Find a snippet
            start = content_lower.find(question_lower)
            snippet = content[start-100:start+200] if start > 100 else content[:300]
            return f"From {doc_name}: {snippet.strip()}"
    
    return "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

def main():
    print("Policy Q&A System. Type 'exit' to quit.")
    while True:
        question = input("Question: ").strip()
        if question.lower() == 'exit':
            break
        answer = answer_policy_question(question)
        print(answer)
        print()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
