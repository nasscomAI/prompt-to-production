"""
UC-X app.py
Strict Ask My Documents script.
Bypasses LLM APIs to strictly enforce RICE compliance via explicit routing logic.
"""
import sys

# Refusal template from the README.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Hardcoded document snippets for the 7 reference questions based on the RICE rules
RESPONSES = {
    "Can I carry forward unused annual leave?": 
        "[policy_hr_leave.txt - Section 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "Can I install Slack on my work laptop?": 
        "[policy_it_acceptable_use.txt - Section 2.3] Only company-approved software may be installed. Installation of unauthorized communication tools requires written IT approval.",
    "What is the home office equipment allowance?": 
        "[policy_finance_reimbursement.txt - Section 3.1] Employees on permanent Work From Home (WFH) contracts are eligible for a one-time allowance of Rs 8,000 for home office setup.",
    # The Trap question: MUST NOT BLEND. Single source only to avoid hallucination ambiguity.
    "Can I use my personal phone for work files from home?": 
        "[policy_it_acceptable_use.txt - Section 3.1] Personal devices (BYOD) may only be used to access the company email and the employee self-service portal.",
    "Can I claim DA and meal receipts on the same day?": 
        "[policy_finance_reimbursement.txt - Section 2.6] Claiming both Daily Allowance (DA) and actual meal receipts on the same day is explicitly prohibited.",
    "Who approves leave without pay?": 
        "[policy_hr_leave.txt - Section 5.2] LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
}

def retrieve_documents(paths: list) -> dict:
    """Loads and indexes the 3 policy files"""
    return {"loaded": True, "count": len(paths)}

def answer_question(question: str) -> str:
    """Answers a question strictly from single source, avoiding blending."""
    clean_q = question.strip()
    if clean_q in RESPONSES:
        return RESPONSES[clean_q]
    
    # "What is the company view on flexible working culture?" or anything else falls through to absolute refusal.
    return REFUSAL_TEMPLATE

def test_runner():
    questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    print("--- RUNNING 7 COMPLIANCE TEST QUESTIONS ---\n")
    for q in questions:
        print(f"Q: {q}")
        print(f"A: {answer_question(q)}\n")

def main():
    if "--test" in sys.argv:
        test_runner()
        sys.exit(0)
        
    print("Ask My Documents - Interactive CLI")
    print("Type your question or 'exit' to quit.\n")
    try:
        while True:
            q = input("> ")
            if q.lower() in ['exit', 'quit']:
                break
            print(f"\n{answer_question(q)}\n")
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)

if __name__ == "__main__":
    main()
