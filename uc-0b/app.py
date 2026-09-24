import argparse
import os
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Reads the policy document and parses it into a dictionary of clause numbers to content.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input policy document not found at: {input_path}")
        
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    clauses = {}
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        stripped = line.strip()
        # Matches clause markers like "2.3", "5.2", etc. at the start of a line
        match = re.match(r'^(\d+\.\d+)\s+(.*)', stripped)
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause:
            # End the clause if a blank line or a new major section boundary is reached
            if not stripped or stripped.startswith('══') or re.match(r'^\d+\.\s+', stripped):
                clauses[current_clause] = " ".join(current_text).strip()
                current_clause = None
                current_text = []
            else:
                current_text.append(stripped)
                
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Extracts the 10 target clauses and compiles them into a verbatim compliance summary.
    """
    target_clause_numbers = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    missing = [num for num in target_clause_numbers if num not in clauses]
    if missing:
        raise ValueError(f"Error: Target clauses {missing} are missing from the policy document!")
        
    summary_lines = []
    summary_lines.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    summary_lines.append("====================================================")
    summary_lines.append("Below is the verbatim compliance summary of key binding obligations:")
    summary_lines.append("")
    
    for num in target_clause_numbers:
        content = clauses[num]
        summary_lines.append(f"[{num}] {content}")
        
    return "\n".join(summary_lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        # Write output file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Successfully generated summary: {args.output}")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
