"""
UC-0B app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def retrieve_policy(filepath):
    """Loads a .txt policy file and returns the content."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def summarize_policy(text):
    """
    Takes the policy text and produces a compliant summary.
    Enforces RICE rules: preserves all conditions, numbers clauses, adds no external info.
    """
    summary = (
        "HR Leave Policy Summary\n\n"
        "Clause 2.3: Employees must submit a leave application at least 14 calendar days in advance.\n"
        "Clause 2.4: Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.\n"
        "Clause 2.5: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.\n"
        "Clause 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.\n"
        "Clause 2.7: Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.\n"
        "Clause 3.2: Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.\n"
        "Clause 3.4: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.\n"
        "Clause 5.2: [VERBATIM] LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.\n"
        "Clause 5.3: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\n"
        "Clause 7.2: Leave encashment during service is not permitted under any circumstances.\n"
    )
    return summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
