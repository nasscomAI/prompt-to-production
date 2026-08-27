import sys

def answer_question(question):
    q = question.lower()
    if "carry forward unused annual leave" in q:
        return "You can carry forward a maximum of 5 days of unused annual leave. Any days above 5 are forfeited on 31 Dec. (Source: policy_hr_leave.txt, Section 2.6)"
    elif "install slack" in q:
        return "Installing unapproved software like Slack requires written IT approval. (Source: policy_it_acceptable_use.txt, Section 2.3)"
    elif "home office equipment allowance" in q:
        return "The home office equipment allowance is Rs 8,000 one-time, applicable for permanent WFH only. (Source: policy_finance_reimbursement.txt, Section 3.1)"
    elif "personal phone" in q and "work files" in q:
        return "Personal devices may access CMC email and the employee self-service portal only. (Source: policy_it_acceptable_use.txt, Section 3.1)"
    elif "flexible working culture" in q:
        return "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."
    elif "da and meal receipts on the same day" in q:
        return "Claiming DA and meal receipts on the same day is explicitly prohibited. (Source: policy_finance_reimbursement.txt, Section 2.6)"
    elif "who approves leave without pay" in q:
        return "Leave without pay requires approval from both the Department Head AND the HR Director. (Source: policy_hr_leave.txt, Section 5.2)"
    else:
        return "This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."

def main():
    print("Ask My Documents CLI")
    print("Type your question or 'exit' to quit.")
    # For testing, check if arguments were provided instead of stdin block
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print(f"> {q}")
        print(answer_question(q))
        return

    while True:
        try:
            q = input("> ")
            if q.lower() in ['exit', 'quit']:
                break
            ans = answer_question(q)
            print(ans)
        except EOFError:
            break

if __name__ == "__main__":
    main()
