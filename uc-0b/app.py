"""
UC-0B app.py — Policy Summarizer
Implements retrieve_policy and summarize_policy enforcing the strict rules for preservation.
"""
import argparse
import re
import sys

def retrieve_policy(filepath: str) -> dict:
    """
    Reads a .txt policy file and extracts all numbered clauses (e.g., "2.3").
    Returns a dictionary mapping clause numbers to their full text.
    """
    clauses = {}
    current_clause = None
    current_text = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines, decorative borders, and section headers (like "1. PURPOSE AND SCOPE")
                if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z]', line) or line.startswith('Document Reference') or line.startswith('Version') or line.startswith('CITY MUNICIPAL') or line.startswith('HUMAN RESOURCES'):
                    if current_clause:
                        clauses[current_clause] = ' '.join(current_text)
                        current_clause = None
                        current_text = []
                    continue
                
                # Match start of a clause, e.g., "2.3 Employees must..."
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_clause:
                        clauses[current_clause] = ' '.join(current_text)
                    current_clause = match.group(1)
                    current_text = [match.group(2)]
                elif current_clause:
                    # Continuation line for the current clause
                    current_text.append(line)
                    
        # Catch the last clause
        if current_clause:
            clauses[current_clause] = ' '.join(current_text)
            
    except Exception as e:
        print(f"ERROR: Cannot read policy file: {e}", file=sys.stderr)
        sys.exit(1)
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Summarizes the extracted clauses ensuring ALL conditions are preserved.
    Uses the [VERBATIM] flag for complex or high-risk multi-condition clauses 
    to avoid meaning loss.
    """
    lines = []
    lines.append("HR LEAVE POLICY SUMMARY")
    lines.append("=======================")
    
    # Identify high-risk keywords that denote multi-approvers, strict forfeits, or negations
    high_risk_keywords = [
        "requires approval", "and the", "not permitted", "forfeited", 
        "cannot be encashed", "under any circumstances", "verbal approval is not valid"
    ]
    
    for clause_id, text in clauses.items():
        # Check if clause needs to be flagged as VERBATIM
        text_lower = text.lower()
        if any(kw in text_lower for kw in high_risk_keywords):
            lines.append(f"Clause {clause_id} [VERBATIM]: {text}")
        else:
            # Perform a safe, light deterministic summarization for simple clauses
            # (In a real system, an LLM would do this safely constrained by the RICE prompt)
            safe_summary = text.replace("City Municipal Corporation (CMC)", "CMC")
            safe_summary = safe_summary.replace("registered medical practitioner", "doctor")
            
            lines.append(f"Clause {clause_id}: {safe_summary}")
            
    return "\n\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write the summary (.txt)")
    args = parser.parse_args()
    
    print(f"Loading policy document from {args.input}...")
    clauses = retrieve_policy(args.input)
    
    if not clauses:
        print("ERROR: No clauses extracted. Check file format.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Extracted {len(clauses)} clauses.")
    
    summary_text = summarize_policy(clauses)
    
    with open(args.output, "w", encoding="utf-8") as out:
        out.write(summary_text)
        
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
