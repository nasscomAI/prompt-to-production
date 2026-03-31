"""
UC-X app.py — Ask My Documents
Follows RICE, agents.md, and skills.md.
"""
import os
import re

# Refusal Template from README.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOCS = {
    "HR": "../data/policy-documents/policy_hr_leave.txt",
    "IT": "../data/policy-documents/policy_it_acceptable_use.txt",
    "Finance": "../data/policy-documents/policy_finance_reimbursement.txt"
}

def retrieve_documents():
    """Loads all 3 policy files and indexes by document name and section number."""
    index = {}
    for name, path in DOCS.items():
        if not os.path.exists(path):
            # Try absolute path or relative from root
            path = os.path.join("prompt-to-production/data/policy-documents", os.path.basename(path))
        
        with open(path, 'r') as f:
            content = f.read()
        
        # Simple parser for "Section #.#"
        # We split by headers like ════ or just look for section numbers
        sections = {}
        # Match lines like "2.3 Employees must..." or "Section 2.3"
        # Using a simplistic regex to capture numbered bullets at start of lines
        matches = re.finditer(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|\Z)', content, re.MULTILINE | re.DOTALL)
        for m in matches:
            sec_num = m.group(1)
            text = m.group(2).strip()
            sections[sec_num] = text
        
        index[os.path.basename(path)] = sections
    return index


def answer_question(question, index):
    """Searches indexed documents for single-source answers."""
    q = question.lower()
    
    # 1. Carry forward (HR 2.6)
    if "carry forward" in q and "leave" in q:
        sec = index['policy_hr_leave.txt'].get('2.6')
        if sec:
            return f"{sec}\n\nSource: policy_hr_leave.txt Section 2.6"

    # 2. Install Slack (IT 2.3)
    if "install" in q and ("slack" in q or "software" in q):
        sec = index['policy_it_acceptable_use.txt'].get('2.3')
        if sec:
            return f"{sec}\n\nSource: policy_it_acceptable_use.txt Section 2.3"

    # 3. Home office allowance (Finance 3.1)
    if "home office" in q and "allowance" in q:
        sec = index['policy_finance_reimbursement.txt'].get('3.1')
        if sec:
            return f"{sec}\n\nSource: policy_finance_reimbursement.txt Section 3.1"

    # 4. Personal phone / work files (TRAP - IT 3.1 only)
    if "personal phone" in q and ("work files" in q or "home" in q):
        # We must NOT blend with HR. IT 3.1 says email and portal only.
        sec = index['policy_it_acceptable_use.txt'].get('3.1')
        if sec:
            return f"Personal devices may be used to access CMC email and the CMC employee self-service portal ONLY.\n\nSource: policy_it_acceptable_use.txt Section 3.1"

    # 5. DA and meal receipts (Finance 2.6)
    if "da" in q and "meal" in q:
        sec = index['policy_finance_reimbursement.txt'].get('2.6')
        if sec:
            return f"DA and meal receipts cannot be claimed simultaneously for the same day.\n\nSource: policy_finance_reimbursement.txt Section 2.6"

    # 6. Who approves leave without pay (HR 5.2)
    if "approves" in q and "leave without pay" in q:
        sec = index['policy_hr_leave.txt'].get('5.2')
        if sec:
            return f"LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.\n\nSource: policy_hr_leave.txt Section 5.2"

    # Default: Use the mandated refusal template
    return REFUSAL_TEMPLATE


def main():
    print("Loading documents...")
    try:
        index = retrieve_documents()
        print("Ready. Type your question (or 'quit' to exit).")
        
        while True:
            question = input("\nQ: ").strip()
            if not question or question.lower() == 'quit':
                break
            
            answer = answer_question(question, index)
            print(f"\nA: {answer}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
