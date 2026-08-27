"""Run UC-X test questions non-interactively."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "uc-x"))
from app import retrieve_documents, answer_question

base = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
doc_paths = [
    os.path.join(base, "policy_hr_leave.txt"),
    os.path.join(base, "policy_it_acceptable_use.txt"),
    os.path.join(base, "policy_finance_reimbursement.txt"),
]

doc_index = retrieve_documents(doc_paths)

questions = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]

print("\n" + "=" * 60)
for q in questions:
    print(f"\nQ: {q}")
    a = answer_question(q, doc_index)
    print(f"A: {a}")
    print("-" * 60)
