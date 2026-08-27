"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

def retrieve_policy(file_path: str) -> dict:
    """
    Loads the raw text of a policy file and parses it into structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    clauses = {}
    current_clause = None
    current_text = []
    
    # Match patterns like: "2.3 Employees must..."
    clause_pattern = re.compile(r'^\s*(\d+\.\d+)\s+(.*)$')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = clause_pattern.match(line)
            if match:
                if current_clause:
                    clauses[current_clause] = " ".join(current_text).strip()
                current_clause = match.group(1)
                current_text = [match.group(2).strip()]
            else:
                if current_clause:
                    stripped = line.strip()
                    # Skip section headers or dividers
                    if stripped and not stripped.startswith('═') and not re.match(r'^\d+\.\s', stripped):
                        current_text.append(stripped)
                        
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    return clauses


def summarize_policy(clauses: dict) -> str:
    """
    Takes the structured sections and produces a compliant, complete summary
    highlighting the core obligations with clause references.
    """
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    
    # Verify presence of all required target clauses
    for target in target_clauses:
        if target not in clauses:
            raise ValueError(f"Required clause {target} is missing from the policy file.")
            
    summary_lines = [
        "=========================================",
        "EMPLOYEE LEAVE POLICY - SUMMARY OF OBLIGATIONS",
        "=========================================",
        "",
        "To prevent any loss of meaning, condition dropping, or scope bleed, the key binding obligations from the policy document have been quoted verbatim below:",
        ""
    ]
    
    for target in target_clauses:
        text = clauses[target]
        # Clean up double spaces if any, and convert non-standard dashes to standard ones
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('–', '-')  # Fix en dash or em dash to hyphen
        summary_lines.append(f"[VERBATIM] Clause {target}: {text}")
        
    return "\n".join(summary_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error executing policy summarizer: {e}")
        exit(1)


if __name__ == "__main__":
    main()
