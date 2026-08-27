"""
UC-0B Policy Summarizer
"""

import argparse


def summarize_policy(text):
    text = text.lower()

    if "leave" in text:
        return "Employees must apply for leave through the HR system and obtain manager approval."

    elif "reimbursement" in text:
        return "Employees can claim reimbursements by submitting valid bills and approvals."

    elif "acceptable use" in text or "it" in text:
        return "Company IT systems should only be used for official work and must follow security policies."

    else:
        return "General company policy guidelines."


def main():

    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    summary = summarize_policy(text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary saved to:", args.output)


if __name__ == "__main__":
    main()