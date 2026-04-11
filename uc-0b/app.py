"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    sections = {}
    current_section = None
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Ignore header lines or decorative dividers
                if line.startswith("=") or re.match(r'^\d+\.\s+[A-Z]', line):
                    current_section = None
                    continue
                
                # Match numbered clauses, e.g., "1.1 Text goes here"
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    clause_num = match.group(1)
                    text = match.group(2)
                    sections[clause_num] = text
                    current_section = clause_num
                elif current_section:
                    # Append continuation lines to the current clause
                    sections[current_section] += " " + line
    except FileNotFoundError:
        print(f"Error: Input file {file_path} not found.", file=sys.stderr)
        sys.exit(1)
    
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references.
    Flags and quotes verbatim clauses with complex multi-condition obligations.
    """
    summary_lines = []
    summary_lines.append("POLICY COMPLIANCE SUMMARY")
    summary_lines.append("=========================")
    summary_lines.append("Note: Multi-condition obligations and critical bindings are quoted verbatim")
    summary_lines.append("to prevent scope bleed, obligation softening, or condition drops.")
    summary_lines.append("=========================\n")
    
    # Keywords that indicate a strong obligation or multi-condition logic
    complex_keywords = ["must", "requires", "will", "forfeited", "not permitted", "only", "cannot", "and"]
    
    for clause_num, text in sections.items():
        is_complex = any(kw in text.lower() for kw in complex_keywords)
        
        if is_complex:
            # Quote verbatim and flag as per enforcement rules
            summary_lines.append(f"[CLAUSE {clause_num} - STRICT/MULTI-CONDITION]:")
            summary_lines.append(f'"{text}"\n')
        else:
            summary_lines.append(f"[CLAUSE {clause_num}]: {text}\n")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Compliance Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()
    
    # Check if input file exists
    structured_sections = retrieve_policy(args.input)
    if not structured_sections:
        print("Error: No sections extracted from policy document.", file=sys.stderr)
        sys.exit(1)
        
    summary_text = summarize_policy(structured_sections)
    
    with open(args.output, mode='w', encoding='utf-8') as f:
        f.write(summary_text)
        
    print(f"Done. Compliant summary written to {args.output}")

if __name__ == "__main__":
    main()
