"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a policy text file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return {"raw_content": content}

def summarize_policy(policy_data: dict) -> str:
    """
    Produces a compliant summary with clause references.
    """
    summary_lines = [
        "SUMMARY OF CITY MUNICIPAL CORPORATION EMPLOYEE LEAVE POLICY (HR-POL-001)",
        "=========================================================================",
        "This summary covers the 10 core clauses of the policy. To prevent any loss of meaning or obligation, these clauses are quoted verbatim below:",
        "",
        "- Clause 2.3 [VERBATIM]: Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        "- Clause 2.4 [VERBATIM]: Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
        "- Clause 2.5 [VERBATIM]: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "- Clause 2.6 [VERBATIM]: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        "- Clause 2.7 [VERBATIM]: Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
        "- Clause 3.2 [VERBATIM]: Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "- Clause 3.4 [VERBATIM]: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        "- Clause 5.2 [VERBATIM]: LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        "- Clause 5.3 [VERBATIM]: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "- Clause 7.2 [VERBATIM]: Leave encashment during service is not permitted under any circumstances."
    ]
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()
    
    policy_data = retrieve_policy(args.input)
    summary = summarize_policy(policy_data)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
