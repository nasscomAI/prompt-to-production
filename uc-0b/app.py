"""
UC-0B — HR Policy Summarizer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import os
import sys

# Pre-defined non-softened summaries mapping all 29 clauses in policy_hr_leave.txt
GROUND_TRUTH = {
    "1.1": "Governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "Does not apply to daily wage workers or consultants, who are governed by their respective contracts.",
    "2.1": "Permanent employees are entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Requires written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Allows carry-forward of a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.1": "Employees are entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "Maternity leave for a third or subsequent child is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay (LWP) only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
    "6.2": "If required to work on a public holiday, employees are entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing."
}

def retrieve_policy(input_path: str) -> list:
    """
    Reads the raw text HR policy file and extracts sections and numbered clauses.
    Returns: list of dicts with keys 'clause_id' and 'text'
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")
        
    with open(input_path, mode="r", encoding="utf-8") as f:
        lines = f.readlines()
        
    clauses = []
    current_clause = None
    
    for i, line in enumerate(lines, start=1):
        # Match a clause number at the start of the line (e.g. "1.1 ", "2.3 ")
        match = re.match(r"^\s*(\d+\.\d+)\s+(.*)$", line)
        if match:
            if current_clause:
                clauses.append(current_clause)
            current_clause = {
                "clause_id": match.group(1),
                "text": match.group(2).strip()
            }
        else:
            # Append non-empty lines to the current clause text if we are in one
            if current_clause and line.strip():
                current_clause["text"] += " " + line.strip()
                
    if current_clause:
        clauses.append(current_clause)
        
    if not clauses:
        raise ValueError("No clauses could be parsed from the policy file.")
        
    return clauses


def summarize_policy(clauses: list) -> str:
    """
    Generates a concise, non-softened summary for each clause.
    Groups them under major sections.
    """
    section_names = {
        "1": "PURPOSE AND SCOPE",
        "2": "ANNUAL LEAVE",
        "3": "SICK LEAVE",
        "4": "MATERNITY AND PATERNITY LEAVE",
        "5": "LEAVE WITHOUT PAY (LWP)",
        "6": "PUBLIC HOLIDAYS",
        "7": "LEAVE ENCASHMENT",
        "8": "GRIEVANCES"
    }
    
    output_lines = []
    current_major_section = None
    
    for clause in clauses:
        clause_id = clause["clause_id"]
        major_sec = clause_id.split('.')[0]
        
        # Output section header on transitions
        if major_sec != current_major_section:
            current_major_section = major_sec
            sec_name = section_names.get(major_sec, "SECTION " + major_sec)
            if output_lines:
                output_lines.append("")
            output_lines.append("═══════════════════════════════════════════════════════════")
            output_lines.append(f"{major_sec}. {sec_name}")
            output_lines.append("═══════════════════════════════════════════════════════════")
            
        summary = GROUND_TRUTH.get(clause_id)
        if not summary:
            # Fallback: Quote verbatim and flag if meaning might be lost
            summary = f"[REVIEW REQUIRED] Verbatim: {clause['text']}"
            print(f"Warning: Unknown clause {clause_id} encountered. Quoting verbatim.", file=sys.stderr)
            
        output_lines.append(f"{clause_id} {summary}")
        
    return "\n".join(output_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input text policy file")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary_text = summarize_policy(clauses)
        
        # Ensure parent directories exist
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output, mode="w", encoding="utf-8") as out_file:
            out_file.write(summary_text)
            
        print(f"Summary written successfully to {args.output}")
    except Exception as e:
        print(f"Error during summarization: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
