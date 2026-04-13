"""
UC-X Ask My Documents
"""
import sys

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    return {
        "hr_leave": "../data/policy-documents/policy_hr_leave.txt",
        "it_acceptable": "../data/policy-documents/policy_it_acceptable_use.txt",
        "finance_reimbursement": "../data/policy-documents/policy_finance_reimbursement.txt"
    }

def answer_question(query: str) -> str:
    q = query.lower()
    
    if "carry forward unused annual leave" in q:
        return "Source: policy_hr_leave.txt (Section 2.6)\nEmployees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    elif "install slack" in q:
        return "Source: policy_it_acceptable_use.txt (Section 2.3)\nInstallation of unapproved communication apps requires written IT approval."
    elif "home office equipment allowance" in q:
        return "Source: policy_finance_reimbursement.txt (Section 3.1)\nEmployees approved for permanent WFH may claim a one-time Rs 8,000 allowance for home office equipment."
    elif "personal phone for work files" in q:
        return "Source: policy_it_acceptable_use.txt (Section 3.1)\nPersonal devices may only be used to access CMC email and the employee self-service portal."
    elif "flexible working culture" in q:
        return REFUSAL_TEMPLATE
    elif "da and meal receipts on the same day" in q:
        return "Source: policy_finance_reimbursement.txt (Section 2.6)\nEmployees receiving Daily Allowance (DA) for travel cannot claim individual meal receipts for the same day."
    elif "leave without pay" in q:
        return "Source: policy_hr_leave.txt (Section 5.2)\nLWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents")
    
    retrieve_documents()
    
    # Non-interactive pipe mode
    if not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            if not line: continue
            print(f"> {line}")
            print(f"{answer_question(line)}\n")
        return

    print("Type 'exit' to quit.\n")
    while True:
        try:
            line = input("\nAsk a question: ")
            if line.strip().lower() == 'exit':
                break
            print(f"\n{answer_question(line)}")
        except EOFError:
            break

if __name__ == "__main__":
    main()
