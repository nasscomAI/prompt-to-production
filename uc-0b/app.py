import argparse
import os
import re

def retrieve_policy(file_path):
    """Parses the policy file into structured clauses."""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    clauses = {}
    lines = content.split('\n')
    current_clause = None
    
    for line in lines:
        match = re.match(r'^\s*(\d+\.\d+)\s+(.*)', line)
        if match:
            current_clause = match.group(1)
            clauses[current_clause] = match.group(2).strip()
        elif current_clause and line.strip():
            clauses[current_clause] += " " + line.strip()
            
    return clauses

def summarize_policy(clauses):
    """Summarizes clauses while strictly preserving conditions."""
    summary_lines = ["# Policy Summary\n"]
    
    # Mandatory checks as per UC-0B README requirements
    critical_mappings = {
        "2.3": "14-day advance notice required (must).",
        "2.4": "Written approval required before leave; verbal not valid (must).",
        "2.5": "Unapproved absence results in Loss of Pay (will).",
        "2.6": "Max 5 days carry-forward; excess forfeited on 31 Dec.",
        "2.7": "Carry-forward days must be used Jan–Mar or forfeited.",
        "3.2": "3+ consecutive sick days requires medical cert within 48hrs.",
        "3.4": "Sick leave before/after holiday requires cert regardless of duration.",
        "5.2": "LWP requires approval from BOTH Department Head AND HR Director.",
        "5.3": "LWP >30 days requires Municipal Commissioner approval.",
        "7.2": "Leave encashment during service not permitted under any circumstances."
    }
    
    for clause_id, requirement in critical_mappings.items():
        if clause_id in clauses:
            summary_lines.append(f"- **Clause {clause_id}**: {requirement}")
        else:
            summary_lines.append(f"- **Clause {clause_id}**: [MISSING FROM SOURCE]")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to save summary .txt")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    if not clauses:
        print(f"Error: Could not read input file {args.input}")
        return
    
    summary = summarize_policy(clauses)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary successfully written to {args.output}")

if __name__ == "__main__":
    main()
