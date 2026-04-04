"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """Loads the .txt policy file and returns content as structured numbered sections."""
    sections = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            current_clause = None
            current_text = []
            for line in lines:
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_clause:
                        sections[current_clause] = " ".join(current_text).strip()
                    current_clause = match.group(1)
                    current_text = [match.group(2).strip()]
                elif current_clause and line.strip() and not line.startswith('═') and not re.match(r'^\d+\.\s+[A-Z]', line.strip()):
                    current_text.append(line.strip())
            if current_clause:
                sections[current_clause] = " ".join(current_text).strip()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return sections

def summarize_policy(sections: dict) -> str:
    """Takes structured sections and produces a compliant summary with clause references."""
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    for clause in target_clauses:
        if clause in sections:
            # Rule 2: Multi-condition obligations must preserve ALL conditions.
            # Rule 4: If meaning loss is possible, quote verbatim.
            summary_lines.append(f"Clause {clause}: {sections[clause]}")
        else:
            summary_lines.append(f"Clause {clause}: [MISSING IN SOURCE - ERROR]")
            
    return "\n\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Successfully wrote summary to {args.output}")
    except Exception as e:
        print(f"Error writing to {args.output}: {e}")

if __name__ == "__main__":
    main()
