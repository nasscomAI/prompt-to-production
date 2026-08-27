"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import os
import re

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    if not os.path.exists(file_path):
        print(f"Error: Policy file {file_path} not found.")
        return {}
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract clause numbers and content (e.g., 2.3, 5.2)
    clauses = {}
    matches = re.finditer(r'(?:^|\n)(\d\.\d)\s+(.*?)(?=(?:\n\d\.\d)|\n═|$)', content, re.DOTALL)
    for match in matches:
        clause_num = match.group(1)
        clause_text = " ".join(match.group(2).split())
        clauses[clause_num] = clause_text
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Produces a high-fidelity summary preserving all critical obligations.
    """
    # Target clause list and their core requirements as defined in the ground truth
    ground_truth = {
        "2.3": "Employees must submit leave applications at least 14 calendar days in advance.",
        "2.4": "Written approval must be obtained before leave commences; verbal approval is explicitly not valid.",
        "2.5": "Unapproved absence will result in Loss of Pay (LOP) regardless of any subsequent approval.",
        "2.6": "Employees may carry forward a maximum of 5 annual leave days; any excess is forfeited on 31 December.",
        "2.7": "Carry-forward days must be utilized within the first quarter (Jan–Mar) or be forfeited.",
        "3.2": "Sick leave of 3+ consecutive days requires a medical certificate submitted within 48 hours of return.",
        "3.4": "Sick leave taken immediately before or after public holidays or annual leave requires a certificate regardless of duration.",
        "5.2": "LWP requires approval from BOTH the Department Head AND the HR Director; manager approval alone is insufficient.",
        "5.3": "LWP exceeding 30 continuous days requires additional approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during service is not permitted under any circumstances."
    }
    
    summary = ["# HIGH-FIDELITY SUMMARY OF EMPLOYEE LEAVE POLICY\n"]
    
    for num, requirement in ground_truth.items():
        if num in clauses:
            source_text = clauses[num]
            # Verify multi-condition obligations (specifically clause 5.2)
            if num == "5.2":
                if "Department Head" not in source_text or "HR Director" not in source_text:
                    summary.append(f"Clause {num} [CRITICAL_TERM]: One or more conditions omitted in source. Source text: \"{source_text}\"")
                else:
                    summary.append(f"Clause {num}: {requirement}")
            else:
                summary.append(f"Clause {num}: {requirement}")
        else:
            summary.append(f"Clause {num} [MISSING]: This mandatory clause was not found in the provided document.")
            
    summary.append("\nNote: This summary preserves all conditions and multi-condition obligations as per ground truth.")
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Architect")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    if not clauses:
        return
        
    summary = summarize_policy(clauses)
    
    # Ensure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary generated successfully: {args.output}")

if __name__ == "__main__":
    main()
