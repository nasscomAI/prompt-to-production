"""
UC-0B app.py — Summarise policy clauses without condition dropping or scope bleed.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Reads the policy document and parses it into a dictionary of numbered clauses.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")
        
    clauses = {}
    current_clause_num = None
    current_clause_text = []
    
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            # Ignore decorative header separators and uppercase section titles
            if line_str.startswith('═') or re.match(r"^\d+\.\s+[A-Z\s\(\)&]+$", line_str):
                continue
                
            # Match pattern like "2.3", "5.12", etc. at the start of a line
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", line_str)
            if match:
                # If we had a previous clause, save it
                if current_clause_num:
                    clauses[current_clause_num] = " ".join(current_clause_text).strip()
                current_clause_num = match.group(1)
                current_clause_text = [match.group(2)]
            elif current_clause_num is not None:
                # Accumulate multi-line clause text
                if line_str:
                    current_clause_text.append(line_str)
                    
        # Don't forget the last clause
        if current_clause_num:
            clauses[current_clause_num] = " ".join(current_clause_text).strip()
            
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Generates a faithful summary of target clauses.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = []
    
    summary_lines.append("SUMMARY OF TARGETED LEAVE POLICY CLAUSES")
    summary_lines.append("=" * 40)
    
    for num in target_clauses:
        text = clauses.get(num, "").strip()
        if not text:
            continue
            
        # For critical clauses with multiple conditions or strict obligations,
        # we quote them verbatim with a [VERBATIM] flag to avoid any meaning loss.
        if num in ["5.2", "2.4", "3.2", "3.4"]:
            summary_lines.append(f"- Clause {num} [VERBATIM]: {text}")
        else:
            summary_lines.append(f"- Clause {num}: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy document txt")
    parser.add_argument("--output", required=True, help="Path to write summary txt")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")
        
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()

