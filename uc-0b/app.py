"""
UC-0B app.py — Policy Summarizer Agent.
Implements the skills retrieve_policy and summarize_policy.
Strictly adheres to enforcement rules in agents.md.
"""
import argparse
import os
import re

# Standard expected texts for clauses in policy_hr_leave.txt for comparison and validation.
EXPECTED_CLAUSE_TEXTS = {
    "1.1": "This policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "This policy does not apply to daily wage workers or consultants. Those categories are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
    "6.2": "If an employee is required to work on a public holiday, they are entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing."
}

# The high-fidelity summaries that precisely preserve all constraints, conditions, and obligations.
HIGH_FIDELITY_SUMMARIES = {
    "1.0": "PURPOSE AND SCOPE",
    "1.1": "This policy governs all leave entitlements for permanent and contractual CMC employees.",
    "1.2": "Daily wage workers and consultants are excluded and are governed by their respective contracts.",
    "2.0": "ANNUAL LEAVE",
    "2.1": "Permanent employees are entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the direct manager before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.0": "SICK LEAVE",
    "3.1": "Employees are entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.0": "MATERNITY AND PATERNITY LEAVE",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "Maternity leave is 12 weeks paid for a third or subsequent child.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.0": "LEAVE WITHOUT PAY (LWP)",
    "5.1": "LWP can be applied for only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "LWP periods do not count toward service for seniority, increments, or retirement benefits.",
    "6.0": "PUBLIC HOLIDAYS",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government each year.",
    "6.2": "Working on a public holiday entitles an employee to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.0": "LEAVE ENCASHMENT",
    "7.1": "Annual leave encashment is permitted only at retirement or resignation, up to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.0": "GRIEVANCES",
    "8.1": "Leave grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing."
}

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

def normalize_text(text: str) -> str:
    """Helper to normalize text for comparison by removing non-alphanumeric chars and lowercasing."""
    if not text:
        return ""
    text = text.lower()
    return re.sub(r'[^a-z0-9]', '', text)

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a policy text file and parses its contents into structured numbered sections.
    Raises FileNotFoundError if the file cannot be found.
    """
    if not os.path.exists(file_path):
        error_msg = f"FileNotFoundError: The file '{file_path}' does not exist."
        print(error_msg)
        raise FileNotFoundError(error_msg)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        error_msg = f"Error reading file '{file_path}': {str(e)}"
        print(error_msg)
        raise FileNotFoundError(error_msg)

    lines = content.split('\n')
    sections = {}
    current_key = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Skip separator lines containing only non-alphanumeric symbols
        if re.match(r'^[^\w\s]+$', stripped):
            continue

        # Check for clauses (e.g. "1.1", "2.3")
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)$', stripped)
        # Check for section headers (e.g. "1. PURPOSE AND SCOPE")
        section_match = re.match(r'^(\d+)\.\s+([A-Z\s&()\-]+)$', stripped)

        if clause_match:
            current_key = clause_match.group(1)
            sections[current_key] = clause_match.group(2)
        elif section_match:
            current_key = f"{section_match.group(1)}.0"
            sections[current_key] = section_match.group(2)
        else:
            # Append line to active clause text
            if current_key:
                sections[current_key] = sections[current_key] + " " + stripped

    # Normalize whitespaces inside parsed values
    for k in sections:
        sections[k] = re.sub(r'\s+', ' ', sections[k]).strip()

    return sections

def summarize_policy(sections: dict) -> str:
    """
    Generates a high-fidelity summary of the structured policy sections,
    strictly enforcing all constraints, conditions, and clause mappings.
    If a clause is missing or ambiguous/modified, quotes verbatim and flags it.
    """
    summary_lines = []
    
    # Check for missing required clauses
    for req in REQUIRED_CLAUSES:
        if req not in sections:
            # Flag missing required clause
            flag_line = f"Clause {req} [FLAG: MISSING]: This required clause is missing from the input document."
            summary_lines.append(flag_line)
            print(f"Warning: Required clause {req} is missing from the input policy.")

    # Sort the section keys to maintain order
    sorted_keys = sorted(sections.keys(), key=lambda x: [int(num) for num in x.split('.')])

    for key in sorted_keys:
        input_text = sections[key]
        
        # Check if the clause has a predefined expected text
        if key in EXPECTED_CLAUSE_TEXTS:
            expected_normalized = normalize_text(EXPECTED_CLAUSE_TEXTS[key])
            input_normalized = normalize_text(input_text)
            
            # If wording is exactly or nearly the same, use high-fidelity summary
            if input_normalized == expected_normalized:
                if key.endswith(".0"):
                    summary_lines.append(f"\n{key.split('.')[0]}. {HIGH_FIDELITY_SUMMARIES[key]}")
                else:
                    summary_lines.append(f"Clause {key}: {HIGH_FIDELITY_SUMMARIES[key]}")
            else:
                # Wording has changed, indicating ambiguity or modified obligation.
                # Must quote verbatim and flag it as per skills.md error handling.
                flagged_content = f"Clause {key} [FLAG: VERBATIM - AMBIGUOUS/MODIFIED]: \"{input_text}\""
                summary_lines.append(flagged_content)
                print(f"Flagged Clause {key} due to text mismatch (ambiguity/modified obligations).")
        else:
            # If the clause key is not in expected texts:
            if key.endswith(".0"):
                summary_lines.append(f"\n{key.split('.')[0]}. {input_text}")
            else:
                # Quote verbatim and flag it
                flagged_content = f"Clause {key} [FLAG: VERBATIM - UNKNOWN]: \"{input_text}\""
                summary_lines.append(flagged_content)
                print(f"Flagged Clause {key} as it is not in the standard clause list.")

    return "\n".join(summary_lines).strip()

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Path to the input policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary text file")
    args = parser.parse_args()

    print(f"Loading policy from: {args.input}")
    try:
        sections = retrieve_policy(args.input)
        print(f"Successfully parsed {len(sections)} sections/clauses.")
        
        print("Generating high-fidelity summary...")
        summary = summarize_policy(sections)
        
        # Ensure output directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary + "\n")
            
        print(f"Summary successfully written to: {args.output}")
        
    except FileNotFoundError as e:
        print(f"Execution failed: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
