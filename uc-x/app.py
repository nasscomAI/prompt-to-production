"""
UC-X app.py — Ask My Documents
Answers a question using a single policy document.
"""

import argparse
import os


def load_document(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def find_answer(question, doc_text):
    q = question.lower()
    lines = doc_text.split("\n")

    for line in lines:
        if any(word in line.lower() for word in q.split()):
            return line.strip()

    return None


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", required=True, help="Question to ask")
    parser.add_argument(
        "--doc",
        default="../data/policy-documents/policy_hr_leave.txt",
        help="Policy document path",
    )

    args = parser.parse_args()

    if not os.path.exists(args.doc):
        print("Document not found.")
        return

    document = load_document(args.doc)

    answer = find_answer(args.question, document)

    if answer:
        print("Answer:", answer)
        print(f"(Source: {args.doc})")
    else:
        print("Refusal: The answer cannot be found in the provided document.")


if __name__ == "__main__":
    main()