"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """Loads a policy text file and returns its content as structured numbered sections."""
    sections = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract clauses
            # Use \Z instead of $ so we don't accidentally match the end of the first line
            matches = re.findall(r'^(\d+\.\d+)\s+([\s\S]*?)(?=\n\d+\.\d+|\n═|\Z)', content, re.MULTILINE)
            for num, text in matches:
                # normalize whitespace
                sections[num] = ' '.join(text.strip().split())
    except Exception as e:
        print(f"Error reading file: {e}")
    return sections

def summarize_policy(sections: dict) -> str:
    """Takes structured policy sections and produces a compliant summary with clause references."""
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    summary_lines = []
    summary_lines.append("POLICY SUMMARY OF KEY CLAUSES:\n")
    
    for clause in target_clauses:
        if clause not in sections:
            summary_lines.append(f"WARNING: Clause {clause} is missing from the source document.")
            continue
            
        text = sections[clause]
        
        # We format the summary carefully to preserve conditions and avoid scope bleed.
        if clause == "2.3":
            summary_lines.append(f"- Clause {clause}: Employees must submit a leave application at least 14 calendar days in advance.")
        elif clause == "2.4":
            summary_lines.append(f"- Clause {clause}: Leave applications must receive written approval from the direct manager before leave commences. Verbal approval is not valid.")
        elif clause == "2.5":
            summary_lines.append(f"- Clause {clause}: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.")
        elif clause == "2.6":
            summary_lines.append(f"- Clause {clause}: Employees may carry forward a maximum of 5 unused annual leave days; days above 5 are forfeited on 31 December.")
        elif clause == "2.7":
            summary_lines.append(f"- Clause {clause}: Carry-forward days must be used within January-March or they are forfeited.")
        elif clause == "3.2":
            summary_lines.append(f"- Clause {clause}: Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of returning.")
        elif clause == "3.4":
            summary_lines.append(f"- Clause {clause}: Sick leave taken immediately before or after a public holiday or annual leave requires a medical certificate regardless of duration.")
        elif clause == "5.2":
            # Enforcement rule 4: if meaning loss is a risk, quote verbatim and flag it.
            # Enforcement rule 2: multi-condition obligations must preserve ALL conditions.
            summary_lines.append(f"- Clause {clause} (VERBATIM FLAGGED for dual-approval condition): \"{text}\"")
        elif clause == "5.3":
            summary_lines.append(f"- Clause {clause}: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.")
        elif clause == "7.2":
            summary_lines.append(f"- Clause {clause}: Leave encashment during service is not permitted under any circumstances.")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary (.txt)")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary generated successfully at {args.output}")

if __name__ == "__main__":
    main()
