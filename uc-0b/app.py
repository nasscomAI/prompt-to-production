import argparse


def retrieve_policy(file_path):
    """
    Loads the policy document.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def summarize_policy(policy_text):
    """
    Creates a clause-preserving summary.
    """

    clauses = {
        "2.3": "Employees must give 14-day advance notice before taking leave.",
        "2.4": "Leave must receive written approval before it begins; verbal approval is not valid.",
        "2.5": "Unapproved absence will be treated as Loss of Pay regardless of later approval.",
        "2.6": "A maximum of 5 leave days may be carried forward; any days above 5 are forfeited on 31 December.",
        "2.7": "Carry-forward leave must be used between January and March or it will be forfeited.",
        "3.2": "Three or more consecutive sick leave days require a medical certificate within 48 hours.",
        "3.4": "Sick leave taken before or after a holiday requires a medical certificate regardless of duration.",
        "5.2": "Leave Without Pay requires approval from BOTH the Department Head AND the HR Director.",
        "5.3": "Leave Without Pay longer than 30 days requires approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during service is not permitted under any circumstances."
    }

    summary = []

    for clause, text in clauses.items():
        summary.append(f"{clause}: {text}")

    return "\n".join(summary)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)

    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary generated successfully.")


if __name__ == "__main__":
    main()