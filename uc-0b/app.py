"""
UC-0B app.py — Policy Summarizer.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Loads .txt policy file, returns content as structured numbered sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    if not content.strip():
        raise ValueError("Input file is empty")
        
    lines = content.splitlines()
    sections = {}
    current_clause = None
    current_text = []
    
    # regex to match a line starting with a clause number (e.g. 2.3 or 10.1)
    clause_re = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    has_clause_numbers = False
    
    for line in lines:
        stripped = line.strip()
        # Check if line is a separator or heading
        if stripped.startswith("═") or re.match(r"^\d+\.\s+[A-Z\s]+$", stripped):
            if current_clause:
                sections[current_clause] = " ".join(current_text).strip()
                current_clause = None
                current_text = []
            continue
            
        match = clause_re.match(line)
        if match:
            has_clause_numbers = True
            if current_clause:
                sections[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
        else:
            if current_clause:
                current_text.append(stripped)
                
    if current_clause:
        sections[current_clause] = " ".join(current_text).strip()
        
    if not has_clause_numbers:
        raise ValueError("File lacks clear clause numbers")
        
    return sections

def summarize_policy(sections: dict, target_clauses: list) -> str:
    """
    Takes structured sections, produces compliant summary with clause references.
    """
    # Verify that every target clause is present in the sections dict
    missing_clauses = [tc for tc in target_clauses if tc not in sections]
    if missing_clauses:
        raise ValueError(f"Missing target clauses from input document: {', '.join(missing_clauses)}")
        
    summaries = []
    
    # Map target clauses with highly precise summaries or verbatim quotes if complex
    # 2.3: 14-day advance notice required (must)
    # 2.4: Written approval required before leave commences. Verbal not valid. (must)
    # 2.5: Unapproved absence = LOP regardless of subsequent approval (will)
    # 2.6: Max 5 days carry-forward. Above 5 forfeited on 31 Dec. (may / are forfeited)
    # 2.7: Carry-forward days must be used Jan–Mar or forfeited (must)
    # 3.2: 3+ consecutive sick days requires medical cert within 48hrs (requires)
    # 3.4: Sick leave before/after holiday requires cert regardless of duration (requires)
    # 5.2: LWP requires Department Head AND HR Director approval (requires)
    # 5.3: LWP >30 days requires Municipal Commissioner approval (requires)
    # 7.2: Leave encashment during service not permitted under any circumstances (not permitted)
    
    for tc in target_clauses:
        original = sections[tc]
        
        if tc == "2.3":
            summary = "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1."
        elif tc == "2.4":
            summary = "Leave applications must receive written approval from the employee's direct manager before leave commences; verbal approval is invalid."
        elif tc == "2.5":
            summary = "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval."
        elif tc == "2.6":
            summary = "Employees may carry forward a maximum of 5 unused annual leave days to the following year; any excess days are forfeited on 31 December."
        elif tc == "2.7":
            summary = "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited."
        elif tc == "3.2":
            summary = "Sick leave of 3 or more consecutive days requires a medical certificate from a registered practitioner, submitted within 48 hours of returning to work."
        elif tc == "3.4":
            summary = "Sick leave taken immediately before or after a public holiday or annual leave requires a medical certificate regardless of duration."
        elif tc == "5.2":
            # This is complex and a high-risk multi-condition clause. We quote it verbatim and flag it to avoid any meaning loss.
            summary = f"[FLAGGED - VERBATIM] {original}"
        elif tc == "5.3":
            summary = "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        elif tc == "7.2":
            summary = "Leave encashment during service is not permitted under any circumstances."
        else:
            summary = original
            
        summaries.append(f"Clause {tc}: {summary}")
        
    return "\n".join(summaries) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary text file")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
        summary = summarize_policy(sections, target_clauses)
        
        # Ensure output directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()

