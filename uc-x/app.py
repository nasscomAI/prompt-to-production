"""
UC-X app.py — Ask My Documents
Search policy documents and return a relevant snippet.
"""

import argparse
import os


def load_documents(folder):

    docs = {}

    for file in os.listdir(folder):

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8") as f:
            docs[file] = f.read()

    return docs


def search_documents(question, docs):

    question = question.lower()

    for name, text in docs.items():

        if question.split()[0] in text.lower():

            return name, text[:400]

    return None, "No relevant information found."


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    docs = load_documents("../data/policy-documents")

    source, answer = search_documents(args.question, docs)

    print("\nSource document:", source)
    print("\nAnswer:\n", answer)


if __name__ == "__main__":
    main()