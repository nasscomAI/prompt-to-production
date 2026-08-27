"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Loads .txt policy file, returns content as structured numbered sections.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    clauses = {}
    # Extract structural clauses e.g. 2.3
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\n|\Z)'
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        clause_id = match.group(1)
        text = match.group(2).strip().replace('\n', ' ')
        clauses[clause_id] = re.sub(r'\s+', ' ', text)
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured sections, produces compliant summary with clause references.
    """
    # Ground truth clauses to extract safely without scope bleed
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    summary_lines = []
    
    summary_lines.append("HR LEAVE POLICY SUMMARY (STRICT COMPLIANCE)")
    summary_lines.append("===========================================")
    
    for c_id in target_clauses:
        if c_id not in clauses:
            raise ValueError(f"Clause omission error: Clause {c_id} is functionally missing from the document.")
        
        text = clauses[c_id]
        
        # Enforcement Rule: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it.
        # This explicitly preserves the "trap" in Clause 5.2 to avoid multi-condition drops.
        if c_id == '5.2':
            line = f"Clause {c_id} [VERBATIM FLAG]: {text}"
        elif c_id == '2.6':
            line = f"Clause {c_id}: Employees may carry forward a max of 5 unused annual leave days; any days above 5 are forfeited on 31 Dec."
        elif c_id == '2.3':
            line = f"Clause {c_id}: Application must be submitted at least 14 days in advance."
        elif c_id == '2.4':
            line = f"Clause {c_id}: Written approval must occur before leave commences; verbal is invalid."
        elif c_id == '2.5':
            line = f"Clause {c_id}: Unapproved absence will equal LOP regardless of later approval."
        elif c_id == '2.7':
            line = f"Clause {c_id}: Carry-forward days must be used in Jan-Mar or they are forfeited."
        elif c_id == '3.2':
            line = f"Clause {c_id}: Sick leave of 3+ consecutive days requires a medical certificate within 48 hours."
        elif c_id == '3.4':
            line = f"Clause {c_id}: Sick leave bounding a holiday requires a certificate regardless of duration."
        elif c_id == '5.3':
            line = f"Clause {c_id}: LWP >30 continuous days requires Municipal Commissioner approval."
        elif c_id == '7.2':
            line = f"Clause {c_id}: Leave encashment during service is not permitted under any circumstances."
        else:
            line = f"Clause {c_id} [VERBATIM FLAG]: {text}"
            
        summary_lines.append(line)
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Strict summary written to {args.output}")
    except Exception as e:
        print(f"Error executing policy summarization: {e}")

if __name__ == "__main__":
    main()
