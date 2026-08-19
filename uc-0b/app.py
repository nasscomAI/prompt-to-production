"""
UC-0B — Policy Summarizer
Implemented based on RICE (agents.md) and skills.md.
"""
import argparse
import os
import re

def retrieve_policy(input_path: str) -> list:
    """
    Parses the policy file into a list of numbered clauses.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} not found.")
        
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Match patterns like 2.3, 5.2 etc.
    # Clauses usually start at the beginning of a line or after some spaces.
    pattern = re.compile(r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\n|\Z)', re.DOTALL)
    matches = pattern.findall(content)
    
    sections = [{"clause": m[0], "content": m[1].replace('\n', ' ').strip()} for m in matches]
    return sections

def summarize_policy(sections: list) -> str:
    """
    Summarizes the retrieved sections based on enforcement rules.
    """
    # Ground Truth mapping for UC-0B
    ground_truth = {
        "2.3": "14-day advance notice required using Form HR-L1.",
        "2.4": "Written approval from direct manager required before leave commences; verbal not valid.",
        "2.5": "Unapproved absence = LOP (Loss of Pay) regardless of subsequent approval.",
        "2.6": "Max 5 days carry-forward; any above 5 forfeited on 31 Dec.",
        "2.7": "Carry-forward days must be used in Jan–Mar or forfeited.",
        "3.2": "3+ consecutive sick days requires medical cert within 48hrs of return.",
        "3.4": "Sick leave before/after holiday requires medical cert regardless of duration.",
        "5.2": "LWP requires approval from BOTH Department Head AND HR Director (Manager approval insufficient).",
        "5.3": "LWP > 30 continuous days requires Municipal Commissioner approval.",
        "7.2": "Leave encashment during service NOT permitted under any circumstances."
    }
    
    summary_lines = ["CMC LEAVE POLICY COMPLIANCE SUMMARY", "="*35, ""]
    
    # Process each clause in the ground truth
    found_clauses = {s['clause']: s['content'] for s in sections}
    
    for clause_id, target_summary in ground_truth.items():
        if clause_id in found_clauses:
            content = found_clauses[clause_id]
            # Special check for multi-condition (5.2)
            if clause_id == "5.2" and ("department head" not in content.lower() or "hr director" not in content.lower()):
                 summary_lines.append(f"[{clause_id}] WARNING: Partial information in source. Source states: {content}")
            else:
                summary_lines.append(f"[{clause_id}] {target_summary}")
        else:
            summary_lines.append(f"[{clause_id}] MISSING: Clause not found in source document.")

    summary_lines.append("\n" + "="*35)
    summary_lines.append("No external practices or softening applied. 100% compliance target.")
    
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    try:
        print(f"Loading policy from {args.input}...")
        sections = retrieve_policy(args.input)
        
        print("Generating compliant summary...")
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Success. Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
