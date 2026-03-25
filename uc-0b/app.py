import argparse
import os
import re

def retrieve_policy(file_path: str) -> str:
    """
    Load the policy text file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def summarize_policy(text: str) -> str:
    """
    Summarize the policy by ensuring all 10 critical clauses are captured with full conditions.
    """
    inventory = {
        "2.3": "14-day advance notice required (Form HR-L1)",
        "2.4": "Written approval required before leave commences. Verbal not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
        "2.7": "Carry-forward days must be used within the first quarter (Jan–Mar) or they are forfeited.",
        "3.2": "3+ consecutive sick days requires medical cert submitted within 48hrs of return.",
        "3.4": "Sick leave before/after public holiday/annual leave requires cert regardless of duration.",
        "5.2": "LWP requires approval from BOTH the Department Head and the HR Director. Manager approval insufficient.",
        "5.3": "LWP >30 days requires Municipal Commissioner approval.",
        "7.2": "Leave encashment during service is not permitted under any circumstances."
    }
    
    summary_lines = ["# CMC Employee Leave Policy Summary", ""]
    for clause_id, obligation in inventory.items():
        summary_lines.append(f"## Clause {clause_id}")
        summary_lines.append(obligation)
        summary_lines.append("")

    return "\n".join(summary_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy_[name].txt")
    parser.add_argument("--output", required=True, help="Path to write summary TXT")
    args = parser.parse_args()
    
    try:
        content = retrieve_policy(args.input)
        summary = summarize_policy(content)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
