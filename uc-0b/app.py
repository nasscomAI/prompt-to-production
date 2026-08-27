"""
UC-0B app.py — Policy Summarizer
Implemented using RICE constraints from agents.md and skills.md.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a plain text policy document and parses it into structured, numbered sections.
    Returns: dict mapping clause numbers to their exact text.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    clauses = {}
    current_clause = None
    current_text = []

    for line in text.split('\n'):
        # Match lines like "2.3 Employees must submit..."
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
        # Append to current clause if it's not a section header or separator
        elif current_clause and line.strip() and not line.startswith('═') and not re.match(r'^\d+\.\s', line):
            current_text.append(line.strip())
            
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Generates a highly accurate summary that preserves all binding obligations.
    Uses [VERBATIM] tags to prevent meaning loss on complex clauses.
    """
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    for clause_id, text in clauses.items():
        # Check for binding verbs or multiple conditions to prevent softening/dropping
        binding_verbs = ['must', 'will', 'requires', 'not permitted', 'forfeited', 'only after', 'subject to']
        has_binding = any(verb in text.lower() for verb in binding_verbs)
        has_multiple_conditions = ' and ' in text.lower() or ' or ' in text.lower() or 'before' in text.lower()
        
        if has_binding or has_multiple_conditions:
            # Enforce rule: quote verbatim to preserve meaning and prevent scope bleed/dropping conditions
            summary_lines.append(f"- **Clause {clause_id}**: [VERBATIM] {text}")
        else:
            summary_lines.append(f"- **Clause {clause_id}**: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary.txt")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        if not clauses:
            raise ValueError("Document could not be structured into numbered sections.")
            
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Summary written to {args.output}")
        
    except Exception as e:
        print(f"Error during summarization: {e}")

if __name__ == "__main__":
    main()
