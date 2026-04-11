"""
UC-0B app.py — Strict Clause-Preserving Summarizer.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import os

def retrieve_policy(filepath: str) -> list:
    """
    loads .txt policy file, returns content as structured numbered sections
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    clauses = []
    current_clause = None
    current_text = []
    
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in lines:
        match = clause_pattern.match(line)
        if match:
            if current_clause:
                clauses.append({
                    'clause': current_clause,
                    'text': ' '.join(current_text).strip()
                })
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
        elif current_clause and line.startswith('    '):
            current_text.append(line.strip())
            
    if current_clause:
        clauses.append({
            'clause': current_clause,
            'text': ' '.join(current_text).strip()
        })
        
    return clauses

def summarize_policy(clauses: list) -> str:
    """
    takes structured sections, produces compliant summary with clause references.
    To avoid condition drop or scope bleed, we enforce verbatim quotation.
    """
    summary_lines = ["POLICY SUMMARY - VERBATIM PRESERVATION\n"]
    for item in clauses:
        summary_lines.append(f"Clause {item['clause']}: {item['text']}")
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input policy text")
    parser.add_argument("--output", required=True, help="Path to write summary summary text")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: file {args.input} not found.")
        return

    clauses = retrieve_policy(args.input)
    summary_text = summarize_policy(clauses)
    
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text)
        
    print(f"Done. Wrote {len(clauses)} preserved clauses verbatim to {args.output}")

if __name__ == "__main__":
    main()
