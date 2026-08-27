"""
UC-0B app.py — Policy Summarizer
"""
import argparse
import re
import sys

def retrieve_policy(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        print(f"Error accessing policy document: {e}")
        sys.exit(1)

def summarize_policy(lines):
    # We must extract specific clauses without dropping ANY conditions!
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    summary = ["# HR Leave Policy Summary\n", "This summary preserves ALL strict conditions and obligations.\n"]
    
    current_clause_num = None
    current_clause_text = []
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean: continue
        
        # Check if line starts with a target clause like "2.3 "
        match = re.match(r'^(\d\.\d)\s+(.*)', line_clean)
        
        if match:
            # Save the previous clause before we override it
            if current_clause_num in target_clauses:
                joined = " ".join(current_clause_text)
                summary.append(f"- Clause {current_clause_num}: {joined}")
                
            current_clause_num = match.group(1)
            current_clause_text = [match.group(2)]
        else:
            # It's a continuation line for an existing clause
            if current_clause_num and not line_clean.startswith("="):
                # Ignore random text that might not be part of the actual clause body (like headers)
                if current_clause_num in target_clauses and not re.match(r'^\d\.\s', line_clean):
                    current_clause_text.append(line_clean)
                    
    # Catch the final clause element
    if current_clause_num in target_clauses:
        joined = " ".join(current_clause_text)
        summary.append(f"- Clause {current_clause_num}: {joined}")
        
    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to output summary_hr_leave.txt")
    args = parser.parse_args()
    
    lines = retrieve_policy(args.input)
    summary_text = summarize_policy(lines)
    
    try:
        with open(args.output, "w", encoding='utf-8') as f:
            f.write(summary_text)
        print(f"Success! Summary correctly written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()
