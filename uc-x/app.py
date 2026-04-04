import argparse
import os


def load_documents(folder_path):
    docs = {}

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                docs[file] = f.read().lower()

    return docs


def search_documents(query, docs):
    query = query.lower()

    for name, text in docs.items():
        if query in text:
            return f"Answer found in {name}"

    return "INFORMATION_NOT_FOUND"


def main(doc_folder, question):

    documents = load_documents(doc_folder)

    answer = search_documents(question, documents)

    print("Question:", question)
    print("Answer:", answer)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")

    parser.add_argument("--docs", required=True)
    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    main(args.docs, args.question)