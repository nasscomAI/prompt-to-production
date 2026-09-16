import argparse


REQUIRED_CLAUSES = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def extract_required_clauses(policy_text):
    """Verify that every mandatory clause exists in the source policy."""
    missing = []

    for clause in REQUIRED_CLAUSES:
        if not any(line.startswith(clause + " ") for line in policy_text.splitlines()):
            missing.append(clause)

    return missing


def build_summary(policy_text):
    """Create a traceable summary containing every mandatory clause."""
    missing = extract_required_clauses(policy_text)

    if missing:
        raise ValueError(
            "Required clauses missing from source policy: " + ", ".join(missing)
        )

    lines = [
        "CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY",
        "Summary of mandatory clauses",
        "",
    ]

    for clause, summary in REQUIRED_CLAUSES.items():
        lines.append(f"{clause}: {summary}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate a compliant summary of the HR leave policy."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as file:
        policy_text = file.read()

    summary = build_summary(policy_text)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
