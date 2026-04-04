"""
UC-0B app.py — Deterministic Verbatim Summarizer.
Built strictly according to RICE + agents.md rules.
"""
import argparse
import re
import sys

def retrieve_policy(input_path: str) -> list:
    """Read the policy and extract only the relevant numbered clauses."""
    clauses = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_clause = []
        for line in lines:
            line_stripped = line.strip()
            # Match clause beginnings like "2.1 "
            if re.match(r'^\d+\.\d+\s+', line_stripped):
                if current_clause:
                    clauses.append(" ".join(current_clause))
                current_clause = [line_stripped]
            # Capture continuation lines, avoiding headers and section breaks
            elif current_clause and line_stripped and not line.startswith('══') and not re.match(r'^\d+\.\s+[A-Z]', line_stripped) and not line.startswith('Document Reference') and not line.startswith('Version:'):
                current_clause.append(line_stripped)
                
        if current_clause:
            clauses.append(" ".join(current_clause))
            
        return clauses
    except IOError as e:
        print(f"Error reading file: {e}")
        return []

def summarize_policy(clauses: list) -> str:
    """Summarize by preserving all conditions verbatim to prevent condition drops."""
    summary_lines = ["# STRICT POLICY SUMMARY (VERBATIM ADHERENCE)", ""]
    for clause in clauses:
        # Rule 4 from README: quote verbatim to avoid losing meaning or dropping sub-conditions
        summary_lines.append(f"[VERBATIM REQUIRED] {clause}")
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    if not clauses:
        print("Failed to retrieve policy clauses.")
        sys.exit(1)
        
    summary = summarize_policy(clauses)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
