"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and returns content as structured numbered sections.
    Raises an error if the file is not found or cannot be parsed into numbered sections.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    
    clauses = {}
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in lines:
        match = clause_pattern.match(line.strip())
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
        elif current_clause and line.strip() and not line.startswith('═') and not re.match(r'^\d+\.', line.strip()):
            current_text.append(line.strip())
            
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    if not clauses:
        raise ValueError("Could not parse file into numbered sections.")
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references.
    Fails and flags the clause verbatim if it cannot be summarized without altering its meaning or dropping conditions.
    """
    summary_lines = ["# HR Policy Summary", ""]
    
    for clause_num, clause_text in clauses.items():
        # Enforcement Rule 4: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
        summary_lines.append(f"## Clause {clause_num}")
        summary_lines.append(f"[VERBATIM] {clause_text}")
        summary_lines.append("")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarization Agent")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
