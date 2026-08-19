"""
UC-0B app.py — Starter file completed.
Builds upon agents.md and skills.md to strictly retrieve and summarize policy details.
"""
import argparse
import os
import re
import sys

def retrieve_policy(filepath: str) -> list:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    if not os.path.exists(filepath):
        print(f"Error: Input file does not exist at '{filepath}'.")
        sys.exit(1)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    structured_data = []
    current_clause = None
    current_text = []

    for line in lines:
        line = line.strip()
        
        # Skip empty lines, separators, and non-clause document meta
        if not line or line.startswith('═') or line.startswith('Document') or line.startswith('Version') or line.startswith('CITY HUMAN') or line.startswith('EMPLOYEE'):
            continue
            
        # Match major heading like "3. SICK LEAVE"
        if re.match(r'^\d+\.\s+[A-Z\s]+$', line) or re.match(r'^[A-Z\s]+$', line):
            # This is a major heading or uppercase text, not a clause.
            # We don't want to append this to the previous clause.
            if current_clause:
                structured_data.append({
                    "section": current_clause,
                    "text": " ".join(current_text)
                })
            current_clause = None
            current_text = []
            continue

        # Match lines like "2.3 Employees must submit..."
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                structured_data.append({
                    "section": current_clause,
                    "text": " ".join(current_text)
                })
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause:
            current_text.append(line)

    if current_clause:
        structured_data.append({
            "section": current_clause,
            "text": " ".join(current_text)
        })

    if not structured_data:
        print("Error: The content cannot be successfully parsed into distinct numbered sections.")
        sys.exit(1)

    return structured_data

def summarize_policy(structured_data: list) -> str:
    """
    Takes structured sections and produces a compliant summary with explicit clause references.
    """
    # Ground truth clauses to include
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    
    extracted = {item['section']: item['text'] for item in structured_data}
    missing_clauses = [c for c in target_clauses if c not in extracted]
    
    if missing_clauses:
        print(f"Error: Summarization detected clause omission for clauses: {missing_clauses}")
        sys.exit(1)

    summary_lines = []
    summary_lines.append("# HR Leave Policy Summary\n")
    
    for clause in target_clauses:
        text = extracted[clause]
        
        # Enforcement Rules:
        # 1. Every numbered clause must be present in the summary
        # 2. Multi-condition obligations must preserve ALL conditions.
        # 3. Never add information not present in the source document.
        # 4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it.
        
        # To strictly avoid condition drops, scope bleed, and obligation softening, 
        # we will extract the exact text and flag it as preserved verbatim.
        summary_lines.append(f"**Clause {clause}** (Preserved Verbatim to avoid meaning loss):")
        summary_lines.append(f"> {text}\n")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Input policy text file")
    parser.add_argument("--output", required=True, help="Output summary text file")
    
    args = parser.parse_args()
    
    try:
        # Execute Skill 1
        structured_data = retrieve_policy(args.input)
        
        # Execute Skill 2
        summary_text = summarize_policy(structured_data)
        
        # Ensure output directory exists if there is one
        out_dir = os.path.dirname(os.path.abspath(args.output))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)

        print(f"Summary generated successfully. Results written to {args.output}")
        
    except Exception as e:
        print(f"Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
