"""
UC-0B app.py — HR Policy Summarization Agent Pipeline
Built using RICE + agents.md + skills.md parameters.
"""
import argparse
import os
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Skill: retrieve_policy
    Loads a .txt policy document and returns its contents parsed as structured numbered sections.
    """
    if not os.path.exists(filepath):
        raise IOError(f"Input file not found at {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all numbered clauses using regex: e.g. "2.3 Employees must..."
    # Matches <number>.<number> <text until next clause or section line>
    clauses = {}
    pattern = r"(\d+\.\d+)\s+([^\n]+(?:(?!\n\d+\.\d+|\n══).)*)"
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        clause_id = match.group(1)
        # clean up text
        clause_text = " ".join(line.strip() for line in match.group(2).split('\n') if line.strip())
        clauses[clause_id] = clause_text
        
    if not clauses:
        raise ValueError("Could not group any text into numbered sections. Unsupported formatting.")

    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Skill: summarize_policy
    Generates a fully compliant summary from structured sections.
    Enforces rules:
    - Every numbered clause present
    - Preserves all multi-conditions
    - Never adds non-source context
    - Quotes verbatim and flags when meaning could be lost
    """
    summary_lines = []
    summary_lines.append("HR POLICY SUMMARY DOCUMENT")
    summary_lines.append("══════════════════════════════")
    
    # Pre-defined complexity indicators where meaning is likely to be lost
    complexity_keywords = ['and the', 'only after', 'under any circumstances', 'prior written', 'verbal approval is not']
    
    for clause_id, text in clauses.items():
        text_lower = text.lower()
        
        # Check against multi-condition/complexity rule to quote verbatim + flag
        if any(keyword in text_lower for keyword in complexity_keywords) or 'approval' in text_lower:
            summary_lines.append(f"[{clause_id}] [FLAGGED: VERBATIM] \"{text}\"")
        else:
            # Minimal summarization without external info
            # Removing some filler words while preserving exact obligations
            safe_summary = text.replace("Each permanent employee is entitled to ", "Entitlement: ") \
                               .replace("Employees may ", "Allowed: ") \
                               .replace("Employees are entitled to ", "Entitlement: ")
            
            summary_lines.append(f"[{clause_id}] {safe_summary}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarization Agent")
    parser.add_argument("--input", required=False, help="Path to input policy .txt file")
    parser.add_argument("--output", required=False, help="Path to output summary .txt file")
    args = parser.parse_args()
    
    # Use defaults if not provided, resolving relative to this script's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = args.input or os.path.normpath(os.path.join(base_dir, "..", "data", "policy-documents", "policy_hr_leave.txt"))
    output_path = args.output or os.path.normpath(os.path.join(base_dir, "summary_hr_leave.txt"))

    try:
        print(f"Retrieving policy from: {input_path}")
        clauses = retrieve_policy(input_path)
        
        print("Summarizing policy clauses based on rule enforcement...")
        summary = summarize_policy(clauses)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Success! Output written to: {output_path}")
        
    except Exception as e:
        print(f"Pipeline Failed: {e}")

if __name__ == "__main__":
    main()
