"""
UC-0B app.py — Policy Summarizer.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import sys

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a policy text file and parses its contents into structured numbered sections.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading policy file: {e}")
        sys.exit(1)

    clauses = {}
    current_clause = None
    current_text = []
    
    for line in content.splitlines():
        # Match a line starting with digit.digit
        match = re.match(r'^\s*(\d+\.\d+)\s+(.*)$', line)
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2)]
        else:
            if current_clause:
                # Check if line is empty or is a header line like ═══
                if line.strip().startswith('═══') or re.match(r'^\s*\d+\.\s+[A-Z]', line):
                    clauses[current_clause] = " ".join(current_text).strip()
                    current_clause = None
                    current_text = []
                else:
                    current_text.append(line.strip())
                    
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured policy sections and produces a compliant summary that explicitly preserves critical clauses.
    """
    critical_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = [
        "CMC Employee Leave Policy - Critical Clauses Summary",
        "==================================================",
        "All critical clauses have been extracted verbatim to prevent any obligation softening,",
        "condition dropping, or meaning loss.",
        ""
    ]
    for clause in critical_clauses:
        if clause in clauses:
            text = clauses[clause]
            summary_lines.append(f"Clause {clause}: \"{text}\" [VERBATIM]")
        else:
            summary_lines.append(f"Clause {clause}: [MISSING IN SOURCE]")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing summary to file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
