"""
UC-0B app.py — Legal Policy Summarization
Implementation based strictly on agents.md (RICE enforcement) and skills.md.
"""
import argparse
import os
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Skill: retrieve_policy
    Loads a .txt policy file and parses its contents into structured, numbered sections.
    """
    if not os.path.exists(filepath):
        print(f"Error: Could not read {filepath}")
        return {}

    if not filepath.endswith('.txt'):
        print("Error: Input file must be a .txt document")
        return {}
        
    structured_sections = {}
    current_clause = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('═') or line.startswith('Document') or line.startswith('Version') or line == 'CITY MUNICIPAL CORPORATION' or line == 'HUMAN RESOURCES DEPARTMENT' or line == 'EMPLOYEE LEAVE POLICY':
                continue
                
            # Check for section header like "1. PURPOSE AND SCOPE"
            header_match = re.match(r'^(\d+)\.\s+([A-Z\s]+)$', line)
            if header_match:
                continue # We can ignore main headers for the breakdown of clauses
                
            # Check for numbered clause like "1.1 This policy..."
            clause_match = re.match(r'^(\d+\.\d+)\s+(.*)$', line)
            if clause_match:
                current_clause = clause_match.group(1)
                structured_sections[current_clause] = clause_match.group(2)
            elif current_clause:
                # Continuation of the previous clause
                structured_sections[current_clause] += " " + line
                
    if not structured_sections:
        print("Error: No discernible numbered clause structure found.")
        return {}
        
    return structured_sections

def summarize_policy(structured_sections: dict) -> str:
    """
    Skill: summarize_policy
    Generates a plain-text summary from structured sections while preserving every condition
    and obligation verbatim, prefixing complex clauses with [VERBATIM].
    """
    summary_lines = []
    summary_lines.append("HR POLICY SUMMARY")
    summary_lines.append("-" * 50)
    
    for clause_id, content in structured_sections.items():
        # As per agents.md: "Multi-condition obligations must preserve ALL conditions verbatim...
        # Quote it verbatim and flag it with [VERBATIM] in the summary"
        
        # We identify complex, binding clauses (those with 'must', 'requires', 'AND', 'or', 'not permitted')
        is_complex = any(keyword in content for keyword in ['must', 'requires', 'AND', 'or', 'not permitted', 'LWP', 'forfeited', 'will'])
        
        if is_complex:
            summary_lines.append(f"Clause {clause_id} [VERBATIM]: {content}")
        else:
            summary_lines.append(f"Clause {clause_id}: {content}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Legal Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input .txt policy document")
    parser.add_argument("--output", required=True, help="Path to save the plain-text summary")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    if not sections:
        print("Failed to parse policy document.")
        return
        
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Summary successfully generated at {args.output}")

if __name__ == "__main__":
    main()
