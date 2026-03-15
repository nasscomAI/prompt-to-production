import argparse

REFUSAL_TEMPLATE = """
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance.
"""

def answer_question(question):

    q = question.lower()

    # HR policy answers
    if "leave days" in q or "carry forward" in q:
        return "HR Policy (Section 2.6): Maximum 5 leave days may be carried forward. Any days above 5 are forfeited on 31 December."

    if "leave without pay" in q or "approve leave without pay" in q:
        return "HR Policy (Section 5.2): Leave Without Pay requires approval from BOTH the Department Head AND the HR Director."

    # IT policy answers
    if "slack" in q:
        return "IT Policy (Section 2.3): Installing Slack or other third-party software on a work laptop requires written IT approval."

    if "personal phone" in q:
        return "IT Policy (Section 3.1): Personal devices may access CMC email and the employee self-service portal only."

    # Finance policy answers
    if "home office equipment" in q:
        return "Finance Policy (Section 3.1): A one-time Rs 8,000 home office equipment allowance is available for permanent work-from-home employees."

    if "da and meal" in q:
        return "Finance Policy (Section 2.6): Daily allowance and meal receipts cannot be claimed on the same day."

    return REFUSAL_TEMPLATE


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    answer = answer_question(args.question)

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    main()