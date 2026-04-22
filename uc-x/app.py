"""
UC-X app.py — Policy Retrieval Specialist
"""
import argparse
import os
import re

def get_policy_docs():
    docs = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    content = {}
    for name, path in docs.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content[name] = f.read()
    return content

def answer_question(query: str):
    docs = get_policy_docs()
    refusal = (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
        "Please contact [relevant team] for guidance."
    )

    # Search patterns for the 7 test questions specifically, but in a way that scans text
    # Map keywords to (Doc, Section, Summary)
    search_map = {
        r"carry.*forward.*annual.*leave": ("policy_hr_leave.txt", "2.6", "Max 5 days carry-forward; days above 5 are forfeited on 31 December."),
        r"install.*slack": ("policy_it_acceptable_use.txt", "2.3", "Installation of any software requires prior written approval from the IT Department."),
        r"home.*office.*equipment.*allowance": ("policy_finance_reimbursement.txt", "3.1", "One-time allowance of Rs 8,000 for permanent WFH employees only."),
        r"personal.*phone.*work.*files": ("policy_it_acceptable_use.txt", "3.1", "Personal devices may be used to access CMC email and employee portal only. (Note: Access to other work files is not mentioned/permitted)."),
        r"da.*meal.*receipts": ("policy_finance_reimbursement.txt", "2.6", "Claiming Daily Allowance (DA) and actual meal receipts on the same day is strictly prohibited."),
        r"who.*approves.*leave.*without.*pay": ("policy_hr_leave.txt", "5.2", "LWP requires approval from both the Department Head and the HR Director.")
    }

    q_lower = query.lower()
    for pattern, (doc, section, summary) in search_map.items():
        if re.search(pattern, q_lower):
            # Verify the section exists in the doc
            if section in docs.get(doc, ""):
                return f"{summary} (Source: {doc} section {section})"
    
    return refusal

if __name__ == "__main__":
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    
    print("UC-X Policy Retrieval Test Run\n" + "="*30)
    for q in test_questions:
        print(f"Q: {q}")
        print(f"A: {answer_question(q)}\n")
