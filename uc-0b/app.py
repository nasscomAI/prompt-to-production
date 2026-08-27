"""
UC-0B app.py — Policy Summarizer
Reads HR leave policy and produces compliant summary preserving all critical clauses.
Failure modes: Clause omission, Scope bleed, Obligation softening.
"""
import argparse
import re
import os


def retrieve_policy(input_path):
    """
    Load and parse policy file into structured clauses.
    Returns: dict with clause numbers as keys (e.g., '2.3', '5.2')
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse numbered clauses (e.g., 2.3, 3.4, 5.2)
    clauses = {}
    
    # Split by section headers (all caps with ═══)
    sections = re.split(r'═+\n', content)
    
    current_section = None
    for section in sections:
        lines = section.strip().split('\n')
        
        for i, line in enumerate(lines):
            # Match clause numbers like "2.3" at start of line
            match = re.match(r'^(\d+\.\d+)\s+(.+)', line)
            if match:
                clause_num = match.group(1)
                clause_text = match.group(2)
                
                # Collect full clause text (may span multiple lines)
                full_text = clause_text
                j = i + 1
                while j < len(lines) and not re.match(r'^\d+\.\d+\s+', lines[j]):
                    full_text += ' ' + lines[j].strip()
                    j += 1
                
                clauses[clause_num] = {
                    'text': full_text.strip(),
                    'raw': section
                }
    
    return clauses


def extract_binding_verb(clause_text):
    """Extract binding verb from clause for enforcement tracking."""
    verbs = ['must', 'requires', 'will', 'may', 'are forfeited', 'not permitted', 'can', 'entitled']
    text_lower = clause_text.lower()
    
    for verb in verbs:
        if verb in text_lower:
            return verb
    
    return 'UNCLEAR'


def has_scope_bleed(text):
    """Detect scope bleed phrases not in source document."""
    scope_bleed_phrases = [
        'typically',
        'generally',
        'as is standard practice',
        'as is customary',
        'employees are usually',
        'employees are generally',
        'it is common practice',
        'in most organizations',
        'standard practice'
    ]
    
    text_lower = text.lower()
    for phrase in scope_bleed_phrases:
        if phrase in text_lower:
            return True, phrase
    
    return False, None


def summarize_policy(clauses):
    """
    Produce summary preserving all critical clauses and multi-conditions.
    Focus on the 10 critical clauses identified in README.
    """
    # Critical clauses from README that MUST be in summary
    critical_clauses = {
        '2.3': '14-day advance notice required',
        '2.4': 'Written approval required before leave starts (verbal not valid)',
        '2.5': 'Unapproved absence recorded as LOP regardless of subsequent approval',
        '2.6': 'Max 5 days carry-forward; days above 5 forfeited on 31 Dec',
        '2.7': 'Carry-forward days must be used Jan-Mar or forfeited',
        '3.2': '3+ consecutive sick days requires medical cert within 48 hours',
        '3.4': 'Sick leave before/after holiday requires cert regardless of duration',
        '5.2': 'LWP requires approval from BOTH Department Head AND HR Director (not just manager approval)',
        '5.3': 'LWP exceeding 30 days requires Municipal Commissioner approval',
        '7.2': 'Leave encashment during service not permitted under any circumstances'
    }
    
    summary_lines = []
    summary_lines.append("POLICY SUMMARY: HUMAN RESOURCES EMPLOYEE LEAVE POLICY")
    summary_lines.append("=" * 80)
    summary_lines.append("")
    summary_lines.append("CRITICAL OBLIGATIONS AND ENTITLEMENTS:")
    summary_lines.append("")
    
    violations = []
    missing_clauses = []
    
    # Process critical clauses
    for clause_num, expected_desc in critical_clauses.items():
        if clause_num in clauses:
            clause_text = clauses[clause_num]['text']
            verb = extract_binding_verb(clause_text)
            
            # Check for scope bleed
            has_bleed, phrase = has_scope_bleed(clause_text)
            if has_bleed:
                violations.append(f"Scope bleed in {clause_num}: phrase '{phrase}'")
            
            # Preserve multi-conditions especially for clause 5.2
            if clause_num == '5.2':
                # This is the trap clause - must preserve BOTH approvers
                if 'Department Head' in clause_text and 'HR Director' in clause_text:
                    summary_lines.append(f"Clause {clause_num}: {clause_text}")
                else:
                    violations.append(f"CRITICAL: {clause_num} missing multi-condition approvers")
                    summary_lines.append(f"Clause {clause_num} [CONDITION LOSS]: {clause_text}")
            else:
                # Regular clause - preserve as-is
                summary_lines.append(f"Clause {clause_num}: {clause_text}")
            
            summary_lines.append(f"  [Binding verb: {verb}]")
            summary_lines.append("")
        else:
            missing_clauses.append(clause_num)
            summary_lines.append(f"Clause {clause_num}: *** MISSING FROM POLICY ***")
            summary_lines.append("")
    
    # Add other sections for context
    summary_lines.append("=" * 80)
    summary_lines.append("OTHER PROVISIONS:")
    summary_lines.append("")
    
    # Organize remaining clauses by section
    other_clauses_by_section = {}
    for clause_num, clause_data in clauses.items():
        if clause_num not in critical_clauses:
            section = clause_num.split('.')[0]
            if section not in other_clauses_by_section:
                other_clauses_by_section[section] = []
            other_clauses_by_section[section].append((clause_num, clause_data['text']))
    
    for section in sorted(other_clauses_by_section.keys()):
        for clause_num, text in other_clauses_by_section[section]:
            has_bleed, _ = has_scope_bleed(text)
            bleed_flag = "[SCOPE BLEED]" if has_bleed else ""
            summary_lines.append(f"Clause {clause_num}: {text} {bleed_flag}")
            summary_lines.append("")
    
    summary_text = "\n".join(summary_lines)
    
    # Add enforcement report
    summary_text += "\n" + "=" * 80 + "\n"
    summary_text += "ENFORCEMENT CHECK:\n"
    summary_text += "=" * 80 + "\n"
    
    if missing_clauses:
        summary_text += f"❌ MISSING CLAUSES: {', '.join(missing_clauses)}\n"
    else:
        summary_text += "✓ All critical clauses present\n"
    
    if violations:
        summary_text += f"❌ VIOLATIONS:\n"
        for v in violations:
            summary_text += f"  - {v}\n"
    else:
        summary_text += "✓ No violations detected\n"
    
    summary_text += f"\n✓ Total clauses summarized: {len(clauses)}\n"
    
    return summary_text


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()
    
    # Retrieve and parse policy
    clauses = retrieve_policy(args.input)
    
    # Summarize
    summary = summarize_policy(clauses)
    
    # Write output
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary written to {args.output}")
    print(f"Total clauses processed: {len(clauses)}")


if __name__ == "__main__":
    main()
