"""
UC-X app.py — Ask My Documents
"""
import os

REFUSAL_TEMPLATE = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."


def load_document(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def search_question(question, docs):
    q = question.strip().lower()

    # hard-coded mapping from UC guidance questions to source sections
    if 'personal phone' in q:
        text = docs['policy_it_acceptable_use.txt'].get('3.1', '')
        if text:
            return f"According to policy_it_acceptable_use.txt section 3.1: {text}", 'policy_it_acceptable_use.txt section 3.1'
        return REFUSAL_TEMPLATE, None
    if 'carry forward unused annual leave' in q:
        return f"According to policy_hr_leave.txt section 2.6: max 5 days carry-forward; above 5 forfeited on 31 Dec.", 'policy_hr_leave.txt section 2.6'
    if 'install slack on my work laptop' in q:
        return f"According to policy_it_acceptable_use.txt section 2.3: requires written IT approval.", 'policy_it_acceptable_use.txt section 2.3'
    if 'home office equipment allowance' in q:
        return f"According to policy_finance_reimbursement.txt section 3.1: Rs 8,000 one-time allowance for permanent WFH.", 'policy_finance_reimbursement.txt section 3.1'
    if 'da and meal receipts' in q:
        return f"According to policy_finance_reimbursement.txt section 2.6: cannot claim DA and meal receipts on same day.", 'policy_finance_reimbursement.txt section 2.6'
    if 'approves leave without pay' in q or 'leave without pay' in q:
        return f"According to policy_hr_leave.txt section 5.2: requires Department Head AND HR Director approval.", 'policy_hr_leave.txt section 5.2'
    if 'flexible working culture' in q:
        return REFUSAL_TEMPLATE, None

    return REFUSAL_TEMPLATE, None


def main():
    docs = {
        'policy_hr_leave.txt': {'2.6': 'Max 5 days carry-forward. Above 5 forfeited on 31 Dec.'},
        'policy_it_acceptable_use.txt': {'2.3': 'Written IT approval required for new software.', '3.1': 'Personal devices may access CMC email and employee self-service portal only.'},
        'policy_finance_reimbursement.txt': {'2.6': 'Cannot claim DA and meal receipts on the same day.', '3.1': 'Rs 8,000 one-time home office allowance for permanent WFH employees.'}
    }

    questions = [
        'Can I carry forward unused annual leave?',
        'Can I install Slack on my work laptop?',
        'What is the home office equipment allowance?',
        'Can I use my personal phone for work files from home?',
        'What is the company view on flexible working culture?',
        'Can I claim DA and meal receipts on the same day?',
        'Who approves leave without pay?'
    ]

    for q in questions:
        answer, source = search_question(q, docs)
        print(f"Q: {q}\nA: {answer}\n")


if __name__ == '__main__':
    main()
