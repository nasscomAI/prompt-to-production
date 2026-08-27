import sys
import os

# Add the current directory to path so we can import app
sys.path.append(os.getcwd())

import app

TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?"
]

def generate_output():
    indexed_docs = app.retrieve_documents(app.DOC_PATHS)
    
    with open("qa_output.txt", "w", encoding="utf-8") as f:
        f.write("UC-X Policy Document Q&A Agent - Test Results\n")
        f.write("=" * 50 + "\n\n")
        
        for i, q in enumerate(TEST_QUESTIONS, 1):
            f.write(f"Question {i}: {q}\n")
            answer = app.answer_question(q, indexed_docs)
            f.write("-" * 20 + "\n")
            f.write(answer + "\n")
            f.write("=" * 50 + "\n\n")
    
    print("Output generated in qa_output.txt")

if __name__ == "__main__":
    generate_output()
