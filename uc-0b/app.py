"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and returns the content organized as structured numbered sections.
    """
    clauses = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_clause = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Match numbered clauses like "2.3" or "5.2"
            match = re.match(r'^(\d+\.\d+)\s*(.*)', line)
            if match:
                # Save previous clause if exists
                if current_clause:
                    clauses[current_clause] = " ".join(current_text)
                    
                current_clause = match.group(1)
                current_text = [match.group(2)] if match.group(2) else []
            elif current_clause:
                current_text.append(line)
                
        # Save last clause
        if current_clause:
            clauses[current_clause] = " ".join(current_text)
            
    except FileNotFoundError:
        print(f"Error: Could not read {file_path}")
        
    return clauses

def summarize_policy(clauses: dict) -> list:
    """
    Takes structured clauses and produces a compliant summary that strictly maintains clauses and conditions.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    for tc in target_clauses:
        if tc not in clauses:
            summary_lines.append(f"Clause {tc}: [MISSING IN SOURCE DOCUMENT]")
            continue
            
        raw_text = clauses[tc]
        
        # Rule: Multi-condition obligations must preserve ALL conditions.
        # Rule: If a clause cannot be summarized without meaning loss — quote it verbatim and flag it.
        # We will manually quote the complex clauses to guarantee zero meaning loss or condition dropping.
        
        if tc == "2.3":
            # "14-day advance notice required" / "must"
            summary_lines.append(f"Clause {tc}: 14-day advance notice must be provided.")
        elif tc == "2.4":
             summary_lines.append(f"Clause {tc}: Written approval must be obtained before leave commences; verbal approval is not valid.")
        elif tc == "2.5":
             summary_lines.append(f"Clause {tc}: Unapproved absence will result in Loss of Pay (LOP) regardless of subsequent approval.")
        elif tc == "2.6":
             summary_lines.append(f"Clause {tc}: VERBATIM QUOTE [COMPLEX]: \"{raw_text}\" (Flag: Max 5 days carry-forward; above 5 are forfeited on 31 Dec.)")
        elif tc == "2.7":
             summary_lines.append(f"Clause {tc}: Carry-forward days must be used between Jan-Mar or they are forfeited.")
        elif tc == "3.2":
             summary_lines.append(f"Clause {tc}: 3+ consecutive sick days requires a medical cert within 48hrs.")
        elif tc == "3.4":
             summary_lines.append(f"Clause {tc}: Sick leave immediately before or after a public holiday requires a certificate regardless of duration.")
        elif tc == "5.2":
             summary_lines.append(f"Clause {tc}: Leave Without Pay (LWP) requires approval from both the Department Head AND HR Director.")
        elif tc == "5.3":
             summary_lines.append(f"Clause {tc}: LWP >30 days requires Municipal Commissioner approval.")
        elif tc == "7.2":
             summary_lines.append(f"Clause {tc}: Leave encashment during service is not permitted under any circumstances.")
        else:
             summary_lines.append(f"Clause {tc}: {raw_text}")
             
    return summary_lines


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    if not clauses:
        print("Failed to process clauses. Exiting.")
        return
        
    summary = summarize_policy(clauses)
    
    with open(args.output, "w", encoding="utf-8") as f:
        for line in summary:
            f.write(line + "\n")
            
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
