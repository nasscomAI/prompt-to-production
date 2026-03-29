"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os

def retrieve_documents():
    files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]

    documents = ""

    for file_path in files:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found")

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            documents += f.read() + "\n"

    return documents


def answer_question(documents, question):
    question_lower = question.lower()
    doc_lower = documents.lower()

    keywords = question_lower.split()

    matches = []
    for line in documents.split('\n'):
        if any(word in line.lower() for word in keywords):
            matches.append(line.strip())

    if not matches:
        return "❌ Cannot answer from provided documents."

    # return top relevant lines
    return "\n".join(matches[:3])


def main():
    try:
        docs = retrieve_documents()
        print("📄 Documents loaded successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

    while True:
        question = input("\nAsk a question (type 'exit' to quit): ")

        if question.lower() == "exit":
            print("Exiting...")
            break

        answer = answer_question(docs, question)
        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()
    
