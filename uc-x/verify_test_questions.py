from app import retrieve_documents, answer_question, REFUSAL_TEMPLATE

TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?"
]

def run_tests():
    indexed_docs = retrieve_documents()
    print("--- UC-X Policy Q&A Verification ---")
    
    for i, q in enumerate(TEST_QUESTIONS, 1):
        print(f"Q{i}: {q}")
        response = answer_question(q, indexed_docs)
        print(f"A{i}: {response}")
        print("-" * 40)

if __name__ == "__main__":
    run_tests()
