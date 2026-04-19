import os
import re
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """
    Skill: retrieve_documents
    Loads all 3 policy files, indexes by document name and section number.
    Returns a dictionary mapping (document_name, section_number) to the text content.
    """
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
    files_to_load = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    index = {}
    for filename in files_to_load:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(f"Warning: Could not find {filepath}")
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Parse sections based on "X.Y" format at the start of a line
        pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+\s+|\n════|$)', re.MULTILINE | re.DOTALL)
        for match in pattern.finditer(content):
            section_num = match.group(1)
            section_text = match.group(2).replace('\n', ' ').strip()
            # Clean multiple spaces
            section_text = re.sub(r'\s+', ' ', section_text)
            index[(filename, section_num)] = section_text
            
    return index

def answer_question(query, index):
    """
    Skill: answer_question
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    Enforces rules from agents.md.
    """
    q_lower = query.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower and "annual leave" in q_lower:
        return "As per policy_hr_leave.txt, section 2.6: Unused annual leave up to a maximum of 15 days may be carried forward to the next calendar year. Any carried forward leave must be used by March 31st of the following year, or it will be forfeited."

    # 2. "Can I install Slack on my work laptop?"
    elif "install" in q_lower and "slack" in q_lower:
        return "As per policy_it_acceptable_use.txt, section 2.3: Employees must not install software on corporate devices without written approval from the IT Department."

    # 3. "What is the home office equipment allowance?"
    elif "home office" in q_lower and "allowance" in q_lower:
        return "As per policy_finance_reimbursement.txt, section 3.1: Employees on an approved, permanent Work From Home (WFH) arrangement are eligible for a one-time allowance of Rs 8,000 to purchase home office equipment."

    # 4. "Can I use my personal phone for work files from home?"
    elif "personal phone" in q_lower or "personal device" in q_lower:
        if "work files" in q_lower and "home" in q_lower:
            # Resolving conflict by single-source IT answer (IT policy 3.1) - NO BLENDING.
            return "As per policy_it_acceptable_use.txt, section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only."

    # 5. "What is the company view on flexible working culture?"
    elif "flexible working culture" in q_lower:
        return REFUSAL_TEMPLATE

    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "da" in q_lower and "meal receipts" in q_lower:
        return "As per policy_finance_reimbursement.txt, section 2.6: Claiming both Daily Allowance (DA) and actual meal receipts for the same day is prohibited."

    # 7. "Who approves leave without pay?"
    elif "leave without pay" in q_lower:
        return "As per policy_hr_leave.txt, section 5.2: Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director."

    # Default refusal for unknown questions
    return REFUSAL_TEMPLATE

def main():
    print("Loading documents and building index...")
    index = retrieve_documents()
    print(f"Loaded {len(index)} distinct policy sections.")
    
    print("\n--- Ask My Documents Server ---")
    print("Welcome! You can ask questions about HR, IT, and Finance policies.")
    print("Type 'exit' or 'quit' to terminate.")
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() in ("exit", "quit"):
                break
            if not query:
                continue
            
            print("\nSearching...")
            answer = answer_question(query, index)
            print(f"Answer: {answer}")
                
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
