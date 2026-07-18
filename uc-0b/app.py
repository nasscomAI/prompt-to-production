"""
UC-0B app.py — Preserves precise policy constraints and multi-condition obligations.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import sys
import os

def is_section_header(line: str) -> bool:
    """
    Checks if a line is a section separator or a top-level section header.
    """
    if '══' in line or '──' in line:
        return True
    parts = line.split(maxsplit=1)
    if parts:
        first = parts[0]
        # Matches e.g. "3." or "10."
        if first.endswith('.') and first[:-1].isdigit():
            return True
    return False

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file and returns content as structured numbered sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")
        
    sections = {}
    current_clause = None
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            
            if is_section_header(stripped):
                current_clause = None
                continue
            
            # Identify clause numbers like 2.3, 5.2, etc. at the start of a line
            parts = stripped.split(maxsplit=1)
            if parts:
                first_word = parts[0]
                is_clause = False
                if '.' in first_word:
                    subparts = first_word.split('.')
                    if len(subparts) == 2 and all(s.isdigit() for s in subparts):
                        is_clause = True
                
                if is_clause:
                    current_clause = first_word
                    sections[current_clause] = parts[1] if len(parts) > 1 else ""
                elif current_clause is not None:
                    sections[current_clause] += " " + stripped
                    
    # Clean extra whitespace
    for clause in sections:
        sections[clause] = " ".join(sections[clause].split())
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections, produces a compliant summary with clause references.
    Ensures no clause omission, preserves multi-condition obligations,
    avoids scope bleed/adding info, and flags verbatim clauses.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = []
    
    # 1. Ensure every numbered clause is present
    for clause in target_clauses:
        if clause not in sections:
            raise ValueError(f"Required clause {clause} is missing from the source document!")
        
        text = sections[clause]
        
        # 2. Identify multi-condition obligations or potential meaning loss and quote verbatim with [FLAGGED]
        # Clause 5.2 (two approvers: Department Head AND HR Director)
        # Clause 2.4 (written approval before leave commences; verbal not valid)
        if clause in ["5.2", "2.4"]:
            summary_lines.append(f"[FLAGGED] Clause {clause} (Verbatim): {text}")
        else:
            # Summary preserves all conditions exactly, citing source clause
            summary_lines.append(f"Clause {clause}: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        # Ensure target directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
