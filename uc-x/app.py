"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os

def main():

    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", required=True, help="Folder containing documents")
    parser.add_argument("--question", required=True, help="Question to ask")

    args = parser.parse_args()

    documents = []

    for filename in os.listdir(args.docs):
        path = os.path.join(args.docs, filename)

        with open(path, "r", encoding="utf-8") as f:
            documents.append(f.read())

    question = args.question.lower()

    answer = "No answer found."

    for doc in documents:
        for line in doc.split("\n"):
            if question in line.lower():
                answer = line.strip()
                break

    print("Answer:", answer)

if __name__ == "__main__":
    main()
