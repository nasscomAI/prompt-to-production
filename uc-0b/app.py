import argparse
import re
import sys

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

MANDATORY_CLAUSES = {
    "2.3": "14-day advance notice required using Form HR-L1",
    "2.4": "Written approval required before leave commences; verbal approval not valid",
    "2.5": "Unapproved absence = Loss of Pay (LOP) regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward; above 5 forfeited on 31 December",
    "2.7": "Carry-forward days must be used Jan-Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires BOTH Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service NOT permitted under any circumstances"
}

def retrieve_policy(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = {}
    lines = content.split('\n')
    current_clause = None
    current_text = ""
    
    for line in lines:
        match = re.match(r'^(\d+\.\d+)\s+(.+)$', line.strip())
        if match:
            if current_clause:
                sections[current_clause] = current_text.strip()
            current_clause = match.group(1)
            current_text = match.group(2).strip()
        elif current_clause and line.strip():
            current_text += " " + line.strip()
    
    if current_clause:
        sections[current_clause] = current_text.strip()
    
    return sections

def summarize_policy(policy_sections):
    missing_clauses = []
    summary_lines = []
    
    for clause_id in REQUIRED_CLAUSES:
        if clause_id in policy_sections:
            text = policy_sections[clause_id]
            if clause_id == "5.2":
                if "Department Head" not in text or "HR Director" not in text:
                    missing_clauses.append(clause_id)
                else:
                    summary_lines.append(f"Clauses {clause_id}: {text}")
            else:
                summary_lines.append(f"Clauses {clause_id}: {text}")
        else:
            missing_clauses.append(clause_id)
    
    if missing_clauses:
        print(f"ERROR: Missing clauses: {missing_clauses}")
        sys.exit(1)
    
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description='Summarize HR leave policy')
    parser.add_argument('--input', required=True, help='Input policy file')
    parser.add_argument('--output', required=True, help='Output summary file')
    args = parser.parse_args()
    
    policy_sections = retrieve_policy(args.input)
    summary = summarize_policy(policy_sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()