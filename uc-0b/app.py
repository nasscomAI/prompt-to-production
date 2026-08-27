"""
UC-0B app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import os

CLAUSE_INVENTORY = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']

def parse_policy(file_path):
    clauses = {}
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found at {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Locate each clause by finding lines starting with "X.Y "
    # We clean up multiple spaces and newlines
    pattern = re.compile(r'^\s*([1-9]\.[0-9]+)\s+(.*?)(?=(?:^\s*[1-9]\.[0-9]+\s+)|\Z)', re.MULTILINE | re.DOTALL)
    matches = pattern.findall(content)
    for clause_num, clause_text in matches:
        clean_text = " ".join(clause_text.split())
        if '═══' in clean_text:
            clean_text = clean_text.split('═══')[0].strip()
        clauses[clause_num] = clean_text
        
    return clauses

def main():
    parser = argparse.ArgumentParser(description="UC-0B Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary text file")
    args = parser.parse_args()
    
    clauses = parse_policy(args.input)
    
    summary_lines = []
    summary_lines.append("=== POLICY LEAVE SUMMARY (UC-0B) ===")
    summary_lines.append("Strictly summarized key clauses from HR Leave Policy (HR-POL-001 v2.3):\n")
    
    for clause in CLAUSE_INVENTORY:
        text = clauses.get(clause, "")
        if not text:
            summary_lines.append(f"Clause {clause}: [MISSING IN SOURCE]")
            continue
        
        # We quote verbatim to ensure no clause details or multi-condition approvals (like 5.2) are dropped.
        summary_lines.append(f"Clause {clause} [VERBATIM]: {text}")
        
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary_lines))
        
    print(f"Summary written successfully to {args.output}")

if __name__ == "__main__":
    main()
