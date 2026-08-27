import os


def load_documents(folder):
    docs = {}

    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                docs[filename] = f.read().lower()

    return docs


def ask_question(question, docs):

    question = question.lower()

    for name, text in docs.items():
        if any(word in text for word in question.split()):
            return f"Answer found in {name}"

    return "Information not found in documents"


if __name__ == "__main__":

    docs = load_documents("../data/policy-documents")

    question = input("Ask a question: ")

    answer = ask_question(question, docs)

    print(answer)
