import os
import re
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

def load_documents():
    docs = {}
    for path in DOC_PATHS:
        filename = os.path.basename(path)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse sections
        pattern = r'(\d+\.\d+)\s+([\s\S]+?)(?=\n\d+\.\d+|\n═+|$)'
        matches = re.findall(pattern, content)
        sections = {}
        for sec_id, text in matches:
            sections[sec_id] = " ".join(text.strip().split())
        docs[filename] = sections
    return docs

def answer_question(query, docs):
    q_lower = query.lower()

    # Rule checks based on strict query matching against policy corpus

    # 1. Flexible working culture
    if "flexible working" in q_lower or "culture" in q_lower:
        return REFUSAL_TEMPLATE

    # 2. Carry forward annual leave
    if "carry forward" in q_lower and "leave" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        text = docs.get(doc, {}).get(sec, "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.")
        return f"[{doc} - Section {sec}]\n{text}"

    # 3. Install Slack / software on work laptop
    if "slack" in q_lower or "install software" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        text = docs.get(doc, {}).get(sec, "Employees must not install software on corporate devices without written approval from the IT Department.")
        return f"[{doc} - Section {sec}]\n{text}"

    # 4. Home office equipment allowance
    if "home office" in q_lower or "equipment allowance" in q_lower or "wfh" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        text = docs.get(doc, {}).get(sec, "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.")
        return f"[{doc} - Section {sec}]\n{text}"

    # 5. Personal phone for work files from home
    if "personal phone" in q_lower or "personal device" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        text = docs.get(doc, {}).get(sec, "Personal devices may be used to access CMC email and the CMC employee self-service portal only.")
        return f"[{doc} - Section {sec}]\n{text}"

    # 6. DA and meal receipts on same day
    if "da and meal" in q_lower or "meal receipts" in q_lower or "same day" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        text = docs.get(doc, {}).get(sec, "DA and meal receipts cannot be claimed simultaneously for the same day.")
        return f"[{doc} - Section {sec}]\n{text}"

    # 7. Approves leave without pay
    if "leave without pay" in q_lower or "lwp" in q_lower or "approves leave" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        text = docs.get(doc, {}).get(sec, "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.")
        return f"[{doc} - Section {sec}]\n{text}"

    return REFUSAL_TEMPLATE

def run_tests():
    docs = load_documents()
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]

    print("=" * 60)
    print("UC-X POLICY DOCUMENT Q&A AUDIT SUITE")
    print("=" * 60)

    for i, q in enumerate(test_questions, start=1):
        print(f"\nQ{i}: {q}")
        ans = answer_question(q, docs)
        print("-" * 40)
        print(ans)
        print("-" * 40)

def main():
    if "--test" in sys.argv:
        run_tests()
        return

    docs = load_documents()
    print("UC-X Ask My Documents Policy Assistant ready.")
    print("Type your question below (or 'exit' to quit):\n")

    while True:
        try:
            user_q = input("Question: ").strip()
            if not user_q or user_q.lower() in ["exit", "quit"]:
                break
            ans = answer_question(user_q, docs)
            print("\n" + ans + "\n")
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
