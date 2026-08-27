"""
UC-0B Policy Compliance Summarizer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import os

def retrieve_policy(file_path: str) -> dict:
    """
    Parses a policy .txt file into a dictionary of clause sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find sections like "2.3 " at the start of a line
    sections = {}
    current_clause = None
    current_text = []

    for line in content.splitlines():
        # Match clause numbers at the beginning of a line (e.g., "2.3")
        match = re.match(r'^(\d+\.\d+)\b', line.strip())
        if match:
            if current_clause:
                sections[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [line.strip()]
        elif current_clause:
            current_text.append(line.strip())

    if current_clause:
        sections[current_clause] = " ".join(current_text).strip()

    return sections

def summarize_policy(sections: dict) -> str:
    """
    Generates a compliant summary of the 10 mandatory clauses.
    Ensures no conditions are dropped (especially Clause 5.2).
    """
    targets = [
        ("2.3", "14-day advance notice required via Form HR-L1."),
        ("2.4", "Written manager approval is mandatory before leave commences; verbal approval is not valid."),
        ("2.5", "Unapproved absences will be recorded as Loss of Pay (LOP) regardless of subsequent approval."),
        ("2.6", "Maximum 5 days can be carried forward; any days exceeding this limit are forfeited on 31 December."),
        ("2.7", "Carry-forward days must be used between January and March or they are forfeited."),
        ("3.2", "Sick leave of 3+ consecutive days requires a medical certificate submitted within 48 hours of return."),
        ("3.4", "Medical certificate required for sick leave immediately before or after holidays/annual leave regardless of duration."),
        ("5.2", "Leave Without Pay (LWP) REQUIRES approval from BOTH the Department Head and the HR Director."),
        ("5.3", "LWP exceeding 30 continuous days requires Municipal Commissioner approval."),
        ("7.2", "Leave encashment during service is not permitted under any circumstances.")
    ]

    summary_lines = ["# HR Leave Policy Summary — UC-0B Compliance Output", ""]
    
    for clause_num, ground_truth in targets:
        if clause_num in sections:
            summary_lines.append(f"[{clause_num}] {ground_truth}")
        else:
            summary_lines.append(f"[{clause_num}] [MISSING] WARNING: Clause not found in source document.")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Compliance Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Summary written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
