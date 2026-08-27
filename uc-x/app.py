import os

DOCS_DIR = "../data/policy-documents/"

DOCUMENTS = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy"
}

QUESTIONS = [
    "How many days of annual leave are employees entitled to?",
    "Can employees use personal phones for work purposes?",
    "What is the reimbursement limit for travel expenses?",
    "Who approves leave requests?",
    "What happens if an employee violates the IT policy?",
    "How do I claim medical reimbursement?"
]

def load_documents(docs_dir):
    loaded = {}
    for filename in DOCUMENTS:
        filepath = os.path.join(docs_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded[filename] = f.read()
        except FileNotFoundError:
            print(f"WARNING: {filename} not found")
            loaded[filename] = ""
    return loaded

def identify_source(question, docs):
    q = question.lower()
    if any(w in q for w in ["leave", "annual", "sick", "holiday", "approve", "days off"]):
        return "policy_hr_leave.txt"
    if any(w in q for w in ["phone", "device", "internet", "it policy", "computer", "software", "violate"]):
        return "policy_it_acceptable_use.txt"
    if any(w in q for w in ["reimburse", "expense", "travel", "claim", "medical", "receipt"]):
        return "policy_finance_reimbursement.txt"
    return None

def search_answer(question, doc_content):
    q_words = question.lower().split()
    lines = doc_content.split('\n')
    best_line = ""
    best_score = 0
    for line in lines:
        if len(line.strip()) < 10:
            continue
        score = sum(1 for w in q_words if w in line.lower())
        if score > best_score:
            best_score = score
            best_line = line.strip()
    if best_score >= 2:
        return best_line
    return None

def answer_question(question, docs):
    source = identify_source(question, docs)
    if source is None:
        return {
            "question": question,
            "answer": "CANNOT ANSWER: This information is not found in the provided documents",
            "source": "None"
        }
    doc_content = docs[source]
    answer = search_answer(question, doc_content)
    if answer is None:
        return {
            "question": question,
            "answer": "CANNOT ANSWER: This information is not found in the provided documents",
            "source": source
        }
    return {
        "question": question,
        "answer": answer,
        "source": source
    }

def main():
    print("Loading documents...")
    docs = load_documents(DOCS_DIR)
    print(f"Loaded {len(docs)} documents\n")
    print("=" * 60)
    for question in QUESTIONS:
        result = answer_question(question, docs)
        print(f"Q: {result['question']}")
        print(f"A: {result['answer']}")
        print(f"Source: {result['source']}")
        print("-" * 60)

if __name__ == "__main__":
    main()