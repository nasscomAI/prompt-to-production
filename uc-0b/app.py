"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
"""
UC-0B app.py — Policy Summarizer
"""
import argparse
import re

def retrieve_policy(input_path: str) -> str:
    with open(input_path, 'r', encoding='utf-8') as f:
        return f.read()

def summarize_policy(text: str) -> str:
    clauses_to_extract = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    summary_lines = ["# Employee Leave Policy Summary\n"]
    
    # Simple regex to find clauses
    for clause_num in clauses_to_extract:
        # Match from the clause number until the next clause number or an empty line/separator
        pattern = rf"^({clause_num}\s+.*?)(?=\n\d\.\d|\n═|\n\n|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
        if match:
            # Clean up newlines for a readable summary
            clause_text = match.group(1).replace('\n    ', ' ').strip()
            # To ensure no conditions are dropped, we follow the agent rule: quote verbatim and flag it.
            summary_lines.append(f"- Clause {clause_text} [VERBATIM_PRESERVED]")
        else:
            summary_lines.append(f"- Clause {clause_num}: [NOT FOUND]")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    policy_text = retrieve_policy(args.input)
    summary = summarize_policy(policy_text)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
