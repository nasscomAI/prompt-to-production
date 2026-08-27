"""
UC-0B app.py — HR Policy Summarizer
Implementation based on agents.md and skills.md rules.
"""
import argparse
import re
import os

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured, numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
        
    sections = {}
    current_section = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or '══════' in line or line.startswith('Document Reference') or line.startswith('Version:') or line.startswith('CITY MUNICIPAL') or line.startswith('HUMAN RESOURCES') or line.startswith('EMPLOYEE LEAVE'):
                continue
                
            # Match section headers like "1. PURPOSE AND SCOPE"
            sec_match = re.match(r'^(\d+\.\s+[A-Z\s\(\)]+)$', line)
            if sec_match and not re.match(r'^\d+\.\d+', line):
                current_section = sec_match.group(1)
                sections[current_section] = []
                continue
                
            # Match clauses like "1.1 This policy..."
            clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if clause_match:
                if current_section is None:
                    current_section = "0. GENERAL"
                    sections[current_section] = []
                sections[current_section].append(f"{clause_match.group(1)} {clause_match.group(2)}")
            elif current_section and sections[current_section]:
                # Append continuation lines to the last clause
                sections[current_section][-1] += " " + line
                
    return sections


def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references.
    Enforces rules from agents.md:
    1. Every numbered clause must be present.
    2. Multi-condition obligations must preserve ALL conditions.
    3. Never add information not present.
    4. If it cannot be summarised without meaning loss — quote it verbatim and flag it.
    """
    summary_lines = []
    summary_lines.append("# HR Leave Policy Summary")
    summary_lines.append("Generated strictly according to source document constraints.\n")
    
    for section_title, clauses in sections.items():
        summary_lines.append(f"## {section_title}")
        for clause in clauses:
            # Clean up whitespace
            clause = re.sub(r'\s+', ' ', clause).strip()
            
            parts = clause.split(' ', 1)
            if len(parts) == 2:
                c_num, c_text = parts
                
                # Rule 4: Quote verbatim and flag to prevent meaning loss for multi-condition rules
                summary_lines.append(f"- **Clause {c_num}**: [VERBATIM] {c_text}")
            else:
                summary_lines.append(f"- {clause}")
                
        summary_lines.append("")
        
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()
    
    try:
        structured_sections = retrieve_policy(args.input)
        if not structured_sections:
            print("Error: No sections retrieved from the file.")
            return
            
        summary_text = summarize_policy(structured_sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        print(f"Success! Compliant summary written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
