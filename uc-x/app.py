import os

DATA_PATH = "../data/policy-documents/"


def load_documents():
    """Load all policy documents into memory."""
    docs = {}
    for file in os.listdir(DATA_PATH):
        path = os.path.join(DATA_PATH, file)
        with open(path, "r", encoding="utf-8") as f:
            docs[file] = f.read().lower()
    return docs


def retrieve_document(question, docs):
    """Find the most relevant document based on keywords."""
    question = question.lower()

    for name, content in docs.items():
        if any(word in content for word in question.split()):
            return name, content

    return None, None


def answer_question(question, content):
    """Extract answer from document."""
    if not content:
        return "Not found in documents"

    for line in content.split("\n"):
        if any(word in line for word in question.lower().split()):
            return line.strip()

    return "Not found in documents"


def main():
    docs = load_documents()

    print("Ask a question (type 'exit' to quit):")

    while True:
        question = input(">> ")

        if question.lower() == "exit":
            break

        doc_name, content = retrieve_document(question, docs)
        answer = answer_question(question, content)

        if doc_name:
            print(f"[Source: {doc_name}]")

        print(answer)
        print()


if __name__ == "__main__":
    main()