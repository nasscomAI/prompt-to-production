from app import retrieve_documents, answer_question

def verify():
    index = retrieve_documents()
    questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone to access work files when working from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    
    print("UC-X VERIFICATION RESULTS")
    print("=" * 50)
    
    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q}")
        ans = answer_question(q, index)
        print(f"A: {ans}")
        print("-" * 50)

if __name__ == "__main__":
    verify()
