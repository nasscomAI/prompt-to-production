"""
UC-0B app.py — HR Policy Summarizer
Implemented using the RICE constraints from agents.md and skills from skills.md.
"""
import argparse
import os
import re

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and parses it into structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
        
    sections = {}
    current_section = None
    current_text = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines, decorative dividers, and main headers
            if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z\s]+$', line):
                continue
                
            # Match clause numbers like "1.1", "2.3"
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_section:
                    sections[current_section] = " ".join(current_text)
                current_section = match.group(1)
                current_text = [match.group(2)]
            elif current_section:
                current_text.append(line)
                
    if current_section:
        sections[current_section] = " ".join(current_text)
        
    if not sections:
        raise ValueError("No numbered sections could be parsed from the file.")
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured policy sections and produces a compliant summary.
    Preserves all clauses and multi-condition obligations.
    """
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    # Keywords indicating a strict obligation or multi-condition rule
    strict_keywords = ["must", "requires", "will", "forfeited", "not permitted", "only after", "cannot"]
    
    for clause_num, text in sections.items():
        text_lower = text.lower()
        is_strict = any(kw in text_lower for kw in strict_keywords)
        
        if is_strict:
            # Cannot be confidently summarized without losing meaning/conditions -> quote verbatim & flag
            summary_lines.append(f"Clause {clause_num} [VERBATIM FLAG - STRICT OBLIGATION]: {text}")
        else:
            # Include explicitly as a direct statement
            summary_lines.append(f"Clause {clause_num}: {text}")
            
    return "\n\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
