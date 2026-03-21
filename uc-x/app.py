"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

# Load documents
def load_doc(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_sections(text):
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    return re.findall(pattern, text, re.DOTALL)

# Load all documents
docs = {
    "policy_hr_leave.txt": extract_sections(load_doc("../data/policy-documents/policy_hr_leave.txt")),
    "policy_it_acceptable_use.txt": extract_sections(load_doc("../data/policy-documents/policy_it_acceptable_use.txt")),
    "policy_finance_reimbursement.txt": extract_sections(load_doc("../data/policy-documents/policy_finance_reimbursement.txt"))
}

REFUSAL = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the relevant team for guidance."

def search(question):
    q = question.lower()

    for doc_name, sections in docs.items():
        for num, content in sections:
            if any(word in content.lower() for word in q.split()):
                return f"{content.strip()} (Source: {doc_name} Section {num})"

    return REFUSAL


def main():
    print("Ask your question (type 'exit' to quit):")

    while True:
        q = input(">> ")

        if q.lower() == "exit":
            break

        answer = search(q)
        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()
