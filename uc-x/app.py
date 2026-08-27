import re

DOCUMENTS = {
    'policy_hr_leave.txt': "",
    'policy_it_acceptable_use.txt': "",
    'policy_finance_reimbursement.txt': ""
}

KEYWORDS = {
    'carry forward': ('policy_hr_leave.txt', '2.6', 'Max 5 days, forfeited Dec 31'),
    'annual leave': ('policy_hr_leave.txt', '2.6', 'Max 5 days carry-forward, forfeited Dec 31'),
    'install software': ('policy_it_acceptable_use.txt', '2.3', 'Requires written approval from IT Department'),
    'slack': ('policy_it_acceptable_use.txt', '2.3', 'Requires written approval from IT Department'),
    'home office': ('policy_finance_reimbursement.txt', '3.1', 'Rs 8,000 one-time for permanent WFH'),
    'equipment allowance': ('policy_finance_reimbursement.txt', '3.1', 'Rs 8,000 one-time for permanent WFH'),
    'personal phone': ('policy_it_acceptable_use.txt', '3.1', 'Email and self-service portal only'),
    'work files': ('policy_it_acceptable_use.txt', '3.1', 'Personal devices may access email and self-service portal only'),
    'flexible working': (None, None, None),
    'working culture': (None, None, None),
    'da and': ('policy_finance_reimbursement.txt', '2.6', 'DA and meal receipts cannot be claimed simultaneously'),
    'meal receipts': ('policy_finance_reimbursement.txt', '2.6', 'DA and meal receipts cannot be claimed simultaneously'),
    'leave without pay': ('policy_hr_leave.txt', '5.2', 'Department Head AND HR Director approval required'),
    'approves lwp': ('policy_hr_leave.txt', '5.2', 'Department Head AND HR Director'),
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact HR for guidance."""

def load_documents():
    for doc_name in DOCUMENTS:
        try:
            with open(f'../data/policy-documents/{doc_name}', 'r', encoding='utf-8') as f:
                content = f.read()
                DOCUMENTS[doc_name] = content
        except FileNotFoundError:
            pass

def answer_question(question):
    q = question.lower()
    
    for keyword, (doc, section, answer) in KEYWORDS.items():
        if keyword in q:
            if doc is None:
                return REFUSAL_TEMPLATE
            return f"[{doc}, Section {section}] {answer}"
    
    return REFUSAL_TEMPLATE

def main():
    load_documents()
    print("Policy Q&A (type 'quit' to exit)")
    print("-" * 40)
    
    while True:
        q = input("\n> ").strip()
        if q.lower() == 'quit':
            break
        print(answer_question(q))

if __name__ == "__main__":
    main()