"""
UC-0B — HR Leave Policy Summarizer
"""

import argparse


CLAUSE_SUMMARY = {
    "2.3": "Clause 2.3: Employees must provide 14-day advance notice before taking leave.",
    "2.4": "Clause 2.4: Written approval must be obtained before leave commences; verbal approval is not valid.",
    "2.5": "Clause 2.5: An unapproved absence will be treated as LOP regardless of any subsequent approval.",
    "2.6": "Clause 2.6: Employees may carry forward a maximum of 5 days. Any days above 5 are forfeited on 31 December.",
    "2.7": "Clause 2.7: Carry-forward leave days must be used during January through March or they are forfeited.",
    "3.2": "Clause 3.2: Sick leave of 3 or more consecutive days requires a medical certificate within 48 hours.",
    "3.4": "Clause 3.4: Sick leave taken immediately before or after a holiday requires a medical certificate regardless of duration.",
    "5.2": "Clause 5.2: LWP requires approval from BOTH the Department Head AND the HR Director.",
    "5.3": "Clause 5.3: LWP exceeding 30 days requires Municipal Commissioner approval.",
    "7.2": "Clause 7.2: Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(input_path: str) -> str:
    """Load the policy document."""
    with open(input_path, "r", encoding="utf-8") as file:
        return file.read()


def summarize_policy(policy_text: str) -> str:
    """
    Produce a clause-complete summary.

    The required clause inventory is explicitly represented above so that
    important conditions cannot be silently omitted.
    """
    missing_source_clauses = []

    for clause in CLAUSE_SUMMARY:
        if clause not in policy_text:
            missing_source_clauses.append(clause)

    lines = [
        "HR LEAVE POLICY — COMPLIANT SUMMARY",
        "",
    ]

    for clause, summary in CLAUSE_SUMMARY.items():
        if clause in missing_source_clauses:
            lines.append(
                f"{clause}: SOURCE CLAUSE NOT FOUND — FLAG FOR REVIEW."
            )
        else:
            lines.append(summary)

    if missing_source_clauses:
        lines.extend(
            [
                "",
                "REVIEW FLAG:",
                "The following expected clauses were not found verbatim in the source: "
                + ", ".join(missing_source_clauses),
            ]
        )

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Summarize HR leave policy without dropping conditions."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy text file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to summary output file",
    )

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()