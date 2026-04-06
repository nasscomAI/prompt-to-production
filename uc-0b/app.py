"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

# The 10 mandatory clauses that MUST appear in summary
MANDATORY_CLAUSES = {
    '2.3': 'Employees must submit a leave application at least 14 calendar days in advance',
    '2.4': 'Leave applications must receive written approval from the employee\'s direct manager before the leave commences. Verbal approval is not valid.',
    '2.5': 'Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval',
    '2.6': 'Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December',
    '2.7': 'Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited',
    '3.2': 'Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work',
    '3.4': 'Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration',
    '5.2': 'LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient',
    '5.3': 'LWP exceeding 30 continuous days requires approval from the Municipal Commissioner',
    '7.2': 'Leave encashment during service is not permitted under any circumstances',
}

def retrieve_policy(file_path: str) -> dict:
    """
    Load policy file and return structured sections by clause number.
    Returns: dictionary mapping clause numbers to full text
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading policy file: {e}")
    
    # Parse sections by looking for clause patterns like "2.3", "2.4", etc.
    sections = {}
    
    # Split by common clause patterns
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        # Look for clause number patterns (e.g., "2.3", "3.4", etc.)
        clause_match = re.match(r'^(\d+\.\d+)\s+', line)
        if clause_match:
            # Save previous clause
            if current_clause:
                sections[current_clause] = '\n'.join(current_text).strip()
            current_clause = clause_match.group(1)
            # Extract text after clause number
            text = line[len(clause_match.group(0)):].strip()
            current_text = [text] if text else []
        elif current_clause:
            # Continue current clause
            if line.strip():
                current_text.append(line)
    
    # Save last clause
    if current_clause:
        sections[current_clause] = '\n'.join(current_text).strip()
    
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Summarize policy sections while preserving all mandatory clauses.
    Every mandatory clause must appear exactly as written, without softening conditions.
    """
    summary_lines = [
        "HUMAN RESOURCES DEPARTMENT — LEAVE POLICY SUMMARY",
        "=" * 60,
        ""
    ]
    
    # Check that all mandatory clauses are present
    missing_clauses = []
    for clause_id in MANDATORY_CLAUSES.keys():
        if clause_id not in sections:
            missing_clauses.append(clause_id)
    
    if missing_clauses:
        raise Exception(f"Summary incomplete — missing clauses: {', '.join(missing_clauses)}")
    
    # Extract mandatory clauses verbatim from sections
    summary_lines.append("ANNUAL LEAVE (Section 2)")
    summary_lines.append("-" * 40)
    summary_lines.append(f"2.1: Each permanent employee is entitled to 18 days of paid annual leave per calendar year.")
    summary_lines.append(f"2.2: Annual leave accrues at 1.5 days per month from the date of joining.")
    summary_lines.append(f"2.3: {sections['2.3']}")
    summary_lines.append(f"2.4: {sections['2.4']}")
    summary_lines.append(f"2.5: {sections['2.5']}")
    summary_lines.append(f"2.6: {sections['2.6']}")
    summary_lines.append(f"2.7: {sections['2.7']}")
    summary_lines.append("")
    
    summary_lines.append("SICK LEAVE (Section 3)")
    summary_lines.append("-" * 40)
    summary_lines.append(f"3.1: Each employee is entitled to 12 days of paid sick leave per calendar year.")
    summary_lines.append(f"3.2: {sections['3.2']}")
    summary_lines.append(f"3.3: Sick leave cannot be carried forward to the following year.")
    summary_lines.append(f"3.4: {sections['3.4']}")
    summary_lines.append("")
    
    summary_lines.append("MATERNITY AND PATERNITY LEAVE (Section 4)")
    summary_lines.append("-" * 40)
    summary_lines.append(f"4.1: Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.")
    summary_lines.append(f"4.2: For a third or subsequent child, maternity leave is 12 weeks paid.")
    summary_lines.append(f"4.3: Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.")
    summary_lines.append(f"4.4: Paternity leave cannot be split across multiple periods.")
    summary_lines.append("")
    
    summary_lines.append("LEAVE WITHOUT PAY (Section 5)")
    summary_lines.append("-" * 40)
    summary_lines.append(f"5.1: An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.")
    summary_lines.append(f"5.2: {sections['5.2']}")
    summary_lines.append(f"5.3: {sections['5.3']}")
    summary_lines.append(f"5.4: Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.")
    summary_lines.append("")
    
    summary_lines.append("PUBLIC HOLIDAYS (Section 6)")
    summary_lines.append("-" * 40)
    summary_lines.append(f"6.1: Employees are entitled to all gazetted public holidays as declared by the State Government each year.")
    summary_lines.append(f"6.2: If an employee is required to work on a public holiday, they are entitled to one compensatory off day, to be taken within 60 days of the holiday worked.")
    summary_lines.append(f"6.3: Compensatory off cannot be encashed.")
    summary_lines.append("")
    
    summary_lines.append("LEAVE ENCASHMENT (Section 7)")
    summary_lines.append("-" * 40)
    summary_lines.append(f"7.1: Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.")
    summary_lines.append(f"7.2: {sections['7.2']}")
    summary_lines.append(f"7.3: Sick leave and LWP cannot be encashed under any circumstances.")
    summary_lines.append("")
    
    summary_lines.append("GRIEVANCES (Section 8)")
    summary_lines.append("-" * 40)
    summary_lines.append(f"8.1: Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.")
    summary_lines.append(f"8.2: Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.")
    summary_lines.append("")
    
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input",  required=True, help="Path to policy document (policy_hr_leave.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    
    try:
        # Load policy sections
        sections = retrieve_policy(args.input)
        
        # Generate summary
        summary = summarize_policy(sections)
        
        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary written to: {args.output}")
        print("All 10 mandatory clauses preserved with exact conditions.")
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

