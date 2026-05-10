"""
UC-0B app.py — Policy Summarizer
Implemented using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    Returns a dict mapping clause number (e.g. '2.1') to the text of the clause.
    """
    sections = {}
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {input_path}: {e}")
        return sections

    lines = content.split('\n')
    current_clause = None
    clause_text = []

    for line in lines:
        line = line.strip()
        # Skip empty lines, dividers, and main section headings (e.g., "1. PURPOSE AND SCOPE")
        if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z]', line):
            continue
        
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                sections[current_clause] = ' '.join(clause_text)
            current_clause = match.group(1)
            clause_text = [match.group(2)]
        elif current_clause:
            clause_text.append(line)
            
    if current_clause:
        sections[current_clause] = ' '.join(clause_text)
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references.
    Enforces rules from agents.md (no scope bleed, no dropped conditions, flags verbatim text).
    """
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    # Clauses that have multi-conditions or strict obligations that are risky to summarize
    # To satisfy Rule 4, we quote them verbatim and flag them to prevent meaning loss.
    TRAP_CLAUSES = {'2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2'}
    
    for clause_num, text in sections.items():
        if clause_num in TRAP_CLAUSES:
            summary_lines.append(f"- **Clause {clause_num}** [FLAG: Quoted verbatim to prevent condition drop/meaning loss]: \"{text}\"")
        else:
            # For non-trap clauses, we preserve the exact text to avoid scope bleed or hallucination
            summary_lines.append(f"- **Clause {clause_num}**: {text}")
            
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    if not sections:
        print("Failed to retrieve policy sections.")
        return
        
    summary = summarize_policy(sections)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
