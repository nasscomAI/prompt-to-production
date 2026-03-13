import os
import argparse


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact the relevant "
    "team for guidance."
)


def retrieve_documents():

    base = "data/policy-documents"

    docs = {}

    for file in [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]:

        path = os.path.join(base, file)

        with open(path, "r", encoding="utf-8") as f:
            docs[file] = f.read()

    return docs


def answer_question(question, docs):

    q = question.lower()
    keywords = q.split()

    best_match = None
    best_score = 0
    best_doc = None

    for doc_name, text in docs.items():

        lines = text.split("\n")

        for line in lines:

            line = line.strip()
            line_lower = line.lower()

            # Only consider lines that look like policy clauses (e.g., "2.6 ...")
            if not line or not line[0].isdigit():
                continue

            score = sum(1 for k in keywords if k in line_lower)

            if score > best_score:
                best_score = score
                best_match = line
                best_doc = doc_name

    if best_match:
        return f"{best_match} (Source: {best_doc})"

    return REFUSAL_TEMPLATE

def main():

    docs = retrieve_documents()

    print("Policy Q&A system. Type 'exit' to quit.\n")

    while True:

        question = input("Ask a question: ")

        if question.lower() in ["exit", "quit"]:
            break

        answer = answer_question(question, docs)

        print("\nAnswer:")
        print(answer)
        print()


if __name__ == "__main__":
    main()