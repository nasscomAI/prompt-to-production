import argparse

def load_policy(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def answer_query(policy_text, question):

    question_lower = question.lower()

    if "sick leave" in question_lower:
        return "Refer to Sick Leave section in policy_hr_leave.txt for eligibility and limits."

    elif "casual leave" in question_lower:
        return "Refer to Casual Leave section in policy_hr_leave.txt for leave entitlement."

    elif "annual leave" in question_lower or "vacation" in question_lower:
        return "Refer to Annual Leave section in policy_hr_leave.txt for leave rules."

    else:
        return "INSUFFICIENT_POLICY_INFORMATION"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--policy", required=True)
    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    policy_text = load_policy(args.policy)

    answer = answer_query(policy_text, args.question)

    print("Answer:", answer)


if __name__ == "__main__":
    main()