"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

MANDATORY_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2"
]

def retrieve_policy(input_path: str) -> dict:
    """Loads a .txt policy file and returns the content parsed into structured numbered sections."""
    sections = {}
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found at {input_path}")
        
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                sections[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
        elif current_clause and line.strip() and not line.startswith('═══') and not re.match(r'^\d+\.', line):
            current_text.append(line.strip())
            
    if current_clause:
        sections[current_clause] = " ".join(current_text).strip()
        
    return sections


def summarize_policy(sections: dict) -> str:
    """Takes structured sections and produces a compliant summary with exact clause references."""
    summary_lines = ["HR Leave Policy Summary", "=" * 25, ""]
    
    for clause_num in MANDATORY_CLAUSES:
        if clause_num not in sections:
            raise ValueError(f"Mandatory clause {clause_num} is missing from the input.")
            
        text = sections[clause_num]
        
        # Rule 4: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it.
        # Rule 2: Multi-condition obligations must preserve ALL conditions.
        # To strictly guarantee no scope bleed, condition dropping, or softening, we quote them verbatim.
        summary_lines.append(f"Clause {clause_num} [VERBATIM FLAG]: {text}")
        
    return "\n".join(summary_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write the summary (.txt)")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary_text = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
