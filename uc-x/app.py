"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)


def load_documents():

    docs = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_dir, "..", "data", "policy-documents")

    for filename in os.listdir(folder):

        path = os.path.join(folder, filename)

        with open(path, "r", encoding="utf-8") as file:
            docs[filename] = file.read()

    return docs


def answer_question(question, documents):

    question = question.lower()

    for name, content in documents.items():

        if any(word in content.lower() for word in question.split()):

            return f"Source: {name}\n\n{content[:500]}..."

    return REFUSAL


def main():

    parser = argparse.ArgumentParser()

    parser.parse_args()

    documents = load_documents()

    print("Ask questions about the policy documents.")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("Question: ")

        if question.lower() == "exit":
            break

        print()
        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()