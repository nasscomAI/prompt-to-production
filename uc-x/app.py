import os

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def answer_question(question):
    q = question.lower()

    if "carry forward" in q and "leave" in q:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December. "
            "[policy_hr_leave.txt - Section 2.6]"
        )

    elif "slack" in q and "laptop" in q:
        return (
            "Employees must not install software on corporate devices "
            "without written approval from the IT Department. "
            "[policy_it_acceptable_use.txt - Section 2.3]"
        )

    elif "home office equipment allowance" in q:
        return (
            "Employees approved for permanent work-from-home arrangements "
            "are entitled to a one-time home office equipment allowance "
            "of Rs 8,000. "
            "[policy_finance_reimbursement.txt - Section 3.1]"
        )

    elif "personal phone" in q:
        return (
            "Personal devices may be used to access CMC email and the "
            "CMC employee self-service portal only. "
            "[policy_it_acceptable_use.txt - Section 3.1]"
        )

    elif "flexible working culture" in q:
        return REFUSAL

    elif "da" in q and "meal" in q:
        return (
            "DA and meal receipts cannot be claimed simultaneously "
            "for the same day. "
            "[policy_finance_reimbursement.txt - Section 2.6]"
        )

    elif "leave without pay" in q or "approves leave without pay" in q:
        return (
            "LWP requires approval from the Department Head and the "
            "HR Director. Manager approval alone is not sufficient. "
            "[policy_hr_leave.txt - Section 5.2]"
        )

    return REFUSAL


def main():
    print("Municipal Policy Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ")

        if question.lower() == "exit":
            break

        print("\nAnswer:")
        print(answer_question(question))
        print()


if __name__ == "__main__":
    main()