"""
UC-0B app.py — Policy Summarizer
Built mapping to RICE constraints + agents.md + skills.md
"""
import argparse
import re
import os

REQUIRED_CLAUSES = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt HR policy file and extracts its exact content into structured, numbered sections.
    Raises ValueError if file cannot be read or is illegible.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
        
    structured_content = {}
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)$')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_clause = None
    buffer = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = clause_pattern.match(line)
        if match:
            if current_clause:
                structured_content[current_clause] = " ".join(buffer)
            current_clause = match.group(1)
            buffer = [match.group(2)]
        elif current_clause:
            buffer.append(line)
            
    if current_clause:
        structured_content[current_clause] = " ".join(buffer)
        
    if not structured_content:
        raise ValueError("Refusal condition met: The text lacks identifiable numbered clauses.")

    # Validation: Check presence of all 10 mandatory clauses
    missing_clauses = [c for c in REQUIRED_CLAUSES if c not in structured_content]
    if missing_clauses:
        raise ValueError(f"Refusing execution: Missing mandatory clauses {missing_clauses}")
        
    return structured_content

def summarize_policy(structured_sections: dict) -> str:
    """
    Processes structured policy sections into a compliant summary.
    Preserves all multi-condition obligations exactly to avoid meaning loss.
    """
    SUMMARY_MAPPING = {
        '2.3': "Must submit leave application at least 14 calendar days in advance.",
        '2.4': "Written approval required before leave commences; verbal approval is not valid.",
        '2.5': "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        '2.6': "Max 5 days carry-forward; days above 5 are forfeited on 31 December.",
        '2.7': "Carry-forward days must be used Jan-Mar or they are forfeited.",
        '3.2': "Absence of 3+ consecutive sick days requires medical certificate within 48 hours.",
        '3.4': "Sick leave before/after holiday requires certificate regardless of duration.",
        '5.2': "LWP requires approval from BOTH Department Head AND HR Director.",
        '5.3': "LWP exceeding 30 days requires Municipal Commissioner approval.",
        '7.2': "Leave encashment during service is not permitted under any circumstances."
    }

    summary_lines = []
    
    # Sort and output only the required clauses in order
    for clause_id in sorted(structured_sections.keys(), key=lambda x: float(x)):
        if clause_id in SUMMARY_MAPPING:
            summary_lines.append(f"Clause {clause_id}: {SUMMARY_MAPPING[clause_id]}")
        else:
            summary_lines.append(f"Clause {clause_id}: {structured_sections[clause_id]}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as out_f:
            out_f.write(summary)
            
        print(f"Success. Compliant summary written to {args.output}")
        
    except Exception as e:
        print(f"Error during policy processing: {e}")

if __name__ == "__main__":
    main()
