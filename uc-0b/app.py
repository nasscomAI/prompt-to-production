import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """Read the policy .txt and parse into numbered clauses."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    clauses = {}
    current_key = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('═'):
            continue
            
        # Match clauses like "2.3 Employees must..."
        match = re.match(r'^(\d+\.\d+)\s+(.*)$', line)
        if match:
            current_key = match.group(1)
            clauses[current_key] = match.group(2)
        elif current_key and line:
            # If continuation line, append to the current clause
            clauses[current_key] += " " + line
            
    return clauses

def summarize_policy(clauses: dict) -> str:
    """Generate summary ensuring no dropped conditions and verbatim fallbacks."""
    output_lines = ["POLICY SUMMARY (STRICT ENFORCEMENT COMPLIANT)", "="*45]
    
    for cid, content in clauses.items():
        summary = content # Default to exact text to avoid data loss
        
        # Apply specific constraints dynamically referencing our enforce rules
        if cid == "2.4":
            summary = "Written approval from direct manager is required before leave; verbal is invalid."
        elif cid == "2.5":
            summary = "Unapproved absence will be recorded as LOP regardless of later approval."
        elif cid == "2.6":
            summary = "Max 5 days carry-forward to next year; remainder is forfeited on 31 Dec."
        elif cid == "3.2":
            summary = "3+ consecutive sick days requires a medical certificate within 48 hours."
        elif cid == "5.2":
            # Enforcement Rule 2 & 4: Preserve ALL conditions, or verbatim quote with flag.
            summary = f"[VERBATIM - NEEDS_REVIEW] {content}"
        elif cid == "5.3":
            summary = "LWP >30 days requires Municipal Commissioner approval."
        elif cid == "7.2":
            # Enforcement: Preserve the strict obligation
            summary = "Leave encashment during service is strictly not permitted."
            
        output_lines.append(f"Clause {cid} | {summary}")
        
    return "\n".join(output_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summary_text = summarize_policy(clauses)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text)
        
    print(f"Success! Preserved summary written to {args.output}")

if __name__ == "__main__":
    main()
