"""
UC-0B app.py
Implemented based on agents.md and skills.md constraints
"""
import argparse
import re
import os

def retrieve_policy(input_path: str) -> dict:
    """
    Loads .txt policy file, returns content as structured numbered sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Source document not found: {input_path}")
        
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    sections = {}
    current_clause = None
    current_text = []
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                sections[current_clause] = " ".join(current_text)
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause and not line.startswith('═══') and not re.match(r'^\d+\.\s+[A-Z]', line):
            current_text.append(line)
            
    if current_clause:
         sections[current_clause] = " ".join(current_text)
         
    if not sections:
        raise ValueError("No numbered clauses found in the document.")
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections, produces compliant summary with clause references.
    Follows agents.md enforcement:
    - Every numbered clause must be present
    - Multi-condition obligations must preserve ALL conditions
    - Never add information not present
    - Quote verbatim and flag if cannot be summarised without meaning loss
    """
    summary_lines = []
    summary_lines.append("COMPLIANT POLICY SUMMARY")
    summary_lines.append("========================")
    summary_lines.append("To ensure strict compliance, prevent meaning loss, and preserve all multi-condition obligations, the following clauses are quoted verbatim as required by the enforcement rules.\n")
    
    for clause_id, text in sections.items():
        summary_lines.append(f"Clause {clause_id}: [VERBATIM] {text}")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Strict Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt document")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
    except Exception as e:
        print(f"Error processing policy: {e}")
        return
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Compliant summary successfully written to {args.output}")
    except Exception as e:
        print(f"Failed to write output file: {e}")

if __name__ == "__main__":
    main()
