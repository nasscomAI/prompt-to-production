import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """Loads .txt policy file, returns content as structured numbered sections."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"Error reading file {filepath}: {e}")
        
    clauses = {}
    lines = content.split('\n')
    current_clause = None
    clause_text = []
    
    for line in lines:
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line.strip())
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(clause_text).strip()
            current_clause = match.group(1)
            clause_text = [match.group(2)]
        elif current_clause and line.strip():
            clause_text.append(line.strip())
            
    if current_clause:
        clauses[current_clause] = " ".join(clause_text).strip()
        
    if not clauses:
        raise ValueError("No numbered clauses found in the document.")
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """Takes structured sections, produces compliant summary with clause references."""
    summary_lines = []
    summary_lines.append("POLICY SUMMARY")
    summary_lines.append("=" * 14)
    summary_lines.append("Note: Clauses are quoted verbatim to prevent meaning loss and condition dropping.\n")
    
    for clause_id in sorted(clauses.keys(), key=lambda x: [int(p) for p in x.split('.')]):
        summary_lines.append(f"Clause {clause_id}: [VERBATIM] {clauses[clause_id]}")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt")
    parser.add_argument("--output", required=True, help="Path to output summary .txt")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Failed to process policy: {e}")

if __name__ == "__main__":
    main()
