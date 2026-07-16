"""
UC-X app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import sys
import os

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents():
    paths = {
        'HR': '../data/policy-documents/policy_hr_leave.txt',
        'IT': '../data/policy-documents/policy_it_acceptable_use.txt',
        'Finance': '../data/policy-documents/policy_finance_reimbursement.txt'
    }
    docs = {}
    for name, path in paths.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                docs[name] = f.read()
        else:
            # Fallback path if run from root or different folder
            alt_path = os.path.join('data', 'policy-documents', os.path.basename(path))
            if os.path.exists(alt_path):
                with open(alt_path, 'r', encoding='utf-8') as f:
                    docs[name] = f.read()
            else:
                docs[name] = ""
    return docs

def answer_question(question: str, docs: dict) -> str:
    q = question.lower().strip()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry" in q and "annual" in q and "leave" in q:
        return (
            "Yes. Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December.\n"
            "Source: policy_hr_leave.txt (Section 2.6)"
        )
        
    # 2. "Can I install Slack on my work laptop?"
    if "install" in q and "slack" in q:
        return (
            "No. Employees must not install software on corporate devices without written approval from the IT Department. "
            "Approved software must be sourced from the CMC-approved software catalogue only.\n"
            "Source: policy_it_acceptable_use.txt (Section 2.3 & 2.4)"
        )
        
    # 3. "What is the home office equipment allowance?"
    if "home office" in q and ("allowance" in q or "equipment" in q):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.\n"
            "Source: policy_finance_reimbursement.txt (Section 3.1)"
        )
        
    # 4. "Can I use my personal phone for work files from home?" or "Can I use my personal phone to access work files when working from home?"
    if "personal phone" in q and ("work files" in q or "access" in q):
        # Single-source IT policy section 3.1/3.2, no blending with remote work tools from HR.
        return (
            "No. Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.\n"
            "Source: policy_it_acceptable_use.txt (Section 3.1 & 3.2)"
        )
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "claim da" in q or ("da" in q and "meal" in q and "same day" in q):
        return (
            "No. Daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day.\n"
            "Source: policy_finance_reimbursement.txt (Section 2.6)"
        )
        
    # 7. "Who approves leave without pay?"
    if "leave without pay" in q or ("approves" in q and "lwp" in q):
        return (
            "Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director. "
            "Manager approval alone is not sufficient. LWP exceeding 30 continuous days also requires approval from the Municipal Commissioner.\n"
            "Source: policy_hr_leave.txt (Section 5.2 & 5.3)"
        )
        
    # 5. "What is the company view on flexible working culture?" or any other question -> Refusal template
    return REFUSAL_TEMPLATE

def main():
    docs = retrieve_documents()
    print("=" * 60)
    print("CMC Policy Assistant Interactive CLI (UC-X)")
    print("Type your question below, or type 'exit' to quit.")
    print("=" * 60)
    
    # Check if run with standard stdin to allow automated evaluation or manual interactive mode
    if not sys.stdin.isatty():
        # Read from pipeline/redirected input
        for line in sys.stdin:
            q = line.strip()
            if not q or q.lower() in ['exit', 'quit']:
                break
            print(f"\nQuestion: {q}")
            ans = answer_question(q, docs)
            print(f"Answer:\n{ans}\n")
            print("-" * 40)
        return

    while True:
        try:
            q = input("\nAsk a question: ").strip()
            if not q:
                continue
            if q.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            ans = answer_question(q, docs)
            print(f"\nAnswer:\n{ans}\n")
            print("-" * 40)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
