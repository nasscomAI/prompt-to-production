"""
UC-0B app.py — HR Leave Policy Summarizer
Implemented using RICE framework rules from agents.md and skills.md.
"""
import argparse
import os
import re
import sys

def retrieve_policy(file_path: str) -> list:
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns its content organized into structured, numbered sections.
    """
    if not os.path.exists(file_path):
        print(f"Error: Input file {file_path} not found.")
        sys.exit(1)
        
    sections = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_clause_id = None
    current_clause_text = []

    # Regex to match clause numbers like "2.3" or "3.1"
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('═') or line.isupper():
            # Skip empty lines, separators, and headings
            continue
            
        clause_match = re.match(clause_pattern, line)
        if clause_match:
            # Save the previous clause
            if current_clause_id:
                sections.append({
                    "id": current_clause_id,
                    "text": " ".join(current_clause_text)
                })
            
            # Start new clause
            current_clause_id = clause_match.group(1)
            current_clause_text = [clause_match.group(2).strip()]
        else:
            # Append to current clause if it's a continuation
            if current_clause_id:
                current_clause_text.append(line)
                
    # Append the last clause
    if current_clause_id:
         sections.append({
            "id": current_clause_id,
            "text": " ".join(current_clause_text)
        })       

    if not sections:
        print("Error: Could not parse document into distinct numbered clauses.")
        sys.exit(1)
        
    return sections

def summarize_policy(sections: list) -> str:
    """
    Skill: summarize_policy
    Takes structured policy sections and produces a compliant summary with explicit clause references.
    """
    if not sections:
        raise ValueError("No sections provided to summarize.")
        
    summary_lines = [
        "HR LEAVE POLICY SUMMARY",
        "========================\n"
    ]
    
    # Heuristic for multi-condition or critical obligations from README
    # (must, requires, will, may, forfeited, not permitted, AND etc.)
    critical_keywords = ['must', 'requires', 'will', 'forfeited', 'not permitted', 'and']
    
    for sec in sections:
        clause_id = sec['id']
        text = sec['text']
        
        text_lower = text.lower()
        
        # Determine if clause holds multi-conditions or strict obligations
        is_complex = any(kw in text_lower for kw in critical_keywords)
        
        # Enforcement Rule: If a clause cannot be summarised without meaning loss 
        # — quote it verbatim and flag it.
        if is_complex or len(text.split()) > 15:
            summary_lines.append(f"• Clause {clause_id}: [VERBATIM] \"{text}\"")
        else:
            summary_lines.append(f"• Clause {clause_id}: {text}")
            
    summary_text = "\n".join(summary_lines)
    
    # Post-validation (Error Handling from skills.md)
    # Check if any clause was omitted
    for sec in sections:
        if f"Clause {sec['id']}" not in summary_text:
            print(f"Error: Clause {sec['id']} was silently omitted during summarization.")
            sys.exit(1)
            
    # Check for scope bleed words 
    scope_bleed_phrases = ["standard practice", "typically", "expected to"]
    for phrase in scope_bleed_phrases:
        if phrase in summary_text:
            print(f"Error: Scope bleed detected - '{phrase}' found in summary.")
            sys.exit(1)
            
    return summary_text

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy document.txt")
    parser.add_argument("--output", required=True, help="Path to save summary.txt")
    args = parser.parse_args()
    
    print(f"Retrieving policy from: {args.input}")
    sections = retrieve_policy(args.input)
    print(f"Successfully extracted {len(sections)} clauses.")
    
    print("Summarizing policy...")
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Done. Compliant summary written to: {args.output}")

if __name__ == "__main__":
    main()
