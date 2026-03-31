"""
UC-0B app.py — Leave Policy Summarizer
Built according to agents.md and skills.md.
"""
import argparse
import re

def retrieve_policy(input_path: str) -> dict:
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    clauses = {}
    # Find all matches of X.Y followed by text, up to the next X.Y or = line
    pattern = r'(\d+\.\d+)\s+((?:(?!\d+\.\d+|═══).|\n)*)'
    matches = re.findall(pattern, text)
    
    for clause_num, clause_text in matches:
        # Clean up newlines for a continuous string
        clauses[clause_num] = " ".join(line.strip() for line in clause_text.strip().split('\n'))
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    # Strict list of clauses enforced by agents.md
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    
    summary_lines = []
    summary_lines.append("# HR Leave Policy Exact Summary\n")
    summary_lines.append("This summary precisely preserves all obligations and multi-condition requirements as per agents.md instructions:\n")
    
    for tc in target_clauses:
        if tc in clauses:
            # We output verbatim to ensure zero condition drops, obligation softening, or scope bleed.
            summary_lines.append(f"- Clause {tc}: {clauses[tc]}")
        else:
            summary_lines.append(f"- [OMISSION ERROR]: Clause {tc} could not be found.")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary_text = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error processing document: {e}")

if __name__ == "__main__":
    main()
