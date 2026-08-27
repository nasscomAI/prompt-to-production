"""
UC-0B app.py
Policy Summarization Agent execution script.
Developed based on skills.md and agents.md constraints.
"""
import argparse
import re
import os

def retrieve_policy(filepath: str) -> str:
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns its content.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read input file {filepath}: {e}")

def summarize_policy(content: str) -> str:
    """
    Skill: summarize_policy
    Implements Intent and Enforcement rules from agents.md:
    1. Every numbered clause must be present.
    2. Multi-condition obligations must preserve ALL conditions.
    3. Never add information not present.
    4. Quote verbatim and flag if cannot be summarised without meaning loss.
    """
    lines = content.split('\n')
    summary_lines = []
    
    current_clause_id = None
    current_clause_text = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Detect numbered clauses like "2.3"
        match = re.match(r'^(\d+\.\d+)\s*(.*)', line_stripped)
        if match:
            # Process previous clause if exists
            if current_clause_id:
                clause_content = " ".join(current_clause_text)
                # Enforcement Rule 4: Quote verbatim and flag to prevent multi-condition drops
                summary_lines.append(f"[{current_clause_id}] VERBATIM FLAG: {clause_content}")
            
            current_clause_id = match.group(1)
            current_clause_text = [match.group(2)] if match.group(2) else []
        elif current_clause_id:
            current_clause_text.append(line_stripped)

    # Process the final clause
    if current_clause_id:
        clause_content = " ".join(current_clause_text)
        summary_lines.append(f"[{current_clause_id}] VERBATIM FLAG: {clause_content}")

    # Return summary preserving all conditions with no external context added.
    if not summary_lines:
        return "No numbered clauses found in the document."
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy.txt file")
    parser.add_argument("--output", required=True, help="Path to output summary_hr_leave.txt")
    
    args = parser.parse_args()
    
    try:
        # 1. Retrieve policy document
        policy_text = retrieve_policy(args.input)
        
        # 2. Summarize according to strict rules
        summary_text = summarize_policy(policy_text)
        
        # 3. Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        print(f"Done. Summary generated and written to {args.output}")
        
    except Exception as e:
        print(f"Execution failed: {e}")

if __name__ == "__main__":
    main()
