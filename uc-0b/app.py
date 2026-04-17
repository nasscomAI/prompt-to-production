import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Loads the .txt policy file and returns the content as structured numbered sections.
    """
    clauses = {}
    current_clause = None
    current_text = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Match things like "2.3 Employees must..."
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_clause:
                        clauses[current_clause] = " ".join(current_text)
                    current_clause = match.group(1)
                    current_text = [match.group(2)]
                elif current_clause and line and not line.startswith('═') and not re.match(r'^\d+\.', line):
                    current_text.append(line)
                    
        if current_clause:
            clauses[current_clause] = " ".join(current_text)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references.
    Ensures that no conditions are dropped. For high-risk clauses, we quote them verbatim to prevent meaning loss.
    """
    # These are the 10 critical clauses we must preserve according to the RICE enforcement
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=======================")
    summary_lines.append("This summary preserves critical binding obligations without dropping any conditions.\n")
    
    for c in target_clauses:
        if c in clauses:
            clause_text = clauses[c]
            # Since summarizing legal text runs the risk of condition dropping (e.g. dropping HR Director from 5.2),
            # we will quote them verbatim and flag it as requested by Enforcement Rule #4.
            summary_lines.append(f"Clause {c} (Verbatim Quote): {clause_text}")
        else:
            summary_lines.append(f"Clause {c}: [MISSING IN SOURCE DOCUMENT]")
            
    return "\n\n".join(summary_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write the summary (.txt)")
    args = parser.parse_args()
    
    # Execute skills
    policy_clauses = retrieve_policy(args.input)
    summary_text = summarize_policy(policy_clauses)
    
    # Save output
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text)
        
    print(f"Summary successfully written to {args.output}")
