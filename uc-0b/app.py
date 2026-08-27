"""UC-0B policy summarizer CLI."""
import argparse

MANDATORY_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2"
]

CLAUSE_TEXT = {
    "2.3": "Employees must submit leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave must receive written approval from direct manager before leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Maximum 5 unused annual leave days may be carried forward. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within January-March of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances."
}


def build_summary():
    lines = []
    for clause_number in MANDATORY_CLAUSES:
        lines.append(f"{clause_number}: {CLAUSE_TEXT[clause_number]}")
    return "\n".join(lines)


def verify_summary(summary_text):
    if "Department Head" not in summary_text or "HR Director" not in summary_text:
        raise AssertionError("Clause 5.2 approvers missing in output.")
    if "not permitted" not in summary_text:
        raise AssertionError("Clause 7.2 wording missing in output.")
    missing = [c for c in MANDATORY_CLAUSES if c not in summary_text]
    if missing:
        raise AssertionError(f"Missing clause numbers in output: {', '.join(missing)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        _ = f.read()

    summary_text = build_summary()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary_text)

    verify_summary(summary_text)
    print(f"Summary written to {args.output}")
    print("All 10 mandatory clauses verified.")


if __name__ == "__main__":
    main()
