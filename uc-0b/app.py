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
    current_clause = None
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_str = line.strip()
            # Match pattern like "2.3 Employees must submit..."
            match = re.match(r'^(\d+\.\d+)\s+(.*)$', line_str)
            if match:
                current_clause = match.group(1)
                sections[current_clause] = match.group(2)
            elif current_clause and line_str:
                # If it's a section header or a line of equal signs, stop appending
                if re.match(r'^(\d+\.)\s+(.*)$', line_str) or line_str.startswith('═'):
                    current_clause = None
                else:
                    sections[current_clause] += " " + line_str
                    
    # Clean up whitespace
    for clause in list(sections.keys()):
        sections[clause] = re.sub(r'\s+', ' ', sections[clause]).strip()
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections, produces compliant summary with clause references.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    output_lines = []
    output_lines.append("=== POLICY SUMMARY (VERBATIM ENFORCEMENT TO PREVENT MEANING LOSS) ===")
    output_lines.append("")
    
    for clause in target_clauses:
        if clause in sections:
            content = sections[clause]
            output_lines.append(f"Clause {clause}: [VERBATIM] {content} [FLAG: CRITICAL OBLIGATION]")
        else:
            output_lines.append(f"Clause {clause}: [MISSING] Section not found in source document.")
            
    return "\n".join(output_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy txt file")
    parser.add_argument("--output", required=True, help="Path to write summary txt file")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary_text = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text + "\n")
    
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
