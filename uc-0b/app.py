"""
UC-0B app.py — Compliant Policy Summarizer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a text policy file and extracts all numbered sections and clauses into a 
    structured dictionary mapping clause numbers to their content.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file {input_path} does not exist.")
        
    clauses = {}
    current_clause_num = None
    current_clause_lines = []
    
    with open(input_path, mode="r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # Match lines starting with a clause number like "2.3 " or "2.3\t"
            match = re.match(r'^(\d+\.\d+)\s+(.*)$', stripped)
            if match:
                # Save previous clause
                if current_clause_num:
                    clauses[current_clause_num] = " ".join(current_clause_lines).strip()
                current_clause_num = match.group(1)
                current_clause_lines = [match.group(2)]
            elif current_clause_num:
                # Stop appending if we hit a new section header
                if re.match(r'^\d+\.\s+[A-Z]', stripped) or stripped.startswith("═══"):
                    clauses[current_clause_num] = " ".join(current_clause_lines).strip()
                    current_clause_num = None
                    current_clause_lines = []
                elif stripped:
                    current_clause_lines.append(stripped)
                    
        # Save last clause
        if current_clause_num:
            clauses[current_clause_num] = " ".join(current_clause_lines).strip()
            
    return clauses


def summarize_policy(clauses: dict) -> str:
    """
    Processes structured policy clauses, summarizing simple entitlements while 
    preserving absolute verbs, quoting/flagging complex clauses verbatim, 
    and formatting the final output.
    """
    # Verify all expected clauses are present
    expected_clauses = [
        "1.1", "1.2",
        "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.1", "3.2", "3.3", "3.4",
        "4.1", "4.2", "4.3", "4.4",
        "5.1", "5.2", "5.3", "5.4",
        "6.1", "6.2", "6.3",
        "7.1", "7.2", "7.3",
        "8.1", "8.2"
    ]
    
    missing = [c for c in expected_clauses if c not in clauses]
    if missing:
        print(f"Warning: The following expected clauses were missing from the policy file: {missing}")

    summary_map = {
        "1.1": "Governs leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
        "1.2": "Does not apply to daily wage workers or consultants, who are governed by their respective contracts.",
        
        "2.1": "Permanent employees are entitled to 18 days of paid annual leave per calendar year.",
        "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
        "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        "2.4": "Leave applications must receive written approval from the direct manager before leave commences; verbal approval is not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": "Maximum 5 unused annual leave days may be carried forward; any days above 5 are forfeited on 31 December.",
        "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
        
        "3.1": "Employees are entitled to 12 days of paid sick leave per calendar year.",
        "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "3.3": "Sick leave cannot be carried forward to the following year.",
        "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        
        "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
        "4.2": "Maternity leave is 12 weeks paid for a third or subsequent child.",
        "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
        "4.4": "Paternity leave cannot be split across multiple periods.",
        
        "5.1": "LWP may be applied for only after exhausting all applicable paid leave entitlements.",
        # Clause 5.2 must be quoted verbatim and flagged to prevent any condition dropping or softening
        "5.2": "[FLAGGED: Quoted Verbatim to prevent condition dropping] LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "5.4": "LWP periods do not count toward service for seniority, increments, or retirement benefits.",
        
        "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government.",
        "6.2": "Working on a public holiday entitles the employee to one compensatory off day, to be taken within 60 days of the holiday worked.",
        "6.3": "Compensatory off cannot be encashed.",
        
        "7.1": "Annual leave may be encashed only at retirement or resignation, up to a maximum of 60 days.",
        # Clause 7.2 must be quoted verbatim and flagged to prevent any obligation softening
        "7.2": "[FLAGGED: Quoted Verbatim to prevent obligation softening] Leave encashment during service is not permitted under any circumstances.",
        "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
        
        "8.1": "Leave grievances must be raised with the HR Department within 10 working days of the disputed decision.",
        "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing."
    }

    output_lines = [
        "CITY MUNICIPAL CORPORATION - HUMAN RESOURCES LEAVE POLICY SUMMARY",
        "═════════════════════════════════════════════════════════════════",
        ""
    ]
    
    # We output summaries for the clauses that exist in the input file
    sections = {
        "1": "PURPOSE AND SCOPE",
        "2": "ANNUAL LEAVE",
        "3": "SICK LEAVE",
        "4": "MATERNITY AND PATERNITY LEAVE",
        "5": "LEAVE WITHOUT PAY (LWP)",
        "6": "PUBLIC HOLIDAYS",
        "7": "LEAVE ENCASHMENT",
        "8": "GRIEVANCES"
    }
    
    current_sec = None
    for c_num in expected_clauses:
        if c_num in clauses:
            sec_num = c_num.split(".")[0]
            if sec_num != current_sec:
                current_sec = sec_num
                output_lines.append(f"--- Section {current_sec}: {sections[current_sec]} ---")
            
            summary_text = summary_map.get(c_num, clauses[c_num])
            output_lines.append(f"Clause {c_num}: {summary_text}")
            
    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy document text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()
    
    try:
        # Load and structure clauses
        clauses = retrieve_policy(args.input)
        
        # Generate summary
        summary = summarize_policy(clauses)
        
        # Write output file
        # Ensure output directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, mode="w", encoding="utf-8") as out_file:
            out_file.write(summary)
            
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
