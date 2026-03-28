"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(paths):
    docs = {}
    for path in paths:
        with open(path, 'r') as f:
            content = f.read()
        sections = re.findall(r'(Section \d+\.\d+)[\s:-]+(.*?)\n', content, re.DOTALL)
        docs[path] = {num: text.strip() for num, text in sections}
    return docs

def answer_question(question, docs):
    for doc_name, sections in docs.items():
        for section, text in sections.items():
            if question.lower() in text.lower():
                return f"{text} (Source: {doc_name}, {section})"
    return REFUSAL_TEMPLATE

def main():
    import sys
    doc_paths = sys.argv[1:4]
    docs = retrieve_documents(doc_paths)
    while True:
        question = input("Ask a question: ")
        answer = answer_question(question, docs)
        print(answer)

if __name__ == "__main__":
    main()
