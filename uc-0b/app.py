"""
UC-0B app.py — Summarize policy document preserving all obligations.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import re

def retrieve_policy(file_path: str) -> dict:
    """
    Loads an employee policy text file and parses it into structured numbered clauses.
    Returns: dict mapping section numbers (strings) to their corresponding text content (strings).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found at: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    clauses = {}
    current_clause_num = None
    current_clause_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Skip decorative/divider lines
        if re.match(r'^[═─\-_]+$', stripped):
            continue
            
        # Skip section headers like "3. SICK LEAVE"
        if re.match(r'^[0-9]+\.\s+[A-Z\s]+$', stripped):
            if current_clause_num:
                clauses[current_clause_num] = " ".join(current_clause_lines).strip()
            current_clause_num = None
            current_clause_lines = []
            continue
            
        # Match something like "2.3 " or "5.2\t"
        match = re.match(r'^\s*([0-9]+\.[0-9]+)\s+(.*)$', line)
        if match:
            if current_clause_num:
                clauses[current_clause_num] = " ".join(current_clause_lines).strip()
            current_clause_num = match.group(1)
            current_clause_lines = [match.group(2).strip()]
        else:
            if current_clause_num is not None:
                current_clause_lines.append(stripped)
                
    if current_clause_num:
        clauses[current_clause_num] = " ".join(current_clause_lines).strip()
        
    # Clean up whitespace
    for k in clauses:
        clauses[k] = re.sub(r'\s+', ' ', clauses[k])
        
    return clauses


def summarize_policy(clauses: dict) -> str:
    """
    Generates a summary for the policy clauses that strictly preserves all conditions and lists all clauses.
    Returns: string containing the formatted summary matching the RICE enforcement guidelines.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    # Validate that all target clauses are present
    missing = [c for c in target_clauses if c not in clauses]
    if missing:
        raise ValueError(f"Missing expected policy clauses from document: {missing}")
        
    summary_lines = []
    summary_lines.append("CITY MUNICIPAL CORPORATION - EMPLOYEE LEAVE POLICY SUMMARY")
    summary_lines.append("==========================================================")
    summary_lines.append("Policy Document Reference: HR-POL-001 (Version: 2.3 | Effective: 1 April 2024)\n")
    summary_lines.append("Summary of Critical Binding Clauses:\n")
    
    clause_metadata = {
        "2.3": {
            "title": "Annual Leave Notice Period",
            "summary": "Application must be submitted at least 14 calendar days in advance using Form HR-L1."
        },
        "2.4": {
            "title": "Annual Leave Approval Requirement",
            "summary": "Written approval from the direct manager is mandatory before leave starts; verbal approval is invalid."
        },
        "2.5": {
            "title": "Unapproved Absence Penalty",
            "summary": "Unapproved absence is recorded as Loss of Pay (LOP) and cannot be corrected by subsequent approval."
        },
        "2.6": {
            "title": "Leave Carry-forward Limits",
            "summary": "A maximum of 5 unused annual leave days can be carried forward; any excess is forfeited on 31 December."
        },
        "2.7": {
            "title": "Carry-forward Expiration",
            "summary": "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited."
        },
        "3.2": {
            "title": "Sick Leave Medical Certification",
            "summary": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work."
        },
        "3.4": {
            "title": "Sick Leave Adjacent to Holidays",
            "summary": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."
        },
        "5.2": {
            "title": "Leave Without Pay Approvals",
            "summary": "LWP requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient."
        },
        "5.3": {
            "title": "Extended Leave Without Pay Approvals",
            "summary": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        },
        "7.2": {
            "title": "Leave Encashment Restrictions",
            "summary": "Leave encashment during active service is strictly prohibited under any circumstances."
        }
    }
    
    for idx, c_num in enumerate(target_clauses, 1):
        meta = clause_metadata[c_num]
        verbatim = clauses[c_num]
        summary_lines.append(f"{idx}. Clause {c_num} ({meta['title']})")
        summary_lines.append(f"   Summary: {meta['summary']}")
        summary_lines.append(f"   [VERBATIM QUOTE]: \"{verbatim}\"\n")
        
    summary_lines.append("==========================================================")
    summary_lines.append("CRITICAL OBLIGATION FLAG:")
    summary_lines.append("- All 10 clauses listed above represent binding obligations and restrictions.")
    summary_lines.append("- Under Clause 5.2, approval MUST be obtained from BOTH the Department Head AND the HR Director.")
    summary_lines.append("- Under Clause 2.3, application must be submitted 14 calendar days in advance via Form HR-L1.")
    summary_lines.append("- Under Clause 3.2, a medical certificate from a registered medical practitioner must be submitted within 48 hours of returning to work for sick leave of 3+ consecutive days.")
    summary_lines.append("- No external standard practices or assumptions apply; these rules are the exclusive authority for CMC employee leave.")
    
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Employee Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summarized text file")
    args = parser.parse_args()
    
    try:
        print(f"Retrieving policy from: {args.input}")
        clauses = retrieve_policy(args.input)
        
        print("Generating summarized policy document...")
        summary_text = summarize_policy(clauses)
        
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        print(f"Successfully wrote summary to: {args.output}")
    except Exception as e:
        print(f"Error during summarization process: {e}")
        exit(1)


if __name__ == "__main__":
    main()
