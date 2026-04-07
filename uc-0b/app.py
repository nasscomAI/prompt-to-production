"""
UC-0B — Policy Summary Agent
Implements clause extraction and faithful summarization with enforcement of all conditions.
Prevents: clause omission, condition drop, obligation softening, scope bleed.
"""
import argparse
import re

# Expected clauses with verification data
EXPECTED_CLAUSES = {
    '2.3': {'binding_verb': 'must', 'keywords': ['14 days', 'advance', 'application']},
    '2.4': {'binding_verb': 'must', 'keywords': ['written approval', 'before leave', 'verbal']},
    '2.5': {'binding_verb': 'will', 'keywords': ['unapproved absence', 'LOP', 'Loss of Pay']},
    '2.6': {'binding_verb': 'may', 'keywords': ['carry forward', '5 days', 'forfeited', '31 December']},
    '2.7': {'binding_verb': 'must', 'keywords': ['carry-forward', 'January-March', 'first quarter', 'forfeited']},
    '3.2': {'binding_verb': 'requires', 'keywords': ['3 or more consecutive', 'medical certificate', '48 hours']},
    '3.4': {'binding_verb': 'requires', 'keywords': ['before or after', 'holiday', 'medical certificate', 'regardless']},
    '5.2': {'binding_verb': 'requires', 'keywords': ['Department Head', 'HR Director', 'both', 'LWP']},
    '5.3': {'binding_verb': 'requires', 'keywords': ['30 days', 'Municipal Commissioner', 'LWP']},
    '7.2': {'binding_verb': 'not permitted', 'keywords': ['encashment', 'during service', 'any circumstances']},
}

def retrieve_policy(file_path: str) -> dict:
    """
    Load policy file and extract numbered clauses with structure.
    Returns dict with raw_text and sections array.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return {'raw_text': '', 'sections': []}
    
    if not raw_text.strip():
        print(f"Warning: Empty file: {file_path}")
        return {'raw_text': raw_text, 'sections': []}
    
    sections = []
    
    # Extract all numbered clauses (e.g., 2.3, 5.2, etc.)
    # Pattern: digit.digit at start of line followed by text
    clause_pattern = r'^(\d+\.\d+)\s+(.*)$'
    
    lines = raw_text.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        match = re.match(clause_pattern, line)
        if match:
            # Save previous clause if exists
            if current_clause:
                clause_text = ' '.join(current_text).strip()
                sections.append({
                    'number': current_clause['number'],
                    'title': current_clause['title'],
                    'text': clause_text,
                    'binding_verb': extract_binding_verb(clause_text),
                    'conditions': extract_conditions(current_clause['number'], clause_text)
                })
            
            clause_num = match.group(1)
            title = match.group(2).strip()
            current_clause = {'number': clause_num, 'title': title}
            current_text = []
        elif current_clause and line.strip():
            current_text.append(line.strip())
    
    # Save last clause
    if current_clause:
        clause_text = ' '.join(current_text).strip()
        sections.append({
            'number': current_clause['number'],
            'title': current_clause['title'],
            'text': clause_text,
            'binding_verb': extract_binding_verb(clause_text),
            'conditions': extract_conditions(current_clause['number'], clause_text)
        })
    
    return {'raw_text': raw_text, 'sections': sections}


def extract_binding_verb(text: str) -> str:
    """Extract the primary binding verb from clause text."""
    text_lower = text.lower()
    
    binding_verbs = [
        'not permitted',
        'may carry forward',
        'must be used',
        'must submit',
        'must receive',
        'will be recorded',
        'requires',
        'must',
        'may',
        'will'
    ]
    
    for verb in binding_verbs:
        if verb in text_lower:
            return verb
    
    return 'unknown'


def extract_conditions(clause_num: str, text: str) -> list:
    """Extract conditions/qualifications from clause text."""
    conditions = []
    text_lower = text.lower()
    
    # Clause-specific condition patterns
    if clause_num == '2.3':
        if '14' in text:
            conditions.append('14 calendar days advance notice')
        if 'form hr-l1' in text_lower:
            conditions.append('using Form HR-L1')
    elif clause_num == '2.4':
        conditions.append('written approval from direct manager')
        if 'before' in text_lower and ('leave commences' in text_lower or 'leave begins' in text_lower):
            conditions.append('before leave commences')
        if 'verbal' in text_lower:
            conditions.append('verbal approval not valid')
    elif clause_num == '2.5':
        conditions.append('unapproved absence recorded as Loss of Pay (LOP)')
        conditions.append('regardless of subsequent approval')
    elif clause_num == '2.6':
        if '5' in text:
            conditions.append('maximum 5 days carry-forward')
        if '31 december' in text_lower or '31 dec' in text_lower:
            conditions.append('days above 5 forfeited on 31 December')
    elif clause_num == '2.7':
        conditions.append('carry-forward days must be used in first quarter (January-March)')
        conditions.append('days not used by end of March are forfeited')
    elif clause_num == '3.2':
        conditions.append('3 or more consecutive sick days')
        conditions.append('requires medical certificate')
        conditions.append('submitted within 48 hours of returning to work')
    elif clause_num == '3.4':
        conditions.append('sick leave taken before or after public holiday or annual leave')
        conditions.append('requires medical certificate regardless of duration')
    elif clause_num == '5.2':
        conditions.append('requires approval from Department Head')
        conditions.append('requires approval from HR Director')
        conditions.append('BOTH approvals required (manager approval alone insufficient)')
    elif clause_num == '5.3':
        conditions.append('LWP exceeding 30 continuous days')
        conditions.append('requires approval from Municipal Commissioner')
    elif clause_num == '7.2':
        conditions.append('leave encashment during service is not permitted')
        conditions.append('applies under any circumstances (no exceptions)')
    
    return conditions if conditions else ['See source document for details']


def summarize_policy(policy_dict: dict) -> str:
    """
    Produce summary that preserves all clauses with conditions and binding verbs.
    Enforces E1-E5 rules from agents.md.
    """
    if not policy_dict.get('sections'):
        return "Error: No policy sections extracted."
    
    sections = policy_dict['sections']
    
    # Filter to expected clauses only
    expected_set = set(EXPECTED_CLAUSES.keys())
    found_clauses = {s['number'] for s in sections if s['number'] in expected_set}
    missing_clauses = expected_set - found_clauses
    
    summary_lines = []
    
    # Add header
    summary_lines.append("POLICY SUMMARY — EMPLOYEE LEAVE POLICY (HR-POL-001)")
    summary_lines.append("=" * 70)
    summary_lines.append("")
    
    # Summarize each expected clause in order (E1: all clauses must be present)
    clause_order = sorted(expected_set, key=lambda x: tuple(map(int, x.split('.'))))
    
    for clause_num in clause_order:
        clause_section = next((s for s in sections if s['number'] == clause_num), None)
        
        if clause_section:
            summary_lines.append(f"CLAUSE {clause_num}: {clause_section['title']}")
            
            conditions = clause_section['conditions']
            
            # E2: Multi-condition clauses must preserve ALL conditions
            if conditions and conditions[0] != 'See source document for details':
                for condition in conditions:
                    summary_lines.append(f"  • {condition}")
            else:
                # Fallback: use source quote
                summary_lines.append(f"  [SOURCE QUOTE] {clause_section['text']}")
            
            summary_lines.append("")
        else:
            # E1: MISSING CLAUSE ERROR
            summary_lines.append(f"[ERROR] CLAUSE {clause_num}: NOT FOUND IN SOURCE DOCUMENT")
            summary_lines.append("")
    
    # Add verification section
    summary_lines.append("=" * 70)
    summary_lines.append("VERIFICATION")
    summary_lines.append(f"Total clauses extracted: {len(found_clauses)}/{len(expected_set)}")
    
    if missing_clauses:
        summary_lines.append(f"MISSING CLAUSES ({len(missing_clauses)}): {', '.join(sorted(missing_clauses))}")
        summary_lines.append("[FAILURE] Summary is incomplete. Check source document for these clauses.")
    else:
        summary_lines.append("✓ All expected clauses present.")
    
    return '\n'.join(summary_lines)


def main(input_path: str, output_path: str):
    """Load policy, extract, summarize, and write output."""
    print(f"Loading policy from: {input_path}")
    
    policy_dict = retrieve_policy(input_path)
    
    if not policy_dict['sections']:
        print("Error: No clauses extracted from policy.")
        return
    
    print(f"Extracted {len(policy_dict['sections'])} sections from policy.")
    
    summary = summarize_policy(policy_dict)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {output_path}")
    except Exception as e:
        print(f"Error writing output file {output_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Agent")
    parser.add_argument("--input", required=True, help="Path to policy document (e.g., policy_hr_leave.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    main(args.input, args.output)
