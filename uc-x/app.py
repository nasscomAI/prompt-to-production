import os
import argparse


def load_documents(folder_path):
    documents = {}

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            path = os.path.join(folder_path, file)
            with open(path, "r", encoding="utf-8") as f:
                documents[file] = f.read().lower()

    return documents


def answer_question(question, documents):
    question = question.lower()

    for name, content in documents.items():
        if any(word in content for word in question.split()):
            return f"Answer found in {name}:\n{content[:300]}..."

    return "Information not found in provided documents."


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    docs = load_documents("../data/policy-documents")

    result = answer_question(args.question, docs)

    print(result)