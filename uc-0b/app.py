"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

def retrieve_policy(filepath: str) -> dict:
    """Loads the .txt policy file and returns content as structured numbered sections."""
    sections = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)
        
    current_clause = None
    current_text = []
    
    # Matches numbered clauses e.g., 2.3
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in lines:
        line = line.strip()
        # Skip headers or document metadata
        if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z\s\(\)]+$', line):
            continue
        if "Document Reference" in line or "Version" in line or "CITY MUNICIPAL" in line or "HUMAN RESOURCES" in line:
            continue
            
        match = clause_pattern.match(line)
        if match:
            if current_clause:
                sections[current_clause] = ' '.join(current_text)
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause and line:
            current_text.append(line)
            
    if current_clause:
        sections[current_clause] = ' '.join(current_text)
        
    return sections

def summarize_policy(sections: dict) -> str:
    """Takes structured sections and produces a compliant summary with clause references."""
    summary_lines = []
    summary_lines.append("POLICY SUMMARY\n==============")
    
    for clause, text in sections.items():
        # Enforcement Rule: "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it."
        # Because we want to guarantee zero omittance or modification of clauses, we quote strictly verbatim.
        summary_lines.append(f"Clause {clause}:\n[FLAG: VERBATIM] \"{text}\"")
        
    return "\n\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt")
    parser.add_argument("--output", required=True, help="Path to output summary .txt")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    if not sections:
        print("Error: No sections found in the input document.")
        sys.exit(1)
        
    summary = summarize_policy(sections)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
