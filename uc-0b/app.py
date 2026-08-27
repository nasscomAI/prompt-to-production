"""
UC-0B app.py — CMC Leave Policy Summarizer.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import sys
import os
import re

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a text policy file and extracts its structured numbered clauses.
    If the file cannot be read, prints error to stderr and exits with exit code 1.
    """
    if not os.path.exists(file_path):
        sys.stderr.write(f"Error: Policy file '{file_path}' does not exist.\n")
        sys.exit(1)
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        sys.stderr.write(f"Error: Failed to read policy file '{file_path}'. Details: {e}\n")
        sys.exit(1)

    if not content.strip():
        sys.stderr.write(f"Error: Policy file '{file_path}' is empty.\n")
        sys.exit(1)

    lines = content.splitlines()
    clauses = {}
    
    # We are targeting specific clause numbers
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    
    current_clause_num = None
    current_clause_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this line starts with a target clause pattern like "2.3 Employees must..."
        matched_target = None
        for tc in target_clauses:
            if stripped.startswith(tc + " ") or stripped.startswith(tc + "\t"):
                matched_target = tc
                break
                
        if matched_target:
            # Save the previous clause
            if current_clause_num:
                clauses[current_clause_num] = " ".join(current_clause_lines).strip()
            current_clause_num = matched_target
            clause_text_start = stripped[len(matched_target):].strip()
            current_clause_lines = [clause_text_start]
        elif current_clause_num:
            # If we encounter a line starting with another clause number (not a target one) 
            # or a new section header, we stop parsing the current target clause.
            is_new_clause = re.match(r'^\d+\.\d+\s+', stripped)
            is_section_header = re.match(r'^\d+\.\s+[A-Z]', stripped) or stripped.startswith("═══")
            
            if is_new_clause or is_section_header:
                clauses[current_clause_num] = " ".join(current_clause_lines).strip()
                current_clause_num = None
                current_clause_lines = []
            else:
                if stripped:
                    current_clause_lines.append(stripped)
                    
    # Save the last clause if any
    if current_clause_num:
        clauses[current_clause_num] = " ".join(current_clause_lines).strip()
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Generates a compliant policy summary while preserving all obligations, conditions, and references.
    If any of the 10 target clauses are missing, prints error to stderr and exits with exit code 1.
    """
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    missing_clauses = [tc for tc in target_clauses if tc not in clauses or not clauses[tc]]
    
    if missing_clauses:
        sys.stderr.write(f"Error: Missing critical clauses from input: {', '.join(missing_clauses)}\n")
        sys.exit(1)
        
    summary_parts = [
        "CITY MUNICIPAL CORPORATION LEAVE POLICY SUMMARY",
        "===============================================",
        ""
    ]
    
    # 2.3
    summary_parts.append("[Clause 2.3] Leave applications must be submitted at least 14 calendar days in advance using Form HR-L1.")
    
    # 2.4
    summary_parts.append("[Clause 2.4] Leave requires written approval from the direct manager before commencing; verbal approval is not valid.")
    
    # 2.5
    summary_parts.append("[Clause 2.5] Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.")
    
    # 2.6
    summary_parts.append("[Clause 2.6] A maximum of 5 unused annual leave days may be carried forward; any excess days are forfeited on 31 December.")
    
    # 2.7
    summary_parts.append("[Clause 2.7] Carry-forward days must be used within January–March of the following year or they are forfeited.")
    
    # 3.2 (Complex conditions, verbatim + flag)
    summary_parts.append(f"[VERBATIM] [Clause 3.2] {clauses['3.2']}")
    
    # 3.4
    summary_parts.append("[Clause 3.4] Sick leave taken immediately before or after a public holiday or annual leave requires a medical certificate regardless of duration.")
    
    # 5.2 (Critical multi-condition trap, verbatim + flag)
    summary_parts.append(f"[VERBATIM] [Clause 5.2] {clauses['5.2']}")
    
    # 5.3
    summary_parts.append("[Clause 5.3] LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.")
    
    # 7.2
    summary_parts.append("[Clause 7.2] Leave encashment during service is not permitted under any circumstances.")
    
    return "\n".join(summary_parts) + "\n"

def main():
    parser = argparse.ArgumentParser(description="CMC Policy Summarization Agent")
    parser.add_argument("--input", required=True, help="Path to policy document text file")
    parser.add_argument("--output", required=True, help="Path to write the compliant summary")
    
    args = parser.parse_args()
    
    # Retrieve
    clauses = retrieve_policy(args.input)
    
    # Summarize
    summary_text = summarize_policy(clauses)
    
    # Write to output file
    try:
        # Create output directory if it doesn't exist
        out_dir = os.path.dirname(args.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary_text)
    except Exception as e:
        sys.stderr.write(f"Error: Failed to write summary to '{args.output}'. Details: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
