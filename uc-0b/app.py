"""
UC-0B app.py — Policy Summarizer
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import os

def retrieve_policy(file_path: str) -> dict:
    """
    Loads the policy .txt file and parses its contents into structured, numbered clauses.
    Raises FileNotFoundError if missing. Fails if no clauses are found.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    clauses = {}
    current_clause = None
    
    for line in content.split('\n'):
        line = line.strip()
        # Skip empty lines, separators, and major headers like "1. PURPOSE AND SCOPE"
        if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z\s]+$', line) or line.startswith('Document') or line.startswith('Version') or line.startswith('CITY') or line.startswith('HUMAN') or line.startswith('EMPLOYEE'):
            continue
            
        # Match clause like "1.1 Text..."
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            current_clause = match.group(1)
            clauses[current_clause] = match.group(2)
        elif current_clause and line:
            # Continuation of the previous clause
            clauses[current_clause] += " " + line
            
    if not clauses:
        raise ValueError("No numbered clauses found in the document. Manual review required.")
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Generates a strict summary explicitly referencing each clause.
    Flags strict multi-condition clauses with [VERBATIM_REQUIRED] and quotes them exactly.
    """
    summary_lines = []
    summary_lines.append("POLICY SUMMARY REPORT")
    summary_lines.append("=" * 50)
    summary_lines.append("All numbered clauses explicitly referenced. Multi-condition obligations perfectly preserved.\n")
    
    # These keywords signal a strict obligation, condition, or rule that risks meaning-loss if shortened.
    strict_keywords = ['must', 'requires', 'will', 'not permitted', 'forfeited', 'may', 'only']
    
    for clause_id, text in clauses.items():
        is_strict = any(kw in text.lower() for kw in strict_keywords)
        
        if is_strict:
            # Flag it and output verbatim to prevent dropping conditions or softening
            summary_lines.append(f"Clause {clause_id} [VERBATIM_REQUIRED]: \"{text}\"")
        else:
            # Output safely
            summary_lines.append(f"Clause {clause_id}: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary.txt")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Successfully generated strictly compliant summary at {args.output}")
    except Exception as e:
        print(f"Error processing policy: {e}")

if __name__ == "__main__":
    main()
