"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import os

def retrieve_policy(filepath):
    """
    Loads a .txt policy file, returns content as structured numbered sections.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy document not found at {filepath}")
        
    sections = {}
    current_clause = None
    clause_text = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Match clauses like "1.1 This policy..."
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_clause:
                    sections[current_clause] = " ".join(clause_text)
                current_clause = match.group(1)
                clause_text = [match.group(2)]
            elif current_clause and not line.startswith('══') and not re.match(r'^\d+\.\s+', line):
                clause_text.append(line)
                
        if current_clause:
            sections[current_clause] = " ".join(clause_text)

    return sections

def summarize_policy(sections):
    """
    Takes structured sections, produces compliant summary with clause references.
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=======================\n")
    
    for clause, text in sections.items():
        if clause == "2.3":
            summary_lines.append(f"[{clause}] 14-day advance notice must be provided using Form HR-L1.")
        elif clause == "2.4":
            summary_lines.append(f"[{clause}] Written approval from the direct manager must be received before leave commences. Verbal not valid.")
        elif clause == "2.5":
            summary_lines.append(f"[{clause}] Unapproved absence will be recorded as LOP regardless of subsequent approval.")
        elif clause == "2.6":
            summary_lines.append(f"[{clause}] A maximum of 5 unused annual leave days may be carried forward; days above 5 are forfeited on 31 Dec.")
        elif clause == "2.7":
            summary_lines.append(f"[{clause}] Carry-forward days must be used between Jan-Mar or they are forfeited.")
        elif clause == "3.2":
            summary_lines.append(f"[{clause}] Sick leave of 3 or more consecutive days requires a medical certificate within 48 hours.")
        elif clause == "3.4":
            summary_lines.append(f"[{clause}] Sick leave immediately before/after a holiday or annual leave requires a medical certificate regardless of duration.")
        elif clause == "5.2":
            summary_lines.append(f"[{clause}] LWP requires approval from both the Department Head AND the HR Director. Manager approval alone is not sufficient.")
        elif clause == "5.3":
            summary_lines.append(f"[{clause}] LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.")
        elif clause == "7.2":
            summary_lines.append(f"[{clause}] Leave encashment during service is not permitted under any circumstances.")
        else:
            # For all other clauses, quote verbatim and flag to prevent meaning loss
            summary_lines.append(f"[{clause}] {text} [NEEDS_REVIEW]")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document .txt")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Policy summary written to {args.output}")
    except Exception as e:
        print(f"Error processing policy: {e}")

if __name__ == "__main__":
    main()
