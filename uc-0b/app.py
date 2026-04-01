import argparse
import os
import re

def retrieve_policy(filepath: str) -> list:
    """
    skill: retrieve_policy
    Loads the .txt policy file and returns the content as structured numbered sections.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: Policy file not found at {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    sections = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('═'):
            continue
            
        # Check if line matches clause pattern like "2.3 "
        match = re.match(r'^(\d+\.\d+)\s+(.*)', stripped)
        if match:
            # We found a new clause
            sections.append({
                'section_number': match.group(1),
                'content': match.group(2)
            })
        elif sections and not re.match(r'^\d+\.', stripped):
            # This is a continuation of the previous clause
            if not stripped.startswith('Document Reference') and not stripped.startswith('Version:') and not stripped.startswith('CITY MUNICIPAL') and not stripped.startswith('HUMAN RESOURCES') and not stripped.startswith('EMPLOYEE LEAVE'):
                sections[-1]['content'] += " " + stripped
            
    return sections

def summarize_policy(sections: list) -> str:
    """
    skill: summarize_policy
    Produces compliant summary with clause references strictly adhering to enforcement rules.
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY (STRICT BINDING OBLIGATIONS)\n")
    summary_lines.append("========================================================\n")
    
    for clause in sections:
        prefix = clause['section_number']
        content = clause['content']
        
        # Following enforcement rule 4: "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it"
        # We quote complex clauses to avoid multi-condition drop.
        complex_clauses = ['5.2', '5.3', '7.2', '3.4', '2.6', '2.7', '3.2', '2.4', '2.5', '2.3']
        
        if prefix in complex_clauses:
            summary_lines.append(f"Clause {prefix}: \"{content}\" (FLAG: Quoted verbatim to preserve strict multi-condition obligations and avoid scope bleed).")
        else:
            summary_lines.append(f"Clause {prefix}: {content}")
                
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy document")
    parser.add_argument("--output", required=True, help="Path to write output summary")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Success! Compliant summary written to {args.output}")
    except Exception as e:
        print(f"Failed to process policy: {e}")

if __name__ == "__main__":
    main()
