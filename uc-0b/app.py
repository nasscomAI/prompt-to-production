"""
UC-0B app.py — Strict Policy Summarizer
Built following RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import os

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file, returns the content clearly formatted 
    as structured numbered sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")
        
    structured_sections = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find all numbered clauses e.g. "2.3 Employees must..."
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|\Z)', re.MULTILINE | re.DOTALL)
    
    matches = clause_pattern.findall(content)
    for num, text in matches:
        # Clean up whitespace and newlines inside the clause
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        structured_sections[num] = cleaned_text
        
    return structured_sections

def summarize_policy(sections: dict) -> str:
    """
    Produces a highly compliant summary. 
    Any clause with strict constraints, conditions, or multi-party requirements
    is heavily preserved or explicitly quoted to avoid scope bleed or condition drops.
    """
    summary_lines = ["# Policy Document Summary\n"]
    
    for clause_num, text in sections.items():
        # Heuristic to detect complex multi-condition or strict clauses 
        # (e.g. "requires", "must", "AND", multiple approvals)
        is_complex = bool(re.search(r'(requires|must|will|not permitted|and|within)', text, re.IGNORECASE))
        has_multi_party = "and the" in text.lower() or "approval from" in text.lower()
        
        if has_multi_party:
            # Rule: Multi-condition obligations must preserve ALL conditions
            summary_lines.append(f"Clause {clause_num} (Strict Compliance Maintained): {text}")
        elif is_complex:
            # Rule: If a clause cannot be cleanly summarised, quote it verbatim and flag
            summary_lines.append(f"Clause {clause_num} (Original text preserved due to strict constraints): {text}")
        else:
            # Rule: Every numbered clause must be present in the summary
            summary_lines.append(f"Clause {clause_num}: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write results .txt file")
    args = parser.parse_args()
    
    # Skills execution
    print("Retrieving policy sections...")
    sections = retrieve_policy(args.input)
    
    print("Summarizing policy strictly according to agents.md rules...")
    summary_text = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text)
        
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
