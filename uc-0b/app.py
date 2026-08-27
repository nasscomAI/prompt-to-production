"""
UC-0B app.py — Policy Summarizer
Build based on agents.md and skills.md workflow.
"""
import argparse
import re
import sys
import os

class ParseError(Exception):
    pass

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a policy text file and parses it into a structured format of numbered sections.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")
        
    structured_sections = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('═══') or re.match(r'^\d+\.\s+[A-Z\s]+', stripped):
            continue
            
        match = clause_pattern.match(stripped)
        if match:
            if current_clause:
                structured_sections[current_clause] = ' '.join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause and stripped:
            current_text.append(stripped)
            
    if current_clause:
        structured_sections[current_clause] = ' '.join(current_text).strip()
        
    if not structured_sections:
        raise ParseError("Document lacks expected clause numbering.")
        
    return structured_sections


def summarize_policy(structured_sections: dict) -> str:
    """
    Takes structured sections, produces compliant summary with clause references.
    Ensures zero loss of binding obligations, conditions, or specific approver requirements.
    """
    summary_lines = [
        "POLICY SUMMARY",
        "==============",
        "Role: Policy Summary Specialist",
        "Intent: Verifiable summary against original clause inventory.",
        ""
    ]
    
    for clause, text in structured_sections.items():
        lower_text = text.lower()
        
        # Enforce Rule: Quote verbatim and flag if meaning would be lost/softened
        # Multi-condition obligations (e.g., dual approvals), strict bans, and rigid conditions.
        is_critical = False
        
        # Dual approvers
        if "and" in lower_text and ("approv" in lower_text or "requir" in lower_text):
            is_critical = True
        # Strict constraints
        elif "not permitted" in lower_text or "under any circumstances" in lower_text or "not valid" in lower_text:
            is_critical = True
        # Forfeiture rules
        elif "forfeit" in lower_text or "regardless" in lower_text:
            is_critical = True
            
        if is_critical:
            summary_lines.append(f"[Clause {clause}] CRITICAL OBLIGATION:")
            summary_lines.append(f'"{text}"')
            summary_lines.append("")
        else:
            summary_lines.append(f"[Clause {clause}] {text}")
            summary_lines.append("")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary text file")
    
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summary successfully written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
