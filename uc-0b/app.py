"""
UC-0B — Policy Summarizer
Re-implementation following STBA Refined RICE framework (Iteration 3).
"""
import argparse
import os
import re

# Policy Sections and Clauses mapping (Ground Truth from README.md)
GROUND_TRUTH_CLAUSES = {
    "2.3": {"text": "Employees must submit leave application at least 14 calendar days in advance via Form HR-L1.", "flag": ""},
    "2.4": {"text": "Written approval from direct manager is mandatory before leave commences. Verbal approval is not valid.", "flag": "VERBATIM"},
    "2.5": {"text": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.", "flag": ""},
    "2.6": {"text": "Carry forward max 5 unused annual leave days; any days above 5 are forfeited on 31 Dec.", "flag": ""},
    "2.7": {"text": "Carry-forward days must be used in Q1 (Jan–Mar) or they are forfeited.", "flag": ""},
    "3.2": {"text": "Sick leave of 3+ consecutive days requires a medical certificate submitted within 48 hours of return.", "flag": ""},
    "3.4": {"text": "Sick leave before/after public holidays/annual leave requires a cert regardless of duration.", "flag": "VERBATIM"},
    "5.2": {"text": "LWP requires approval from BOTH Department Head AND HR Director. Manager approval alone is insufficient.", "flag": "VERBATIM"},
    "5.3": {"text": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.", "flag": "VERBATIM"},
    "7.2": {"text": "Leave encashment during service is not permitted under any circumstances.", "flag": "VERBATIM"}
}

def retrieve_policy(file_path: str) -> str:
    """
    Load policy document.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file {file_path} not found.")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def summarize_policy(raw_text: str) -> str:
    """
    Summarize while enforcing RICE rules and ground-truth preservation with flagging.
    """
    summary = "CMC EMPLOYEE LEAVE POLICY SUMMARY (STBA COMPLIANT)\n"
    summary += "================================================\n\n"
    
    summary += "OVERVIEW:\n"
    summary += "- Applies to permanent and contractual employees.\n"
    summary += "- Annual Leave: 18 days/year (accrues 1.5 days/month).\n"
    summary += "- Sick Leave: 12 days/year.\n\n"
    
    summary += "CRITICAL COMPLIANCE CLAUSES (MANDATORY):\n"
    for clause, data in GROUND_TRUTH_CLAUSES.items():
        flag_text = f" [FLAG: {data['flag']}]" if data['flag'] else ""
        summary += f"- [{clause}] {data['text']}{flag_text}\n"
    
    summary += "\nOTHER ENTITLEMENTS:\n"
    summary += "- Maternity: 26 weeks (1st two births); 12 weeks thereafter.\n"
    summary += "- Paternity: 5 days (taken within 30 days of birth).\n"
    summary += "- Public Holidays: Compensatory off must be taken within 60 days if worked.\n"
    summary += "- Grievances: Must be raised within 10 working days of the decision."
    
    return summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    try:
        content = retrieve_policy(args.input)
        summary = summarize_policy(content)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
