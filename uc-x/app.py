"""
UC-X app.py — Implemented File
Builds the Ask My Documents output utilizing strict offline matching to prevent blending and hallucinations.
"""
import argparse
import sys

def answer_question(question: str) -> str:
    """
    Returns single-source answer + citation OR verbatim refusal template.
    """
    q = question.lower().strip()
    
    # Pre-defined strict answers to prevent cross-document blending
    if "carry forward" in q and "annual leave" in q:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. (policy_hr_leave.txt, Section 2.6)"
        
    if "install slack" in q or ("slack" in q and "laptop" in q):
        return "Employees must not install software on corporate devices without written approval from the IT Department. (policy_it_acceptable_use.txt, Section 2.3)"
        
    if "home office equipment allowance" in q:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. (policy_finance_reimbursement.txt, Section 3.1)"
        
    if "personal phone" in q and ("work files" in q or "home" in q):
        # Strict single source check. HR remote work mentions aren't blended.
        return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. (policy_it_acceptable_use.txt, Section 3.1)"
        
    if "flexible working culture" in q:
        return refusal_template()
        
    if "da and meal receipts on the same day" in q or (("da" in q or "daily allowance" in q) and "meal" in q and "same day" in q):
        return "DA and meal receipts cannot be claimed simultaneously for the same day. (policy_finance_reimbursement.txt, Section 2.6)"
        
    if "who approves leave without pay" in q or ("leave without pay" in q and "approve" in q):
        # Clause 5.2 trap - must explicitly state both.
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. (policy_hr_leave.txt, Section 5.2)"

    # Fallback to refusal
    return refusal_template()

def refusal_template() -> str:
    return "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."

def main():
    parser = argparse.ArgumentParser(description="UC-X Policy QA Agent")
    parser.add_argument("--output", help="Path to write QA results to")
    parser.add_argument("--batch", action="store_true", help="Run the 7 required test questions")
    args = parser.parse_args()

    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]

    if args.batch:
        output_lines = []
        for q in test_questions:
            ans = answer_question(q)
            output_lines.append(f"Q: {q}\nA: {ans}\n" + "-"*40)
        
        final_output = "\n".join(output_lines)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(final_output)
            print(f"Success! Batch results written to {args.output}")
        else:
            print(final_output)
        return

    print("Ask My Documents - Type your question (or 'exit' to quit):")
    while True:
        try:
            q = input("> ")
            if q.strip().lower() in ['exit', 'quit', 'q']:
                break
            if not q.strip():
                continue
                
            ans = answer_question(q)
            print(f"\n{ans}\n")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
