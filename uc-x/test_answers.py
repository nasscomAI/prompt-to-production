from app import retrieve_documents, answer_question

def run_tests():
    docs = retrieve_documents()
    questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    
    for i, q in enumerate(questions, 1):
        print(f"\nTEST {i}: {q}")
        print("ANSWER:")
        print(answer_question(q, docs))
        print("-" * 20)

if __name__ == "__main__":
    run_tests()
