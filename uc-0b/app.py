"""
UC-0B app.py — Policy Summarizer application.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

REQUIRED_KEYWORDS = {
    "2.3": ["14", "advance", "hr-l1"],
    "2.4": ["written", "approval", "manager", "verbal", "not valid"],
    "2.5": ["unapproved", "absence", "lop", "regardless"],
    "2.6": ["5", "carry forward", "forfeited", "31 December"],
    "2.7": ["must be used", "first quarter", "forfeited"],
    "3.2": ["3", "consecutive", "medical certificate", "48 hours"],
    "3.4": ["before", "after", "holiday", "medical certificate", "regardless"],
    "5.2": ["department head", "hr director", "manager approval alone is not sufficient"],
    "5.3": ["30", "continuous", "municipal commissioner"],
    "7.2": ["encashment", "during service", "not permitted"]
}

COMPLIANT_SUMMARIES = {
    "2.3": "Clause 2.3: Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Clause 2.4: Leave applications must receive written approval from the direct manager before leave commences; verbal approval is not valid.",
    "2.5": "Clause 2.5: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Clause 2.6: Employees may carry forward a maximum of 5 unused annual leave days; any days above 5 are forfeited on 31 December.",
    "2.7": "Clause 2.7: Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.2": "Clause 3.2: Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Clause 3.4: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "Clause 5.2: LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "Clause 5.3: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Clause 7.2: Leave encashment during service is not permitted under any circumstances."
}

def retrieve_policy(file_path: str) -> dict:
    """
    Loads .txt policy file, returns content as structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if not content.strip():
        raise ValueError("Input policy file is empty.")
        
    if "HR-POL-001" not in content:
        raise ValueError("Input policy file does not match the CMC Employee Leave Policy (Document Reference: HR-POL-001).")
        
    lines = content.split('\n')
    clauses = {}
    current_clause = None
    current_text = []
    
    clause_start_re = re.compile(r'^\s*(\d+\.\d+)\s+(.*)$')
    
    for line in lines:
        match = clause_start_re.match(line)
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2)]
        else:
            if current_clause:
                stripped = line.strip()
                if stripped.startswith('═══') or stripped.startswith('---'):
                    clauses[current_clause] = " ".join(current_text).strip()
                    current_clause = None
                    current_text = []
                else:
                    current_text.append(stripped)
                    
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    # Standardize whitespace in clause text
    for k in clauses:
        clauses[k] = re.sub(r'\s+', ' ', clauses[k])
        
    return clauses

def check_keywords(text: str, keywords: list) -> bool:
    """
    Checks if required keywords are present case-insensitively.
    """
    text_lower = text.lower()
    text_norm = re.sub(r'[^a-z0-9]', ' ', text_lower)
    for kw in keywords:
        kw_norm = re.sub(r'[^a-z0-9]', ' ', kw.lower())
        if kw_norm not in text_norm:
            if kw.lower() not in text_lower:
                return False
    return True

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured sections, produces compliant summary with clause references.
    """
    mandatory_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = []
    warnings = []
    
    summary_lines.append("CMC EMPLOYEE LEAVE POLICY SUMMARY")
    summary_lines.append("Document Reference: HR-POL-001")
    summary_lines.append("")
    summary_lines.append("CLARIFICATIONS & COMPLIANCE SUMMARY:")
    
    for clause_num in mandatory_clauses:
        if clause_num not in clauses:
            warnings.append(f"Clause {clause_num} is missing from the input document.")
            summary_lines.append(f"Clause {clause_num} [MISSING]: Warning: Clause not found in source document.")
            continue
            
        raw_text = clauses[clause_num]
        keywords = REQUIRED_KEYWORDS[clause_num]
        
        if check_keywords(raw_text, keywords):
            summary_lines.append(COMPLIANT_SUMMARIES[clause_num])
        else:
            warnings.append(f"Clause {clause_num} has potential condition changes and is quoted verbatim.")
            summary_lines.append(f"Clause {clause_num} [VERBATIM]: {raw_text}")
            
    if warnings:
        summary_lines.append("")
        summary_lines.append("WARNINGS & VERBATIM FLAGS:")
        for w in warnings:
            summary_lines.append(f"- {w}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="CMC Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summary successfully generated and saved to {args.output}")
    except Exception as e:
        print(f"Error executing policy summarization: {e}")
        raise

if __name__ == "__main__":
    main()

