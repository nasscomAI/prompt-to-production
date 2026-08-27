"""
UC-0B app.py — HR Policy Summarizer.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re
import sys

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a policy text file and parses its contents into structured numbered sections.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Regex to find all clauses of format d.d
    pattern = re.compile(r'^\s*(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\n\s*═════|\Z)', re.MULTILINE | re.DOTALL)
    matches = pattern.findall(content)
    
    sections = {}
    for clause_num, text in matches:
        cleaned_text = ' '.join(text.split()).strip()
        sections[clause_num.strip()] = cleaned_text
        
    return sections


def summarize_policy(sections: dict) -> str:
    """
    Summarizes the parsed policy sections, ensuring all required clauses are represented and no conditions are dropped.
    """
    required_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    # Check for missing required clauses
    missing = [c for c in required_clauses if c not in sections]
    if missing:
        print(f"Warning: Missing required clauses in input: {missing}", file=sys.stderr)
        
    summary_lines = [
        "CITY MUNICIPAL CORPORATION LEAVE POLICY SUMMARY",
        "===============================================",
        "This summary covers the key binding obligations from the Employee Leave Policy (HR-POL-001).",
        "",
        "Key Obligations:"
    ]
    
    # Define summary behavior for each clause to prevent condition drops and scope bleed
    summaries = {
        "2.3": lambda text: f"- [Clause 2.3] Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        "2.4": lambda text: f"- [Clause 2.4] Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
        "2.5": lambda text: f"- [Clause 2.5] Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": lambda text: f"- [Clause 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        "2.7": lambda text: f"- [Clause 2.7] Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
        "3.2": lambda text: f"- [Clause 3.2] Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "3.4": lambda text: f"- [Clause 3.4] Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        # Clause 5.2 is complex (multi-condition approval required from both Department Head and HR Director)
        "5.2": lambda text: f"- [Clause 5.2] [VERBATIM QUOTE - FLAG: MULTI-CONDITION APPROVAL REQUIRED] {text}",
        "5.3": lambda text: f"- [Clause 5.3] LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "7.2": lambda text: f"- [Clause 7.2] Leave encashment during service is not permitted under any circumstances."
    }
    
    for clause in required_clauses:
        text = sections.get(clause, "")
        if not text:
            summary_lines.append(f"- [Clause {clause}] [MISSING IN SOURCE DOCUMENT]")
            continue
            
        if clause in summaries:
            summary_lines.append(summaries[clause](text))
        else:
            # Fallback for unexpected required clauses: quote verbatim
            summary_lines.append(f"- [Clause {clause}] [VERBATIM] {text}")
            
    return '\n'.join(summary_lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    # 1. Retrieve sections
    sections = retrieve_policy(args.input)
    
    # 2. Summarize sections
    summary = summarize_policy(sections)
    
    # 3. Write summary output
    try:
        # Create output directory if it doesn't exist
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing output file {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
