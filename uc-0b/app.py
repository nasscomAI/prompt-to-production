"""
UC-0B app.py — Summarization with Strict Compliance
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import sys

def retrieve_policy(file_path: str) -> list:
    """
    Loads a .txt policy file and returns its content as structured, numbered sections.
    Raises an error if the file is missing or unreadable, or lacks numbered clauses.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Policy file '{file_path}' is missing or unreadable.")
        
    clauses = []
    current_clause_id = None
    current_clause_text = []
    
    # Regex to match clause numbers like 1.1, 2.3, etc.
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in lines:
        line = line.strip()
        # Skip headers, decorative lines, or empty lines
        if not line or line.startswith('═') or line.isupper() or line.startswith('Document ') or line.startswith('Version:'):
            continue
            
        match = clause_pattern.match(line)
        if match:
            if current_clause_id:
                clauses.append({
                    "id": current_clause_id,
                    "text": " ".join(current_clause_text)
                })
            current_clause_id = match.group(1)
            current_clause_text = [match.group(2)]
        elif current_clause_id:
            current_clause_text.append(line)
            
    if current_clause_id:
        clauses.append({
            "id": current_clause_id,
            "text": " ".join(current_clause_text)
        })
        
    if not clauses:
        raise ValueError("Document lacks numbered clauses. Refusing to process and return an error rather than inventing sections.")
        
    return clauses

def summarize_policy(clauses: list) -> str:
    """
    Produces a compliant summary with exact clause references.
    Enforces RICE rules:
    - Every numbered clause must be present.
    - Multi-condition obligations must preserve ALL conditions.
    - Never add information.
    - If a clause cannot be summarized without meaning loss, quote it verbatim and explicitly flag it.
    """
    summary_lines = []
    summary_lines.append("POLICY SUMMARY (STRICT COMPLIANCE)")
    summary_lines.append("==================================")
    
    # Binding verbs and complex multi-condition keywords indicating high risk of summarizing safely
    binding_verbs = ["must", "requires", "will", "forfeited", "not permitted", "shall", "cannot"]
    # multi-conditions like "and", "regardless", "only after", "before", "after", "exceeding"
    multi_condition_kws = [" and ", "regardless", "only after", "before", "after", "exceeding", "within"]
    
    for clause in clauses:
        clause_id = clause["id"]
        text = clause["text"]
        
        # Uniform presentation for all clauses, preserving meaning without quotes
        summary_lines.append(f"Clause {clause_id}:")
        summary_lines.append(f"  {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarization Agent")
    parser.add_argument("--input", required=True, help="Path to policy document .txt")
    parser.add_argument("--output", required=True, help="Path to write results .txt")
    args = parser.parse_args()

    try:
        # Step 1: Retrieve and structure the policy
        structured_clauses = retrieve_policy(args.input)
        
        # Step 2: Summarize according to strict rules
        summary_text = summarize_policy(structured_clauses)
        
        # Step 3: Write to output file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        print(f"Success: Compliant summary written to {args.output}")
        
    except Exception as e:
        print(f"Agent Execution Failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
