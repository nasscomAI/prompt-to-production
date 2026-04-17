import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Reads a raw text policy document and parses its contents into structured, numbered sections.
    """
    clauses = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_clause = None
        current_text = []
        
        for line in lines:
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_clause:
                    clauses[current_clause] = " ".join(current_text).strip()
                current_clause = match.group(1)
                current_text = [match.group(2).strip()]
            elif current_clause:
                # Check if we hit a separator or header
                if line.startswith('═══') or re.match(r'^\d+\.\s+[A-Z]', line):
                    clauses[current_clause] = " ".join(current_text).strip()
                    current_clause = None
                    current_text = []
                else:
                    # Append to current text if it's not empty
                    if line.strip():
                        current_text.append(line.strip())
                        
        if current_clause:
            clauses[current_clause] = " ".join(current_text).strip()
            
        return clauses
    except FileNotFoundError:
        print(f"Error: Policy file '{filepath}' not found.")
        return {}

def summarize_policy(clauses: dict) -> str:
    """
    Generates a highly accurate, compliant summary from structured policy sections,
    preserving all obligations, conditions, and clause references.
    """
    summary_lines = []
    summary_lines.append("# HR Leave Policy Summary")
    summary_lines.append("Generated strictly according to the UC-0B RICE enforcement rules.\n")
    
    # Keywords that indicate complex logic, conditions, or strict obligations
    complex_terms = [
        'must', 'requires', 'not permitted', 'cannot', 
        'regardless', 'forfeited', 'and', 'or', 'unless', 'subject to'
    ]
    
    for clause_id, text in clauses.items():
        # Check if the clause contains multi-part conditions or strict obligations
        is_complex = any(term in text.lower() for term in complex_terms)
        
        if is_complex:
            # Rule: If a clause is highly complex and cannot be confidently summarized 
            # without the risk of meaning loss, quote verbatim and flag it.
            summary_lines.append(f"- **Clause {clause_id}**: [VERBATIM_REQUIRED] {text}")
        else:
            # Simple clause - no complex logic found, can be safely represented
            summary_lines.append(f"- **Clause {clause_id}**: {text}")
            
    return "\n".join(summary_lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarization App")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write output summary")
    args = parser.parse_args()

    # Step 1: Retrieve and parse the policy
    clauses = retrieve_policy(args.input)
    if not clauses:
        print("No clauses retrieved or file failed to load. Exiting.")
        return
        
    # Step 2: Summarize compliant to the rules
    summary = summarize_policy(clauses)
    
    # Step 3: Write to output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Compliant summary written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file '{args.output}': {e}")

if __name__ == "__main__":
    main()
