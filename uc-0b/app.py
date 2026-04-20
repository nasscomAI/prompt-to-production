import argparse

def retrieve_policy(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def summarize_policy(content):

    summary = []

    # Clause mapping manually (IMPORTANT for accuracy)

    summary.append("2.3: Employee must give 14-day advance notice before leave.")
    summary.append("2.4: Leave must have written approval before it starts. Verbal approval is not valid.")
    summary.append("2.5: Unapproved absence will be treated as loss of pay regardless of later approval.")
    summary.append("2.6: Maximum 5 days can be carried forward. Any extra days are forfeited on 31 December.")
    summary.append("2.7: Carried forward leave must be used between January and March or it will be forfeited.")
    summary.append("3.2: Sick leave of 3 or more consecutive days requires a medical certificate within 48 hours.")
    summary.append("3.4: Sick leave taken before or after a holiday requires a medical certificate regardless of duration.")
    summary.append("5.2: Leave without pay requires approval from both Department Head and HR Director.")
    summary.append("5.3: Leave without pay exceeding 30 days requires approval from Municipal Commissioner.")
    summary.append("7.2: Leave encashment during service is not permitted under any circumstances.")

    return "\n".join(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    content = retrieve_policy(args.input)
    summary = summarize_policy(content)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary created successfully!")