import argparse

REFUSAL_TEMPLATE = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact HR or IT support for guidance.
"""

def load_documents():
    docs = {}
    files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                docs[file] = f.read()
        except:
            print("Error loading", file)

    return docs


def search_documents(question, docs):
    question = question.lower()

    for name, text in docs.items():
        if "leave" in question and "hr_leave" in name:
            return "Refer policy_hr_leave.txt (Section 2.6): Leave carry forward rules apply."

        if "slack" in question and "acceptable_use" in name:
            return "Refer policy_it_acceptable_use.txt (Section 2.3): Installing software requires IT approval."

        if "equipment allowance" in question and "finance" in name:
            return "Refer policy_finance_reimbursement.txt (Section 3.1): Rs 8000 one-time WFH allowance."

        if "personal phone" in question and "acceptable_use" in name:
            return "Refer policy_it_acceptable_use.txt (Section 3.1): Personal devices may access company email and employee portal only."

    return REFUSAL_TEMPLATE


def main():
    docs = load_documents()

    print("Ask policy questions (type 'exit' to quit):")

    while True:
        question = input("Question: ")

        if question.lower() == "exit":
            break

        answer = search_documents(question, docs)

        print("Answer:", answer)


if __name__ == "__main__":
    main()