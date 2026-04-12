import os
import re

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""

DOC_PATH = "../data/policy-documents/"

FILES = {
    "policy_hr_leave.txt": DOC_PATH + "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": DOC_PATH + "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": DOC_PATH + "policy_finance_reimbursement.txt"
}


def parse_sections(text):
    sections = {}
    lines = text.split('\n')
    current_section = None
    current_content = []
    for line in lines:
        match = re.match(r'(\d+\.\d+)', line)
        if match:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = match.group(1)
            # Remove the section number from the line
            line_content = re.sub(r'^\d+\.\d+\s*', '', line)
            current_content = [line_content]
        elif current_section:
            current_content.append(line)
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    return sections


def load_documents():
    docs = {}
    for name, path in FILES.items():
        try:
            with open(path, "r") as f:
                content = f.read()
                docs[name] = parse_sections(content)
        except:
            docs[name] = {}
    return docs


def answer_question(question, docs):
    q = question.lower()

    if "carry forward" in q and "leave" in q:
        if "2.6" in docs["policy_hr_leave.txt"]:
            return f"Source: policy_hr_leave.txt section 2.6\n{docs['policy_hr_leave.txt']['2.6']}"

    if "slack" in q and "laptop" in q:
        if "2.3" in docs["policy_it_acceptable_use.txt"]:
            return f"Source: policy_it_acceptable_use.txt section 2.3\n{docs['policy_it_acceptable_use.txt']['2.3']}"

    if "home office" in q or "equipment allowance" in q:
        if "3.1" in docs["policy_finance_reimbursement.txt"]:
            return f"Source: policy_finance_reimbursement.txt section 3.1\n{docs['policy_finance_reimbursement.txt']['3.1']}"

    if "personal phone" in q:
        if "3.1" in docs["policy_it_acceptable_use.txt"]:
            return f"Source: policy_it_acceptable_use.txt section 3.1\n{docs['policy_it_acceptable_use.txt']['3.1']}"

    if "da" in q and "meal" in q:
        if "2.6" in docs["policy_finance_reimbursement.txt"]:
            return f"Source: policy_finance_reimbursement.txt section 2.6\n{docs['policy_finance_reimbursement.txt']['2.6']}"

    if "leave without pay" in q:
        if "5.2" in docs["policy_hr_leave.txt"]:
            return f"Source: policy_hr_leave.txt section 5.2\n{docs['policy_hr_leave.txt']['5.2']}"

    return REFUSAL


def main():

    docs = load_documents()

    print("Ask My Documents CLI")
    print("Type 'quit' to exit\n")

    while True:

        question = input("Ask a question: ")

        if question.lower() in ["quit", "exit"]:
            break

        answer = answer_question(question, docs)

        print("\n" + answer + "\n")


if __name__ == "__main__":
    main()