"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import os

def retrieve_policy(file_path: str) -> dict:
    """
    Loads .txt policy file, returns content as structured numbered sections
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
        
    clauses = {}
    with open(file_path, mode="r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Check for section header or divider to close current clause accumulation
        if stripped.startswith('═') or re.match(r'^\d+\.\s+[A-Z]', stripped):
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = None
            current_text = []
            continue
            
        # Check for clause start e.g. "2.3"
        match = re.match(r'^(\d+\.\d+)\s+(.*)', stripped)
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2)]
        else:
            if current_clause:
                current_text.append(stripped)
                    
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured sections, produces compliant summary with clause references
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = [
        "═══════════════════════════════════════════════════════════",
        "CMC EMPLOYEE LEAVE POLICY - SUMMARY OF BINDING OBLIGATIONS",
        "═══════════════════════════════════════════════════════════",
        ""
    ]
    
    for clause_num in target_clauses:
        if clause_num in clauses:
            text = clauses[clause_num]
            # Since summarizing might drop conditions, we quote verbatim and flag to satisfy rule 4.
            summary_lines.append(f"Clause {clause_num} [VERBATIM OBLIGATION]: {text}")
        else:
            summary_lines.append(f"Clause {clause_num}: [Warning: Clause not found in source policy document]")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Employee Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary txt")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    
    with open(args.output, mode="w", encoding="utf-8") as out:
        out.write(summary)
        
    print(f"Summary successfully written to {args.output}")

if __name__ == "__main__":
    main()

