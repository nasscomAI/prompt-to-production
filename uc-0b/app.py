"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

TARGET_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt policy document and returns the content parsed into structured, numbered sections.
    Returns a dictionary mapping clause numbers (e.g., "2.3") to their exact text.
    """
    clauses = {}
    current_clause = None
    
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                    
                match = clause_pattern.match(line)
                if match:
                    # New clause starts
                    current_clause = match.group(1)
                    clauses[current_clause] = match.group(2)
                elif current_clause and (line.startswith(' ') or line.startswith('\t')):
                    # Continuation of current clause
                    clauses[current_clause] += " " + line_stripped
    except FileNotFoundError:
        print(f"Error: Could not find file {filepath}")
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured clauses and produces a compliant summary preserving all required clauses and multi-part conditions.
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=" * 40)
    summary_lines.append("")
    
    for clause_id in TARGET_CLAUSES:
        if clause_id in clauses:
            text = clauses[clause_id]
            # Since these specific clauses contain complex, multi-part conditions (e.g. Department Head AND HR Director approval),
            # any attempt to shorten them programmatically risks losing meaning.
            # Following the strict enforcement rule, we quote them verbatim and flag them.
            summary_lines.append(f"Clause {clause_id} [VERBATIM]: {text}")
        else:
            summary_lines.append(f"Clause {clause_id}: [ERROR - NOT FOUND IN SOURCE]")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to save the summary")
    
    args = parser.parse_args()
    
    structured_sections = retrieve_policy(args.input)
    
    if not structured_sections:
        print("No clauses retrieved. Exiting.")
        return
        
    summary = summarize_policy(structured_sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Summary successfully written to {args.output}")

if __name__ == "__main__":
    main()
