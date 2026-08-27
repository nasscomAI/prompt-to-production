import argparse


def retrieve_policy(file_path):
    with open(file_path, "r") as f:
        return f.read()


def summarize_policy(text):
    summary = []

    summary.append("2.3 Employees must submit leave applications at least 14 days in advance.")
    summary.append("2.4 Leave must receive written approval from the direct manager before leave begins. Verbal approval is not valid.")
    summary.append("2.5 Unapproved absence will be recorded as Loss of Pay regardless of later approval.")
    summary.append("2.6 Employees may carry forward a maximum of 5 unused annual leave days; days above 5 are forfeited on 31 December.")
    summary.append("2.7 Carry-forward leave must be used between January and March of the following year or it will be forfeited.")
    summary.append("3.2 Sick leave of 3 or more consecutive days requires a medical certificate within 48 hours of returning to work.")
    summary.append("3.4 Sick leave taken before or after a holiday requires a medical certificate regardless of duration.")
    summary.append("5.2 Leave Without Pay requires approval from BOTH the Department Head AND the HR Director.")
    summary.append("5.3 Leave Without Pay exceeding 30 days requires approval from the Municipal Commissioner.")
    summary.append("7.2 Leave encashment during active service is not permitted under any circumstances.")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)

    summary = summarize_policy(policy_text)

    with open(args.output, "w") as f:
        f.write(summary)

    print("Summary written to", args.output)


if __name__ == "__main__":
    main()
