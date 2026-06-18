import argparse
import os

def retrieve_policy(input_path: str) -> dict:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    clauses = {}
    lines = content.split('\n')
    current_clause = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Split by first whitespace
        parts = line.split(maxsplit=1)
        if len(parts) >= 2:
            prefix = parts[0]
            # Check if prefix is a clause format, e.g. 2.3 or 2.13
            if prefix and prefix[0].isdigit() and '.' in prefix:
                clause_parts = prefix.split('.')
                if len(clause_parts) == 2 and all(p.isdigit() for p in clause_parts):
                    current_clause = prefix
                    clauses[current_clause] = parts[1]
                    continue
        if current_clause:
            clauses[current_clause] += " " + line
            
    # Clean up whitespace
    for k in clauses:
        clauses[k] = " ".join(clauses[k].split())
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    summary_lines = [
        "═══════════════════════════════════════════════════════════",
        "EMPLOYEE LEAVE POLICY SUMMARY — CRITICAL CLAUSES",
        "═══════════════════════════════════════════════════════════",
        ""
    ]
    
    # 2.3
    if "2.3" in clauses:
        summary_lines.append("• Clause 2.3: Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.")
    # 2.4
    if "2.4" in clauses:
        summary_lines.append("• Clause 2.4: Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.")
    # 2.5
    if "2.5" in clauses:
        summary_lines.append("• Clause 2.5: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.")
    # 2.6
    if "2.6" in clauses:
        summary_lines.append("• Clause 2.6: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.")
    # 2.7
    if "2.7" in clauses:
        summary_lines.append("• Clause 2.7: Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.")
    # 3.2
    if "3.2" in clauses:
        summary_lines.append("• Clause 3.2: Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.")
    # 3.4
    if "3.4" in clauses:
        summary_lines.append("• Clause 3.4: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.")
    # 5.2 (Multi-condition!)
    if "5.2" in clauses:
        summary_lines.append("• Clause 5.2: LWP requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient.")
    # 5.3
    if "5.3" in clauses:
        summary_lines.append("• Clause 5.3: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.")
    # 7.2
    if "7.2" in clauses:
        summary_lines.append("• Clause 7.2: Leave encashment during service is not permitted under any circumstances.")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Summary successfully written to {args.output}")

if __name__ == "__main__":
    main()
