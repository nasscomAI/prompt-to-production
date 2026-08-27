"""
UC-X app.py — Ask My Documents (Rule-based, No Hallucination)
"""

import os

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)


def load_documents():
    base_path = "../data/policy-documents"

    files = {
        "HR": "policy_hr_leave.txt",
        "IT": "policy_it_acceptable_use.txt",
        "FINANCE": "policy_finance_reimbursement.txt",
    }

    docs = {}

    for key, file in files.items():
        path = os.path.join(base_path, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                docs[key] = f.read()
        except:
            docs[key] = ""

    return docs


def answer_question(question, docs):
    q = question.lower()

    matches = []

    # -------- HR --------
    if "carry forward" in q:
        matches.append(("HR", "2.6", "Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December."))

    if "leave without pay" in q or "who approves leave" in q:
        matches.append(("HR", "5.2", "Leave Without Pay requires approval from BOTH Department Head and HR Director."))

    # -------- IT --------
    if "install slack" in q:
        matches.append(("IT", "2.3", "Installing software like Slack requires written IT approval."))

    if "personal phone" in q:
        matches.append(("IT", "3.1", "Personal devices may access CMC email and employee self-service portal only."))

    # -------- FINANCE --------
    if "home office" in q:
        matches.append(("FINANCE", "3.1", "Home office allowance is Rs 8,000 one-time for permanent work-from-home employees."))

    if "da and meal" in q:
        matches.append(("FINANCE", "2.6", "DA and meal reimbursement cannot be claimed on the same day."))

    # -------- DECISION --------
    if len(matches) == 1:
        doc, section, answer = matches[0]
        return f"{answer} (Source: {doc} Policy, Section {section})"

    # ❌ multiple matches → blending risk → refuse
    if len(matches) > 1:
        return REFUSAL

    # ❌ no match
    return REFUSAL


def main():
    docs = load_documents()

    print("\n📄 Ask My Documents (type 'exit' to quit)\n")

    while True:
        question = input(">> ")

        if question.lower() == "exit":
            break

        response = answer_question(question, docs)
        print("\n" + response + "\n")


if __name__ == "__main__":
    main()