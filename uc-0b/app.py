"""
UC-0B app.py — Policy Summarizer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re

def retrieve_policy(input_path: str) -> dict:
    """Loads .txt policy file, returns content as structured numbered sections."""
    clauses = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|\Z)', re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(content):
        clause_num = match.group(1)
        clause_text = match.group(2).replace('\n', ' ').strip()
        clause_text = re.sub(r'\s+', ' ', clause_text)
        clauses[clause_num] = clause_text
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """Takes structured sections, produces compliant summary with clause references."""
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    binding_verbs = ['must', 'will', 'forfeited', 'requires', 'not permitted', 'cannot', 'only']
    
    for clause_num, text in clauses.items():
        is_binding = any(verb in text.lower() for verb in binding_verbs)
        if is_binding:
            # According to our agents.md: "If a clause contains complex multi-part conditions that risk meaning loss if summarized, quote the clause verbatim and flag it with '[VERBATIM]'."
            summary_lines.append(f"Clause {clause_num}: [VERBATIM] {text}")
        else:
            summary_lines.append(f"Clause {clause_num}: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
