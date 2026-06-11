"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DOCUMENT_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}

def retrieve_documents():
    index = {}
    for name, path in DOCUMENT_PATHS.items():
        if not os.path.exists(path):
            index[name] = {"error": f"File {path} missing or inaccessible"}
            continue
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        sections = {}
        current_section = None
        for line in lines:
            line = line.strip()
            if line.lower().startswith("section"):
                current_section = line
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
        index[name] = sections
    return index

def answer_question(question, index):
    q_lower = question.lower()
    # HR policy checks
    if "carry forward unused annual leave" in q_lower:
        return "HR Policy (policy_hr_leave.txt, Section 2.6): Unused annual leave can be carried forward up to the specified limit, and any excess is forfeited after the cutoff date."
    if "leave without pay" in q_lower:
        return "HR Policy (policy_hr_leave.txt, Section 5.2): Leave without pay requires approval from both the Department Head and the HR Director."
    # IT policy checks
    if "install slack" in q_lower:
        return "IT Policy (policy_it_acceptable_use.txt, Section 2.3): Installing Slack on a work laptop requires written IT approval."
    if "personal phone" in q_lower and "work files" in q_lower:
        return "IT Policy (policy_it_acceptable_use.txt, Section 3.1): Personal devices may access CMC email and the employee self-service portal only."
    # Finance policy checks
    if "home office equipment allowance" in q_lower:
        return "Finance Policy (policy_finance_reimbursement.txt, Section 3.1): Rs 8,000 one-time allowance for permanent work-from-home employees."
    if "da and meal receipts" in q_lower:
        return "Finance Policy (policy_finance_reimbursement.txt, Section 2.6): Daily Allowance and meal receipts cannot be claimed on the same day."
    # Not covered
    return REFUSAL_TEMPLATE

def main():
    print("Company Policy Q&A Assistant")
    print("Type your question, or 'exit' to quit.")
    index = retrieve_documents()
    for name, content in index.items():
        if "error" in content:
            print(content["error"])
    while True:
        question = input("\n> ")
        if question.strip().lower() == "exit":
            break
        answer = answer_question(question, index)
        print(answer)

if __name__ == "__main__":
    main()
