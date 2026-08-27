import argparse

REFUSAL = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""

RESPONSES = {
    "can i carry forward unused annual leave?":
        "HR Policy Section 2.6: Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December.",

    "can i install slack on my work laptop?":
        "IT Policy Section 2.3: Installing software such as Slack requires written IT approval.",

    "what is the home office equipment allowance?":
        "Finance Policy Section 3.1: Permanent work-from-home employees are eligible for a one-time Rs 8,000 home office equipment allowance.",

    "can i use my personal phone for work files from home?":
        "IT Policy Section 3.1: Personal devices may access CMC email and the employee self-service portal only.",

    "can i claim da and meal receipts on the same day?":
        "Finance Policy Section 2.6: DA and meal reimbursement claims on the same day are explicitly prohibited.",

    "who approves leave without pay?":
        "HR Policy Section 5.2: Leave Without Pay requires approval from BOTH the Department Head AND the HR Director."
}

def main():
    print("CMC Policy Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip().lower()

        if question == "exit":
            break

        answer = RESPONSES.get(question, REFUSAL)

        print("\nAnswer:")
        print(answer)
        print()

if __name__ == "__main__":
    main()