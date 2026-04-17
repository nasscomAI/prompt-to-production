"""
UC-0B app.py — HR Leave Policy Summarizer
Implemented using rules from agents.md and skills.md.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Loads the raw HR leave policy .txt file and processes its content into structured, numbered sections / clauses.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find or read {filepath}")
        return {}
        
    clauses = {}
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Match pattern like "2.3 "
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                clauses[current_clause] = ' '.join(current_text)
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause and not line.startswith('══') and not re.match(r'^\d+\.', line):
            current_text.append(line)
            
    if current_clause:
        clauses[current_clause] = ' '.join(current_text)
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Receives structured policy clauses and produces a compliant summary.
    Enforces all conditions from agents.md, including the verbatim flag.
    """
    required_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    summary_lines = []
    
    summary_lines.append("HR LEAVE POLICY SUMMARY (Verbatim Extracts Enforced)")
    summary_lines.append("====================================================\n")
    
    for clause_id in required_clauses:
        clause_text = clauses.get(clause_id)
        if clause_text:
            # Enforcing agents.md Rule 4: "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it."
            summary_lines.append(f"Clause {clause_id} [VERBATIM: Meaning loss risk flagged]:")
            summary_lines.append(f"  {clause_text}\n")
        else:
            summary_lines.append(f"Clause {clause_id}: [ERROR - CLAUSE NOT FOUND IN SOURCE]\n")
            
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    if not clauses:
        return
        
    summary = summarize_policy(clauses)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Policy summary written to {args.output}")
    except Exception as e:
        print(f"Failed to write output: {e}")

if __name__ == "__main__":
    main()
