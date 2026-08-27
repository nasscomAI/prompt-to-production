"""
UC-X — Ask My Documents
Simple document question-answer system for policy files.
"""

import os

DOC_FOLDER = "../data/policy-documents"


def load_documents():
    docs = {}

    for filename in os.listdir(DOC_FOLDER):
        path = os.path.join(DOC_FOLDER, filename)

        if filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                docs[filename] = f.read().lower()

    return docs


def search_documents(question, documents):
    question = question.lower()

    for name, text in documents.items():
        if any(word in text for word in question.split()):
            return name, text[:400]

    return None, "No relevant policy found."


def main():

    documents = load_documents()

    question = input("Ask a question about company policies: ")

    source, answer = search_documents(question, documents)

    if source:
        print("\nAnswer found in:", source)
        print(answer)
    else:
        print(answer)


if __name__ == "__main__":
    main()