"""
UC-0B app.py — Policy Summarizer.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import sys

def retrieve_policy(input_path: str) -> dict:
    """
    Read input policy text file and parse its numbered clauses into a dictionary.
    """
    clauses = {}
    current_clause = None
    current_text = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_str = line.rstrip()
                # Match line starting with a clause pattern like 2.3, 5.2, etc.
                match = re.match(r'^\s*(\d+\.\d+)\s+(.*)$', line_str)
                if match:
                    if current_clause:
                        clauses[current_clause] = " ".join(current_text).strip()
                    current_clause = match.group(1)
                    current_text = [match.group(2).strip()]
                else:
                    if current_clause:
                        # End clause if we hit section lines or headers
                        if line_str.strip() == "" or "════" in line_str or re.match(r'^\s*\d+\.\s+[A-Z]', line_str):
                            clauses[current_clause] = " ".join(current_text).strip()
                            current_clause = None
                            current_text = []
                        else:
                            current_text.append(line_str.strip())
            
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
    except Exception as e:
        print(f"Error reading policy file: {e}", file=sys.stderr)
        raise e
        
    return clauses


def summarize_policy(clauses: dict) -> str:
    """
    Extract the 10 target clauses and format them verbatim to ensure no binding conditions
    are dropped or softened.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = [
        "CITY MUNICIPAL CORPORATION LEAVE POLICY SUMMARY",
        "===============================================",
        "This summary details the core binding obligations and conditions of the employee leave policy.",
        ""
    ]
    
    for clause_num in target_clauses:
        if clause_num in clauses:
            summary_lines.append(f"{clause_num}: {clauses[clause_num]}")
        else:
            # Fallback if clause is missing from source for some reason
            summary_lines.append(f"{clause_num}: [Error: Clause not found in source document]")
            print(f"Warning: Target clause {clause_num} not found in the policy document.", file=sys.stderr)
            
    return "\n".join(summary_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Employee Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary text file")
    args = parser.parse_args()
    
    print(f"Reading policy from: {args.input}")
    clauses = retrieve_policy(args.input)
    
    print("Generating summary...")
    summary = summarize_policy(clauses)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

