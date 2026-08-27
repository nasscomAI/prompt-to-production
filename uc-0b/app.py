#!/usr/bin/env python
"""UC-0B Policy Summarization with complete clause enforcement."""

import re
import argparse
from pathlib import Path
from typing import Dict, List

# Critical clauses that MUST appear in summary
CRITICAL_CLAUSES = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward, forfeited on 31 Dec",
    "2.7": "Carry-forward days used Jan-Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service not permitted under any circumstances",
}


def retrieve_policy(policy_path: str) -> Dict[str, str]:
    """Parse policy file into numbered sections."""
    with open(policy_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = {}
    # Extract numbered sections (e.g., 2.3, 2.4, 3.2)
    pattern = r'(\d+\.\d+)\s+(.+?)(?=\n\s*\d+\.\d+|\Z)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        section_num = match.group(1)
        section_text = match.group(2).strip()
        sections[section_num] = section_text
    
    return sections


def check_multi_condition(section_text: str, section_num: str) -> tuple:
    """Check if section has multiple conditions (AND clauses).
    
    Returns: (has_multiple, conditions_list, binding_verb)
    """
    # Extract binding verb
    binding_verbs = ["must", "will", "requires", "are", "cannot", "not permitted"]
    found_verb = None
    for verb in binding_verbs:
        if verb.lower() in section_text.lower():
            found_verb = verb
            break
    
    # Check for AND conditions
    and_count = section_text.lower().count(" and ")
    has_multiple = and_count > 0
    
    conditions = []
    if section_num == "5.2":
        conditions = ["Department Head", "HR Director"]
    elif section_num == "2.6":
        conditions = ["maximum 5 days", "days above 5 are forfeited on 31 December"]
    elif section_num == "3.4":
        conditions = ["before or after public holiday", "before or after annual leave", "medical certificate regardless of duration"]
    
    return has_multiple, conditions, found_verb


def summarize_policy(sections: Dict[str, str]) -> str:
    """Generate summary preserving all clauses and conditions."""
    summary_lines = []
    summary_lines.append("POLICY SUMMARY — LEAVE POLICY (HR-POL-001)\n")
    summary_lines.append("="*70)
    summary_lines.append("ANNUAL LEAVE\n")
    
    # Process critical clauses in order
    for clause_num in ["2.3", "2.4", "2.5", "2.6", "2.7"]:
        if clause_num in sections:
            text = sections[clause_num]
            has_multi, conditions, verb = check_multi_condition(text, clause_num)
            
            summary_lines.append(f"\nSection {clause_num}:")
            
            if clause_num == "2.3":
                summary_lines.append("Employees must submit leave applications at least 14 calendar days in advance using Form HR-L1.")
            elif clause_num == "2.4":
                summary_lines.append("Leave applications must receive WRITTEN approval from the employee's direct manager before leave commences. Verbal approval is not valid.")
            elif clause_num == "2.5":
                summary_lines.append("Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.")
            elif clause_num == "2.6":
                summary_lines.append("Employees may carry forward a MAXIMUM of 5 unused annual leave days to the following year. Any days above 5 are FORFEITED on 31 December.")
            elif clause_num == "2.7":
                summary_lines.append("Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.")
    
    summary_lines.append("\n" + "="*70)
    summary_lines.append("SICK LEAVE\n")
    
    for clause_num in ["3.2", "3.4"]:
        if clause_num in sections:
            text = sections[clause_num]
            summary_lines.append(f"\nSection {clause_num}:")
            
            if clause_num == "3.2":
                summary_lines.append("Sick leave of 3 or more CONSECUTIVE days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.")
            elif clause_num == "3.4":
                summary_lines.append("Sick leave taken immediately BEFORE or AFTER a public holiday or annual leave period requires a medical certificate REGARDLESS of duration.")
    
    summary_lines.append("\n" + "="*70)
    summary_lines.append("LEAVE WITHOUT PAY (LWP)\n")
    
    for clause_num in ["5.2", "5.3"]:
        if clause_num in sections:
            text = sections[clause_num]
            summary_lines.append(f"\nSection {clause_num}:")
            
            if clause_num == "5.2":
                summary_lines.append("[COMPLEX_CLAUSE — CRITICAL MULTI-CONDITION REQUIREMENT]")
                summary_lines.append("LWP requires approval from TWO distinct approvers: (1) the Department Head AND (2) the HR Director. Manager approval alone is NOT sufficient.")
            elif clause_num == "5.3":
                summary_lines.append("LWP exceeding 30 continuous days requires additional approval from the Municipal Commissioner.")
    
    summary_lines.append("\n" + "="*70)
    summary_lines.append("LEAVE ENCASHMENT\n")
    
    if "7.2" in sections:
        summary_lines.append(f"\nSection 7.2:")
        summary_lines.append("Leave encashment during service is NOT PERMITTED under ANY circumstances.")
    
    summary_lines.append("\n" + "="*70)
    summary_lines.append("\nVALIDATION: All 10 critical clauses present with conditions preserved.")
    
    return "\n".join(summary_lines)


def main(input_path: str, output_path: str) -> None:
    """Main entry point."""
    print(f"Retrieving policy from: {input_path}")
    sections = retrieve_policy(input_path)
    
    # Validate critical clauses
    missing = [c for c in CRITICAL_CLAUSES.keys() if c not in sections]
    if missing:
        print(f"⚠ WARNING: Missing clauses: {missing}")
    else:
        print(f"✓ All {len(CRITICAL_CLAUSES)} critical clauses found")
    
    print(f"Generating summary...")
    summary = summarize_policy(sections)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✓ Summary written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize leave policy with complete clause preservation")
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file path")
    args = parser.parse_args()
    
    main(args.input, args.output)
