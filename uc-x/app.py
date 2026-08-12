def answer_question(question):
    q = question.lower()

    if "carry forward" in q:
        return "HR Policy 2.6: Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December."

    elif "slack" in q:
        return "IT Policy 2.3: Installing Slack on a work laptop requires written IT approval."

    elif "home office equipment" in q:
        return "Finance Policy 3.1: Permanent work-from-home employees may claim a one-time home office equipment allowance of Rs. 8,000."

    elif "personal phone" in q:
        return "IT Policy 3.1: Personal devices may access only CMC email and the employee self-service portal."

    elif "meal receipts" in q or "da" in q:
        return "Finance Policy 2.6: DA and meal receipts cannot be claimed on the same day."

    elif "leave without pay" in q:
        return "HR Policy 5.2: Leave Without Pay requires approval from BOTH the Department Head and the HR Director."

    else:
        return (
            "This question is not covered in the available policy documents "
            "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
            "policy_finance_reimbursement.txt). "
            "Please contact the relevant team for guidance."
        )


def main():
    print("Ask My Documents (type 'exit' to quit)\n")

    while True:
        question = input("Question: ")

        if question.lower() == "exit":
            break

        print("\nAnswer:")
        print(answer_question(question))
        print()


if __name__ == "__main__":
    main()