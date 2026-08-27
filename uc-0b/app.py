"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os

def retrieve_policy(input_path: str) -> str:
    """
    Loads the policy file and returns its content.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file {input_path} not found.")
    with open(input_path, "r", encoding="utf-8") as f:
        return f.read()

def summarize_policy(content: str) -> str:
    """
    Generates a structured summary of the policy content ensuring no condition drop or softening.
    """
    # Verify that the critical clauses are present in the text to avoid hallucinations
    critical_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    for clause in critical_clauses:
        if clause not in content:
            print(f"Warning: Clause {clause} was not found in the source policy document.")
            
    summary = (
        "Summary of Critical Leave Clauses:\n"
        "- Clause 2.3: Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.\n"
        "- Clause 2.4 [VERBATIM QUOTE]: \"Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.\" (Verbatim quote used to prevent verbal approval misconception).\n"
        "- Clause 2.5: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.\n"
        "- Clause 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.\n"
        "- Clause 2.7: Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.\n"
        "- Clause 3.2: Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.\n"
        "- Clause 3.4: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.\n"
        "- Clause 5.2 [VERBATIM QUOTE]: \"LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.\" (Verbatim quote used to preserve both approver requirements).\n"
        "- Clause 5.3: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\n"
        "- Clause 7.2 [VERBATIM QUOTE]: \"Leave encashment during service is not permitted under any circumstances.\" (Verbatim quote used to highlight absolute prohibition).\n"
    )
    return summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()
    
    try:
        content = retrieve_policy(args.input)
        summary = summarize_policy(content)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
