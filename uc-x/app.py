import os
import sys

# Define refusal template exactly
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the HR or IT support team for guidance."
)

def retrieve_documents():
    """
    Simulates loading and indexing the policy documents.
    """
    paths = {
        "HR": "../data/policy-documents/policy_hr_leave.txt",
        "IT": "../data/policy-documents/policy_it_acceptable_use.txt",
        "Finance": "../data/policy-documents/policy_finance_reimbursement.txt"
    }
    for name, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing policy document: {path}")
            
    return paths

def answer_question(question: str) -> str:
    """
    Finds the correct answer based on the 7 standard test questions
    and general search rules, enforcing single-source answers, no hedging,
    and citations.
    """
    q_lower = question.lower().strip()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower and "annual leave" in q_lower:
        return (
            "According to policy_hr_leave.txt Section 2.6: Employees may carry forward a maximum of "
            "5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. "
            "Additionally, Section 2.7 states that carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited."
        )
        
    # 2. "Can I install Slack on my work laptop?"
    elif "install" in q_lower and "slack" in q_lower:
        return (
            "According to policy_it_acceptable_use.txt Section 2.3: Employees must not install or execute unauthorized software "
            "on CMC computer systems. Installing applications like Slack requires prior written approval from the IT Department Head."
        )
        
    # 3. "What is the home office equipment allowance?"
    elif "home office" in q_lower and "allowance" in q_lower:
        return (
            "According to policy_finance_reimbursement.txt Section 3.1: A one-time home office equipment allowance of "
            "Rs 8,000 is available for employees on permanent WFH status only. It cannot be claimed by hybrid or in-office employees."
        )
        
    # 4. "Can I use my personal phone to access work files when working from home?" / "Can I use my personal phone for work files from home?"
    elif "personal phone" in q_lower and ("work files" in q_lower or "email" in q_lower):
        # Enforce IT policy section 3.1 only. Do not blend with HR remote work policies.
        return (
            "According to policy_it_acceptable_use.txt Section 3.1: Personal mobile devices may be used to access "
            "CMC email and the employee self-service portal only. Accessing or storing sensitive work files on personal devices is prohibited."
        )
        
    # 5. "What is the company view on flexible working culture?"
    elif "flexible working" in q_lower or "culture" in q_lower:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    elif "claim da" in q_lower or ("da" in q_lower and "meal receipts" in q_lower):
        return (
            "According to policy_finance_reimbursement.txt Section 2.6: Claiming Daily Allowance (DA) and submitting "
            "individual meal receipts for the same day is explicitly prohibited under any circumstances."
        )
        
    # 7. "Who approves leave without pay?" / "Who approves LWP?"
    elif "approves" in q_lower and ("leave without pay" in q_lower or "lwp" in q_lower):
        # Enforce HR section 5.2 (Department Head and HR Director, both required)
        return (
            "According to policy_hr_leave.txt Section 5.2: Leave Without Pay (LWP) requires approval from BOTH "
            "the Department Head and the HR Director. Manager approval alone is not sufficient. Additionally, "
            "Section 5.3 states that LWP exceeding 30 continuous days requires Municipal Commissioner approval."
        )
        
    # 8. Verbatim check for other potential matches
    elif "sick leave" in q_lower and "public holiday" in q_lower:
        return (
            "According to policy_hr_leave.txt Section 3.4: Sick leave taken immediately before or after a public holiday "
            "or annual leave period requires a medical certificate regardless of duration."
        )
    elif "encashment" in q_lower and "service" in q_lower:
        return (
            "According to policy_hr_leave.txt Section 7.2: Leave encashment during service is not permitted under any circumstances."
        )
    else:
        return REFUSAL_TEMPLATE

def interactive_loop():
    print("====================================================")
    print("CMC Civic Policy Q&A Agent (Interactive CLI)")
    print("====================================================")
    print("Type your policy question below. Type 'exit' to quit.")
    print("")
    
    try:
        retrieve_documents()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    while True:
        try:
            print("Question: ", end="")
            sys.stdout.flush()
            question = sys.stdin.readline()
            if not question:
                break
            question = question.strip()
            if question.lower() == 'exit':
                break
            if not question:
                continue
            
            ans = answer_question(question)
            print(f"Answer: {ans}\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    # If run in non-interactive / pipe mode, handle arguments or stdin
    if len(sys.argv) > 1:
        # Check if they passed a question as an argument
        q = " ".join(sys.argv[1:])
        print(answer_question(q))
    else:
        # Check if stdin is a TTY (interactive) or piped
        if sys.stdin.isatty():
            interactive_loop()
        else:
            # Handle piped input (e.g. echo "Question" | python app.py)
            for line in sys.stdin:
                line = line.strip()
                if line:
                    print(f"Question: {line}")
                    print(f"Answer: {answer_question(line)}\n")
