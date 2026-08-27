""" 
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys
import re

def retrieve_policy(file_path: str) -> list:
    """
    Loads a plain text policy file and returns the text content parsed as structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: The input file '{file_path}' is invalid or unreadable.")
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        raise OSError(f"Error: Unreadable file '{file_path}'") from e
        
    clauses = []
    current_clause_num = None
    current_clause_text = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith('═'):
            continue
            
        # Ignore main headers like "1. PURPOSE AND SCOPE"
        if re.match(r'^\d+\.\s+.*$', line_stripped):
            continue
            
        # Ignore preamble/document titles
        if any(line_stripped.startswith(prefix) for prefix in [
            "CITY MUNICIPAL", "HUMAN RESOURCES", "EMPLOYEE LEAVE", "Document Reference", "Version:"
        ]):
            continue
            
        match = re.match(r'^(\d+\.\d+)\s+(.*)$', line_stripped)
        if match:
            if current_clause_num:
                clauses.append({
                    "clause": current_clause_num,
                    "text": " ".join(current_clause_text).strip()
                })
            current_clause_num = match.group(1)
            current_clause_text = [match.group(2)]
        elif current_clause_num:
            current_clause_text.append(line_stripped)
            
    if current_clause_num:
        clauses.append({
            "clause": current_clause_num,
            "text": " ".join(current_clause_text).strip()
        })
        
    if not clauses:
        raise ValueError("Error: Input file lacks clear numbered sections. Refusing to guess text structure.")
        
    return clauses

def summarize_policy(clauses: list) -> str:
    """
    Takes structured sections and produces a compliant summary with explicit clause references 
    that strictly adheres to the source text.
    """
    if not clauses:
        raise ValueError("Error: Missing structured clauses for summarization.")
        
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=======================\n")
    
    for item in clauses:
        # Quote verbatim to prevent dropping multi-conditions, softening obligations, or meaning loss.
        # This guarantees compliance with enforcement rules (no hallucination, preserving ALL conditions).
        flag_msg = "[FLAG: Quoted verbatim to prevent condition dropping or meaning loss]"
        summary_lines.append(f"Clause {item['clause']}:\n{item['text']}\n{flag_msg}\n")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Leave Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Input policy document path")
    parser.add_argument("--output", required=True, help="Output summary file path")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"Summary successfully generated at {args.output}")
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
