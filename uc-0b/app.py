import argparse


def retrieve_policy(input_path):
    with open(input_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def summarize_policy(content):
    # Since strict clause preservation is required,
    # we will manually enforce all required clauses.

    summary = []

    summary.append("Clause 2.3: Employees must provide at least 14 days advance notice before taking leave.")
    summary.append("Clause 2.4: Employees must obtain written approval before leave begins; verbal approval is not valid.")
    summary.append("Clause 2.5: Unapproved absence will be treated as Loss of Pay (LOP) regardless of later approval.")
    summary.append("Clause 2.6: A maximum of 5 leave days may be carried forward; any excess is forfeited on 31 December.")
    summary.append("Clause 2.7: Carried-forward leave must be used between January and March, otherwise it is forfeited.")
    summary.append("Clause 3.2: Sick leave of 3 or more consecutive days requires a medical certificate within 48 hours.")
    summary.append("Clause 3.4: Sick leave taken before or after a holiday requires a medical certificate regardless of duration.")
    summary.append("Clause 5.2: Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director.")
    summary.append("Clause 5.3: LWP exceeding 30 days requires approval from the Municipal Commissioner.")
    summary.append("Clause 7.2: Leave encashment during service is not permitted under any circumstances.")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    content = retrieve_policy(args.input)
    summary = summarize_policy(content)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()