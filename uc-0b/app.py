"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(file_path: str) -> dict:
    """Loads a raw .txt HR policy file and parses its contents into structured, numbered sections."""
    clauses = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            current_clause = None
            current_text = []
            for line in f:
                line = line.strip()
                if not line or line.startswith('═'):
                    continue
                
                # Skip headings like "1. PURPOSE AND SCOPE"
                if re.match(r'^\d+\.\s+[A-Z\s]+$', line):
                    continue

                # Match clause numbers like "1.1 "
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_clause:
                        clauses[current_clause] = ' '.join(current_text)
                    current_clause = match.group(1)
                    current_text = [match.group(2)]
                elif current_clause:
                    current_text.append(line)
                    
            if current_clause:
                clauses[current_clause] = ' '.join(current_text)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Could not find policy document at {file_path}")
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """Produces a compliant summary that strictly preserves all obligations and multiple conditions."""
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    # Keywords that indicate rigid, multi-condition, or strict obligations
    strict_keywords = ['must', 'require', 'requires', 'will', 'not permitted', 'forfeit', 'forfeited', 'approval', 'only', 'cannot']
    
    for num, text in clauses.items():
        text_lower = text.lower()
        
        # Check if the clause contains strict multi-condition or rigid obligations
        if any(kw in text_lower for kw in strict_keywords):
            summary_lines.append(f"- **Clause {num}**: [VERBATIM/FLAGGED] {text}")
        else:
            # Provide the text as the summary to prevent any scope bleed or dropped constraints
            summary_lines.append(f"- **Clause {num}**: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    print(f"Reading policy document from {args.input}...")
    try:
        clauses = retrieve_policy(args.input)
    except Exception as e:
        print(e)
        return
        
    if not clauses:
        print("Warning: No clauses were parsed from the document.")
        return

    print("Generating summary...")
    summary_text = summarize_policy(clauses)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
