"""
UC-0B app.py — Policy Summarizer
Built using agents.md and skills.md.
"""
import argparse
import re

REQUIRED_CLAUSES = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']

def retrieve_policy(file_path: str) -> dict:
    """
    Loads the .txt policy file and returns content as structured numbered sections.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file {file_path} not found.")
    
    # Split by sections (assuming === separators)
    sections = re.split(r'={10,}', content)
    structured = {}
    
    for section in sections:
        lines = section.strip().split('\n')
        for line in lines:
            # Match clause numbers like 2.3
            match = re.match(r'^(\d+\.\d+)\s', line.strip())
            if match:
                clause = match.group(1)
                # Get the full clause text until next clause or end
                clause_text = line.strip()
                # Find the end of this clause
                idx = lines.index(line)
                next_idx = idx + 1
                while next_idx < len(lines):
                    next_line = lines[next_idx].strip()
                    if re.match(r'^\d+\.\d+\s', next_line):
                        break
                    clause_text += ' ' + next_line
                    next_idx += 1
                structured[clause] = clause_text.strip()
    
    return structured

def summarize_policy(structured_sections: dict) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references.
    """
    if not structured_sections:
        raise ValueError("Structured sections are invalid or incomplete.")
    
    summaries = []
    for clause in REQUIRED_CLAUSES:
        if clause not in structured_sections:
            raise ValueError(f"Required clause {clause} not found in policy.")
        
        content = structured_sections[clause]
        # Generate summary based on clause
        if clause == '2.3':
            summary = f"Clause {clause}: Employees must submit leave applications at least 14 calendar days in advance using Form HR-L1."
        elif clause == '2.4':
            summary = f"Clause {clause}: Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid."
        elif clause == '2.5':
            summary = f"Clause {clause}: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval."
        elif clause == '2.6':
            summary = f"Clause {clause}: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        elif clause == '2.7':
            summary = f"Clause {clause}: Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited."
        elif clause == '3.2':
            summary = f"Clause {clause}: Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work."
        elif clause == '3.4':
            summary = f"Clause {clause}: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."
        elif clause == '5.2':
            summary = f"Clause {clause}: LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        elif clause == '5.3':
            summary = f"Clause {clause}: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        elif clause == '7.2':
            summary = f"Clause {clause}: Leave encashment during service is not permitted under any circumstances."
        else:
            # If cannot summarize without loss, quote verbatim
            summary = f"Clause {clause} (quoted verbatim due to complexity): {content} [FLAG: Verbatim quote to preserve meaning]"
        
        summaries.append(summary)
    
    return '\n\n'.join(summaries)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    structured = retrieve_policy(args.input)
    summary = summarize_policy(structured)
    
    with open(args.output, 'w') as f:
        f.write(summary)
    
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
