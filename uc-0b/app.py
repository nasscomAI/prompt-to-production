"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def process_policy(input_path: str, output_path: str):
    required_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    extracted = {}
    
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split text into numbered clauses like "2.3"
    lines = content.split('\n')
    current_clause = None
    clause_text = []
    
    for line in lines:
        match = re.match(r'^(\d+\.\d+)\s(.*)', line)
        if match:
            if current_clause:
                extracted[current_clause] = " ".join(clause_text).strip()
            current_clause = match.group(1)
            clause_text = [match.group(2)]
        elif current_clause and line.strip() and not line.startswith('═'):
            clause_text.append(line.strip())
            
    # save last
    if current_clause:
        extracted[current_clause] = " ".join(clause_text).strip()
        
    summary_lines = ["# Policy Leave Summary\n\n"]
    for clause in required_clauses:
        if clause in extracted:
            text = extracted[clause]
            # Enforcement: "quote it verbatim and flag it" if meaning loss is a risk.
            # Directly quoting verbatim to uphold condition preservation mandate.
            summary_lines.append(f"- **Clause {clause}** (VERBATIM QUOTE): {text}\n")
        else:
            summary_lines.append(f"- **Clause {clause}**: [MISSING FROM SOURCE]\n")
            
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input policy text file")
    parser.add_argument("--output", required=True, help="Output summary text file")
    args = parser.parse_args()
    process_policy(args.input, args.output)
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
