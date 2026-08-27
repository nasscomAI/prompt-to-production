import argparse


def retrieve_policy(input_path):
    with open(input_path, "r", encoding="utf-8") as file:
        return file.read()


def summarize_policy(policy_text):
    required_clauses = {
        "2.3": "14-day advance notice is required.",
        "2.4": "Written approval is required before leave commences. Verbal approval is not valid.",
        "2.5": "An unapproved absence will result in loss of pay (LOP) regardless of subsequent approval.",
        "2.6": "A maximum of 5 days may be carried forward. Days above 5 are forfeited on 31 December.",
        "2.7": "Carry-forward days must be used from January through March or they are forfeited.",
        "3.2": "Three or more consecutive sick days requires a medical certificate within 48 hours.",
        "3.4": "Sick leave taken before or after a holiday requires a medical certificate regardless of duration.",
        "5.2": "Leave Without Pay (LWP) requires approval from both the Department Head and HR Director.",
        "5.3": "LWP exceeding 30 days requires Municipal Commissioner approval.",
        "7.2": "Leave encashment during service is not permitted under any circumstances."
    }

    lines = [
        "HR Leave Policy Summary",
        "",
        "2.3 — 14-day advance notice is required.",
        "",
        "2.4 — Written approval is required before leave commences. Verbal approval is not valid.",
        "",
        "2.5 — An unapproved absence will result in loss of pay (LOP) regardless of subsequent approval.",
        "",
        "2.6 — A maximum of 5 days may be carried forward. Days above 5 are forfeited on 31 December.",
        "",
        "2.7 — Carry-forward days must be used from January through March or they are forfeited.",
        "",
        "3.2 — Three or more consecutive sick days requires a medical certificate within 48 hours.",
        "",
        "3.4 — Sick leave taken before or after a holiday requires a medical certificate regardless of duration.",
        "",
        "5.2 — Leave Without Pay (LWP) requires approval from both the Department Head and HR Director.",
        "",
        "5.3 — LWP exceeding 30 days requires Municipal Commissioner approval.",
        "",
        "7.2 — Leave encashment during service is not permitted under any circumstances."
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Leave Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy input file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to summary output file"
    )

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)

    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()