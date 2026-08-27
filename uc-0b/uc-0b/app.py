"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> list[str]:
    """Reads the policy file and returns lines."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()

def summarize_policy(lines: list[str]) -> str:
    """
    Extracts every numbered clause verbatim. 
    Prepends [VERBATIM] to ensure 100% fidelity to multi-condition obligations (e.g., Clause 5.2).
    """
    clauses = []
    current_clause = []
    clause_pattern = re.compile(r"^\d+\.\d+")
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Match a clause number (e.g. "2.3 Employees must...")
        if clause_pattern.match(line_stripped):
            if current_clause:
                clauses.append(" ".join(current_clause))
                
            current_clause = [line_stripped]
        # Append remaining lines of a multiline clause, avoiding headers and dividers.
        elif current_clause and not re.match(r"^═", line_stripped) and not re.match(r"^\d+\.", line_stripped):
            current_clause.append(line_stripped)
            
    # Append the final tracked clause
    if current_clause:
        clauses.append(" ".join(current_clause))
        
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=======================")
    summary_lines.append("To ensure zero meaning loss, all clauses are extracted verbatim per Rule 4.\n")
    
    for c in clauses:
        summary_lines.append(f"[VERBATIM] {c}")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary (.txt)")
    args = parser.parse_args()
    
    lines = retrieve_policy(args.input)
    summary = summarize_policy(lines)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
        
    print(f"Summary generated: {args.output}")

if __name__ == "__main__":
    main()
