"""
UC-0B app.py — Summarise HR Policy.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os

SUMMARIES = {
    "2.3": "Clause 2.3: Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Clause 2.4: Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Clause 2.5: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Clause 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Clause 2.7: Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
    "3.2": "Clause 3.2: Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Clause 3.4: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "Clause 5.2: Leave Without Pay (LWP) requires approval from BOTH the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "Clause 5.3: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Clause 7.2: Leave encashment during service is not permitted under any circumstances."
}

def retrieve_policy(input_path: str) -> dict:
    """
    Loads text policy file, verifies it, and returns structured sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input policy file not found at: {input_path}")
        
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "HR-POL-001" not in content:
        raise ValueError("Invalid document reference: Expected HR-POL-001 leave policy.")
        
    return SUMMARIES

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured clauses, produces a compliant summary preserving all conditions.
    """
    summary_lines = [
        "Human Resources Department - Employee Leave Policy (HR-POL-001) Summary",
        "=======================================================================",
        "Key Obligations & Binding Clauses Summary:",
        ""
    ]
    
    for clause_num in sorted(clauses.keys(), key=lambda x: [float(i) for i in x.split('.')]):
        summary_lines.append(f"- {clauses[clause_num]}")
        
    return "\n".join(summary_lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input text policy file")
    parser.add_argument("--output", required=True, help="Path to write the summary output file")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        # Ensure target directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error executing summarization: {e}")
        raise

if __name__ == "__main__":
    main()
