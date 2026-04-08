"""
UC-0B — Policy Summary Agent
Summarizes HR Leave Policy while preserving all 10 mandatory clauses.
Builds on RICE principles from agents.md and skills.md.
"""
import argparse
import re
from typing import Dict, List

# Required clauses that must be present in the summary
REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2"
]

# Binding verbs and their strengths
BINDING_VERBS = {
    "must": "MUST",
    "will": "WILL",
    "may": "MAY",
    "requires": "REQUIRES",
    "not permitted": "NOT PERMITTED",
    "cannot": "CANNOT"
}


def retrieve_policy(input_path: str) -> Dict[str, str]:
    """
    Load the HR Leave Policy .txt file and return content as structured sections.
    
    Returns:
        dict with keys:
        - 'header': document metadata
        - 'clauses': dict of clause_number -> clause_text
    """
    # Validate supported file
    if "policy_hr_leave.txt" not in input_path:
        raise ValueError("Only policy_hr_leave.txt is supported for UC-0B")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {input_path}")
    
    if not content.strip():
        raise ValueError("Policy file is empty")
    
    lines = content.split('\n')
    clauses = {}
    
    current_clause_num = None
    current_clause_text = []
    in_document_header = True
    
    for line in lines:
        stripped = line.strip()
        
        # Skip section headers (lines with ═ characters)
        if '═' in stripped:
            in_document_header = False
            continue
            
        # Skip empty lines when collecting text
        if not stripped:
            if current_clause_text:
                current_clause_text.append(' ')
            continue
        
        # Check if this is a section title like "3. SICK LEAVE" or "4. MATERNITY AND PATERNITY LEAVE"
        # Section titles are "X.Y TITLE" where TITLE is ALL CAPS (multiple words)
        # Pattern: starts with digit.digit, followed by space, then ALL CAPS words
        # IMPORTANT: Check this BEFORE clause_match because "3. SICK LEAVE" matches clause pattern too
        is_section_title = False
        # Match "X.Y WORD WORD..." where all words are uppercase
        section_pattern = re.match(r'^(\d+\.\d+)\s+([A-Z][A-Z\s&\-]+(\s+[A-Z][A-Z\s&\-]+)*)$', stripped)
        if section_pattern:
            # This looks like a section title (X.Y followed by all-caps title)
            is_section_title = True
        
        if is_section_title:
            # Save any previous clause before skipping
            if current_clause_num:
                clauses[current_clause_num] = ' '.join(current_clause_text).strip()
                current_clause_num = None
                current_clause_text = []
            continue
        
        # Check if this is a clause header (e.g., "2.3 Some clause text")
        # Clause text starts with lowercase letter or mixed case (sentence case)
        clause_match = re.match(r'^(\d+\.\d+)\s+([A-Za-z].*)', stripped)
        if clause_match:
            # Save previous clause
            if current_clause_num:
                clauses[current_clause_num] = ' '.join(current_clause_text).strip()
            
            current_clause_num = clause_match.group(1)
            current_clause_text = [clause_match.group(2)]
        elif current_clause_num:
            # This is continuation text for the current clause
            current_clause_text.append(stripped)
    
    # Save last clause
    if current_clause_num:
        clauses[current_clause_num] = ' '.join(current_clause_text).strip()
    
    return {
        'clauses': clauses
    }


def _extract_binding_verb(text: str) -> tuple:
    """Extract the binding verb and its strength from clause text."""
    text_lower = text.lower()
    for verb, strength in BINDING_VERBS.items():
        if verb in text_lower:
            return verb, strength
    return None, "STATEMENT"


def _check_critical_pairs(clause_num: str, text: str) -> List[str]:
    """Check for critical multi-condition pairs that must all be preserved."""
    warnings = []
    text_lower = text.lower()
    
    # Clause 5.2: Must have BOTH Department Head AND HR Director
    if clause_num == "5.2":
        has_dept_head = "department head" in text_lower
        has_hr_director = "hr director" in text_lower
        if has_dept_head and has_hr_director:
            warnings.append("Both approvers required: Department Head AND HR Director")
        elif has_dept_head or has_hr_director:
            warnings.append("WARNING: Missing one approver!")
    
    # Clause 2.6: Must have BOTH max 5 days AND 31 December
    if clause_num == "2.6":
        has_max_5 = "5" in text
        has_dec = "31 december" in text_lower or "31 december" in text_lower
        if has_max_5 and has_dec:
            warnings.append("Both conditions required: max 5 days AND forfeited 31 Dec")
    
    return warnings


def summarize_policy(policy_data: Dict) -> str:
    """
    Produce a compliant summary with all clause references preserved.
    Each clause includes its binding verb and all conditions.
    """
    clauses = policy_data['clauses']
    missing_clauses = []
    summary_lines = []
    
    # Document header
    summary_lines.append("=" * 60)
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("Source: policy_hr_leave.txt")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    
    # Process required clauses
    for clause_num in sorted(REQUIRED_CLAUSES, key=lambda x: tuple(map(int, x.split('.')))):
        if clause_num not in clauses:
            missing_clauses.append(clause_num)
            summary_lines.append(f"[MISSING-CLAUSE] {clause_num}: Clause not found in source document")
            continue
        
        clause_text = clauses[clause_num]
        verb, strength = _extract_binding_verb(clause_text)
        warnings = _check_critical_pairs(clause_num, clause_text)
        
        # Build formatted line
        summary_lines.append("")
        summary_lines.append(f"[{strength}] Clause {clause_num}: {clause_text}")
        
        # Add critical pair warnings
        if warnings:
            for warning in warnings:
                summary_lines.append(f"  ⚠ {warning}")
    
    # Report missing clauses
    if missing_clauses:
        summary_lines.append("")
        summary_lines.append("=" * 60)
        summary_lines.append(f"WARNING: {len(missing_clauses)} required clause(s) missing: {', '.join(missing_clauses)}")
        summary_lines.append("=" * 60)
    
    return '\n'.join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summary")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()
    
    # Validate input file is the supported policy
    if "policy_hr_leave.txt" not in args.input:
        raise ValueError("Only policy_hr_leave.txt is supported for UC-0B")
    
    # Retrieve and summarize
    policy_data = retrieve_policy(args.input)
    summary = summarize_policy(policy_data)
    
    # Write output
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary written to {args.output}")
    print(f"Processed {len(policy_data['clauses'])} clauses")
    
    # Check for missing required clauses
    missing = [c for c in REQUIRED_CLAUSES if c not in policy_data['clauses']]
    if missing:
        print(f"WARNING: Missing required clauses: {', '.join(missing)}")


if __name__ == "__main__":
    main()
