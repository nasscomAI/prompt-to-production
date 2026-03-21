"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Loads .txt policy file, returns content as structured numbered sections.
    """
    sections = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        current_clause = None
        current_text = []
        for line in f:
            line = line.strip()
            if not line: continue
            
            # Match numbered clauses like "2.3"
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_clause:
                    sections[current_clause] = " ".join(current_text)
                current_clause = match.group(1)
                current_text = [match.group(2)]
            elif current_clause and not line.startswith("════"):
                current_text.append(line)
        
        if current_clause:
            sections[current_clause] = " ".join(current_text)
            
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections, produces compliant summary with clause references.
    To avoid dropping conditions or changing meaning, we summarize by citing 
    clauses verbatim or with absolute strictness.
    """
    summary = ["# HR Leave Policy Summary\n"]
    for clause, text in sections.items():
        summary.append(f"Clause {clause}: {text}")
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy txt file")
    parser.add_argument("--output", required=True, help="Path to output summary txt file")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary_text = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text)
        
    print(f"Done. Wrote summary to {args.output}")

if __name__ == "__main__":
    main()
