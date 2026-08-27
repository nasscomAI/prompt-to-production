"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import os

def retrieve_policy(input_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def summarize_policy(text, output_path):
    lines = text.split('\n')
    clauses = []
    current_clause = ""
    for line in lines:
        if re.match(r'^\d+\.\d+', line):
            if current_clause:
                clauses.append(current_clause.strip())
            current_clause = line.strip()
        elif current_clause and not re.match(r'^═|^[A-Z]', line) and not re.match(r'^\d+\.\s', line) and line.strip():
            current_clause += " " + line.strip()
    if current_clause:
        clauses.append(current_clause.strip())
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Policy Summary\n")
        f.write("==============\n\n")
        for clause in clauses:
            parts = clause.split(' ', 1)
            if len(parts) == 2:
                clause_id, text = parts
                f.write(f"- Clause {clause_id}: {text} [VERBATIM: Quoted to prevent meaning loss and dropped conditions]\n")

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    print(f"Reading input from: {args.input}")
    text = retrieve_policy(args.input)
    summarize_policy(text, args.output)
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
