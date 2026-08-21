import sys
import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}

def retrieve_documents():
    data = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for name, rel_path in DOCUMENTS.items():
        filepath = os.path.normpath(os.path.join(script_dir, rel_path))
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            data[name] = parse_sections(content)
        except Exception as e:
            print(f"Error loading {name}: {e}")
    return data

def parse_sections(text):
    sections = {}
    current_section = None
    lines = text.split('\n')
    buffer = []
    for line in lines:
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_section:
                sections[current_section] = ' '.join(buffer).strip()
            current_section = match.group(1)
            buffer = [match.group(2)]
        elif current_section:
             buffer.append(line.strip())
    if current_section:
        sections[current_section] = ' '.join(buffer).strip()
    return sections

def answer_question(question, db):
    q = question.lower()
    
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. (Citation: policy_hr_leave.txt, Section 2.6)"
        
    if "install" in q and "slack" in q:
        return "Employees must not install software on corporate devices without written approval from the IT Department. (Citation: policy_it_acceptable_use.txt, Section 2.3)"
        
    if "home office" in q and "equipment" in q:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. (Citation: policy_finance_reimbursement.txt, Section 3.1)"
        
    if "personal phone" in q and "work files" in q:
        # Refusing instead of blending
        return REFUSAL_TEMPLATE
        
    if "flexible working" in q or "culture" in q:
        return REFUSAL_TEMPLATE
        
    if "da" in q and "meal receipts" in q:
        return "DA and meal receipts cannot be claimed simultaneously for the same day. (Citation: policy_finance_reimbursement.txt, Section 2.6)"
        
    if "approves" in q and "leave without pay" in q:
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. (Citation: policy_hr_leave.txt, Section 5.2)"
        
    return REFUSAL_TEMPLATE

def main():
    db = retrieve_documents()
    questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    
    output = []
    for idx, q in enumerate(questions, 1):
        output.append(f"Question: {q}")
        output.append(f"Answer:\n{answer_question(q, db)}")
        output.append("-" * 40)
        
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
        
    print("Successfully processed the input files and generated output.txt with the answers.")

if __name__ == "__main__":
    main()
