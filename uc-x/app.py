import os

# Load documents
def load_docs():
    docs = {}
    base_path = "../data/policy-documents"

    for file in os.listdir(base_path):
        if file.endswith(".txt"):
            with open(os.path.join(base_path, file), "r", encoding="utf-8") as f:
                docs[file] = f.read().lower()
    return docs


# Refusal template
def refusal():
    return "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact relevant team for guidance."


# Simple QA logic
def answer_question(question, docs):
    q = question.lower()

    found_answers = []

    for name, text in docs.items():
        if any(word in text for word in q.split()):
            found_answers.append((name, text[:200]))

    # If nothing found → refuse
    if len(found_answers) == 0:
        return refusal()

    # If multiple docs → ambiguity → refuse
    if len(found_answers) > 1:
        return refusal()

    # Otherwise return answer
    doc_name, content = found_answers[0]

    return f"ANSWER: Based on {doc_name}\nSOURCE: {doc_name}"


# CLI
if __name__ == "__main__":
    docs = load_docs()

    print("Policy QA System (UC-X)")
    print("Type your question (or 'exit'):\n")

    while True:
        q = input("> ")

        if q.lower() == "exit":
            break

        print(answer_question(q, docs))