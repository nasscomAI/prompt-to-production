"""
UC-0B app.py — Strict Legal Summarizer
"""
import argparse
import re
import sys

# The 10 critical clauses we must strictly preserve
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

def retrieve_policy(filepath: str) -> dict:
    """Reads a .txt policy file and parses it into structured numbered clauses."""
    clauses = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        lines = content.split('\n')
        current_clause = None
        clause_text = []
        
        for line in lines:
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_clause:
                    clauses[current_clause] = " ".join(clause_text).strip()
                current_clause = match.group(1)
                clause_text = [match.group(2).strip()]
            elif current_clause and line.strip() and not line.startswith('══') and not re.match(r'^\d+\.', line):
                clause_text.append(line.strip())
                
        if current_clause:
            clauses[current_clause] = " ".join(clause_text).strip()
            
        return clauses
    except FileNotFoundError:
        print(f"Error: Could not find '{filepath}'")
        sys.exit(1)

def summarize_policy(clauses: dict) -> str:
    """Produces a compliant, verbatim-heavy summary ensuring zero condition dropping."""
    summary_lines = []
    summary_lines.append("STRICT LEGAL SUMMARY: HR LEAVE POLICY")
    summary_lines.append("=====================================\n")
    
    summary_lines.append("This summary extracts critical obligations exactly as stated in the source document.")
    summary_lines.append("No external information or 'standard practices' have been added.\n")
    
    summary_lines.append("--- CORE OBLIGATIONS ---")
    
    for clause_id in REQUIRED_CLAUSES:
        if clause_id in clauses:
            text = clauses[clause_id]
            # Enforcement Rule 4: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it.
            summary_lines.append(f"Clause {clause_id} [VERBATIM QUOTE]: {text}")
        else:
            summary_lines.append(f"Clause {clause_id}: [ERROR - MISSING FROM SOURCE]")
            
    return "\n\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
        
    print(f"Done. Verbatim strict summary written to {args.output}")

if __name__ == "__main__":
    main()
