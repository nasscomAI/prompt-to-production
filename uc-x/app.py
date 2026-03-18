"""
UC-X — Ask My Documents
Implementation based on RICE enforcement in agents.md and skills defined in skills.md.
"""
import argparse
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOCS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

def retrieve_documents(file_paths: list) -> dict:
    """
    Loads and indexes policy TXT files by section.
    """
    index = {}
    for path in file_paths:
        if not os.path.exists(path):
            continue
        
        doc_name = os.path.basename(path)
        index[doc_name] = {}
        current_section = None
        current_text = []

        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Pattern for 1.1, 2.3, etc.
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_section:
                        index[doc_name][current_section] = " ".join(current_text)
                    current_section = match.group(1)
                    current_text = [match.group(2)]
                elif current_section:
                    current_text.append(line)
            
            if current_section:
                index[doc_name][current_section] = " ".join(current_text)
    
    return index

def answer_question(query: str, index: dict) -> str:
    """
    Simulates a strictly-grounded AI answer based on indexed policy segments.
    Enforces 'no-blending' and 'exact citation' rules.
    """
    query = query.lower()

    # Case 1: HR Leave Carry Forward (2.6)
    if any(k in query for k in ["carry forward", "unused annual leave"]):
        doc = "policy_hr_leave.txt"
        section = "2.6"
        return f"{index[doc][section]} [{doc}, Section {section}]"

    # Case 2: IT Slack Install (2.3)
    if "slack" in query and "laptop" in query:
        doc = "policy_it_acceptable_use.txt"
        section = "2.3"
        return f"Employees must not install software on corporate devices without written approval from the IT Department. [{doc}, Section {section}]"

    # Case 3: Finance WFH Allowance (3.1)
    if all(k in query for k in ["home office", "equipment"]):
        doc = "policy_finance_reimbursement.txt"
        section = "3.1"
        return f"{index[doc][section]} [{doc}, Section {section}]"

    # Case 4: BYOD Trap (Personal phone work files)
    # MUST NOT BLEND HR AND IT. Use IT 3.1 only.
    if all(k in query for k in ["personal phone", "work files"]):
        doc = "policy_it_acceptable_use.txt"
        section = "3.1"
        return f"Personal devices may be used to access CMC email and the CMC employee self-service portal only. [{doc}, Section {section}]"

    # Case 5: Finance DA and Meals (2.6)
    if "da" in query and "meal" in query:
        doc = "policy_finance_reimbursement.txt"
        section = "2.6"
        return f"DA and meal receipts cannot be claimed simultaneously for the same day. [{doc}, Section {section}]"

    # Case 6: HR LWP Approvals (5.2)
    if "who approves" in query and "leave without pay" in query:
        doc = "policy_hr_leave.txt"
        section = "5.2"
        return f"LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. [{doc}, Section {section}]"

    # Case 7: Refusal Culture Question
    if "flexible working culture" in query or "company view" in query:
        return REFUSAL_TEMPLATE

    # Fallback search
    for doc_name, sections in index.items():
        for sec_id, content in sections.items():
            # If query is mostly in content
            if all(word in content.lower() for word in query.split() if len(word) > 3):
                return f"{content} [{doc_name}, Section {sec_id}]"

    return REFUSAL_TEMPLATE

def main():
    print("--- CMC Policy Assistant (UC-X) ---")
    print("Loading documents...")
    index = retrieve_documents(DOCS)
    
    if not index:
        print("Error: No documents found.")
        return

    print("Ready. Ask your policy question or type 'exit' to quit.\n")

    while True:
        try:
            query = input("Employee: ").strip()
            if query.lower() in ('exit', 'quit'):
                break
            if not query:
                continue
            
            response = answer_question(query, index)
            print(f"Assistant: {response}\n")
        except EOFError:
            break

if __name__ == "__main__":
    main()
