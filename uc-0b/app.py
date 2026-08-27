"""
UC-0B app.py - Starter file replaced with rule-based implementation.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import sys
import re

# The specific clauses we are required to extract based on the assignment README.
TARGET_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7", 
    "3.2", "3.4", 
    "5.2", "5.3", 
    "7.2"
]

def retrieve_policy(file_path):
    """
    Skill: retrieve_policy
    Reads the raw text of the policy document from the file system.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def summarize_policy(content):
    """
    Skill: summarize_policy
    Parses the policy text and generates a strict, compliant summary of required clauses,
    ensuring no dropped conditions or scope bleed.
    """
    lines = content.split('\n')
    extracted_clauses = {}
    
    current_clause = None
    current_text = []
    
    # Parse the document line by line to extract numbered clauses
    for line in lines:
        # If we hit a section break, stop tracking the current clause
        if line.startswith('===='):
            if current_clause and current_clause in TARGET_CLAUSES:
                extracted_clauses[current_clause] = " ".join(current_text)
            current_clause = None
            current_text = []
            continue

        line_clean = line.strip()
        if not line_clean:
            continue
            
        # Match a clause number like "2.3" or "5.2" at the start of a line
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line_clean)
        
        if match:
            # Save previous clause if we were tracking one
            if current_clause and current_clause in TARGET_CLAUSES:
                extracted_clauses[current_clause] = " ".join(current_text)
                
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause and line.startswith('    '):
            # Append continuation lines to the current clause (they are indented)
            current_text.append(line_clean)
            
    # Don't forget the last clause
    if current_clause and current_clause in TARGET_CLAUSES:
        extracted_clauses[current_clause] = " ".join(current_text)
        
    # Build the strict summary
    summary_lines = []
    summary_lines.append("STRICT POLICY SUMMARY - HR LEAVE POLICY")
    summary_lines.append("="*50)
    
    for clause_num in TARGET_CLAUSES:
        if clause_num in extracted_clauses:
            text = extracted_clauses[clause_num]
            # Enforcement Rule 4: quote verbatim if meaning loss is possible
            summary_lines.append(f"Clause {clause_num}: {text}")
        else:
            summary_lines.append(f"Clause {clause_num}: [MISSING FROM SOURCE]")
            
    return "\n\n".join(summary_lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    # Apply skills
    raw_content = retrieve_policy(args.input)
    summary = summarize_policy(raw_content)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Summary generated successfully at {args.output}")

if __name__ == "__main__":
    main()
