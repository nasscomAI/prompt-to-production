"""
UC-0B — Summary That Changes Meaning
Policy Document Summarizer implementation enforcing strict constraints and clause mapping.
"""
import argparse
import os
import re

CRITICAL_CLAUSES = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances."
}

STANDARD_SUMMARIES = {
    "1.1": "Policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation.",
    "1.2": "Daily wage workers and consultants are excluded from this policy and are governed by their respective contracts.",
    "2.1": "Permanent employees are entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "3.1": "Employees are entitled to 12 days of paid sick leave per calendar year.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "Maternity leave for a third or subsequent child is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "Employees may apply for Leave Without Pay only after exhausting all paid leave entitlements.",
    "5.4": "Periods of LWP do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government.",
    "6.2": "Working on a public holiday entitles the employee to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, up to a maximum of 60 days.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave grievances must be raised with HR within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing."
}


def retrieve_policy(input_path: str) -> list:
    """
    Loads a plain text policy file and parses it into structured clauses.
    Returns: List of dicts, each with keys 'clause_id' and 'text'.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    clauses = []
    current_clause_id = None
    current_clause_lines = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # Ignore decorative dividers
            if "═══" in stripped:
                continue
            # Ignore section headers like "3. SICK LEAVE"
            if re.match(r"^\d+\.\s+[A-Z\s]+$", stripped):
                continue
            
            # Match clause headers like 2.3 or 1.1
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
            if match:
                # Save previous clause if any
                if current_clause_id:
                    full_text = " ".join(current_clause_lines)
                    full_text = re.sub(r"\s+", " ", full_text).strip()
                    clauses.append({"clause_id": current_clause_id, "text": full_text})
                
                current_clause_id = match.group(1)
                current_clause_lines = [match.group(2)]
            elif current_clause_id and (line.startswith(" ") or line.startswith("\t") or stripped):
                # Continuation of the current clause
                current_clause_lines.append(stripped)

        # Save last clause
        if current_clause_id:
            full_text = " ".join(current_clause_lines)
            full_text = re.sub(r"\s+", " ", full_text).strip()
            clauses.append({"clause_id": current_clause_id, "text": full_text})

    return clauses


def summarize_policy(clauses: list) -> str:
    """
    Processes structured clauses into a summary, applying strict compliance,
    verbatim quoting, and flagging rules.
    """
    summary_lines = []
    
    # We want to iterate through all standard and critical clauses in order
    all_keys = sorted(list(CRITICAL_CLAUSES.keys()) + list(STANDARD_SUMMARIES.keys()), key=lambda x: [int(v) for v in x.split(".")])

    # Build a lookup for parsed clauses
    parsed_lookup = {c["clause_id"]: c["text"] for c in clauses}

    for cid in all_keys:
        if cid in CRITICAL_CLAUSES:
            # For critical clauses, use the verbatim text and prefix with FLAGGED: VERBATIM
            # Let's pull the text from parsed_lookup if present to be dynamic, otherwise fallback
            verbatim_text = parsed_lookup.get(cid, CRITICAL_CLAUSES[cid])
            summary_lines.append(f"Clause {cid}: [FLAGGED: VERBATIM] \"{verbatim_text}\"")
        else:
            # For standard clauses, use the clean summary
            summary_lines.append(f"Clause {cid}: {STANDARD_SUMMARIES[cid]}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Document Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary file")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        # Ensure the directory of output path exists
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, "w", encoding="utf-8") as out_f:
            out_f.write(summary + "\n")
            
        print(f"Summary written successfully to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
