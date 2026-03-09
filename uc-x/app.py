import argparse
import os

def load_documents(folder_path):
    documents = {}

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                documents[file] = f.read()

    return documents


def ask_documents(documents, query):

    results = []

    query = query.lower()

    for name, text in documents.items():
        if query in text.lower():
            results.append((name, text))

    return results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--query", required=True)

    args = parser.parse_args()

    docs = load_documents("../data/policy-documents")

    results = ask_documents(docs, args.query)

    if results:
        for name, text in results:
            print(f"\nFound in {name}\n")
            print(text[:500])
    else:
        print("No matching document found.")


if __name__ == "__main__":
    main()