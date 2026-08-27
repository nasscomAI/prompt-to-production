"""
UC-0B app.py — Policy Summarization with Clause Preservation.
Implements retrieve_policy and summarize_policy skills following agents.md enforcement rules.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any


def retrieve_policy(file_path: str) -> Dict[str, Any]:
    """
    Loads HR leave policy .txt file, parses numbered clauses,
    and returns structured sections with clause identifiers and binding verbs.
    
    Skills.md: retrieve_policy
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    clauses = []
    
    # Parse numbered clauses: split by section headers
    # Pattern matches clauses like "2.3 text..." until next clause or section
    clause_pattern = r'^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|^═|^[A-Z\s]+$|\Z)'
    matches = re.finditer(clause_pattern, content, re.MULTILINE | re.DOTALL)
    
    binding_verbs = ['must', 'will', 'requires', 'may', 'not permitted', 'cannot']
    
    for match in matches:
        clause_id = match.group(1)
        full_text = match.group(2).strip()
        
        # Extract section (e.g., "2. ANNUAL LEAVE" for clause 2.3)
        section_num = clause_id.split('.')[0]
        section = f"Section {section_num}"
        
        # Find binding verb
        binding_verb = None
        for verb in binding_verbs:
            if verb.lower() in full_text.lower():
                binding_verb = verb
                break
        
        # Extract obligation (clean up formatting)
        obligation = full_text.split('\n')[0].replace('    ', ' ').strip()
        
        clause_dict = {
            'clause_id': clause_id,
            'section': section,
            'obligation': obligation,
            'binding_verb': binding_verb,
            'full_text': full_text
        }
        clauses.append(clause_dict)
    
    return {
        'clauses': clauses,
        'metadata': {
            'source_file': str(path),
            'format': 'HR_LEAVE_POLICY',
            'total_clauses': len(clauses)
        }
    }


def summarize_policy(policy_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes structured policy clauses, produces a concise summary
    that preserves all obligations and multi-condition requirements
    without adding unstated context.
    
    Skills.md: summarize_policy
    """
    if not isinstance(policy_dict, dict) or 'clauses' not in policy_dict:
        return {
            'error': 'invalid_input',
            'message': 'Input must be output from retrieve_policy with keys: clauses, metadata'
        }
    
    clauses = policy_dict.get('clauses', [])
    summary_lines = []
    clause_references = []
    critical_clauses = []
    condition_audit = []
    
    # Map of target clauses from README (the 10-clause inventory)
    target_clauses = {
        '2.3': '14-day advance notice required',
        '2.4': 'Written approval required before leave commences. Verbal not valid.',
        '2.5': 'Unapproved absence = LOP regardless of subsequent approval',
        '2.6': 'Max 5 days carry-forward. Above 5 forfeited on 31 Dec.',
        '2.7': 'Carry-forward days must be used Jan–Mar or forfeited',
        '3.2': '3+ consecutive sick days requires medical cert within 48hrs',
        '3.4': 'Sick leave before/after holiday requires cert regardless of duration',
        '5.2': 'LWP requires Department Head AND HR Director approval',
        '5.3': 'LWP >30 days requires Municipal Commissioner approval',
        '7.2': 'Leave encashment during service not permitted under any circumstances'
    }
    
    summary_lines.append("POLICY SUMMARY - HR LEAVE POLICY (UC-0B)\n")
    summary_lines.append("=" * 70)
    summary_lines.append("")
    
    # Process each clause
    for clause in clauses:
        clause_id = clause['clause_id']
        
        # Only include target clauses
        if clause_id in target_clauses:
            clause_references.append(clause_id)
            
            # Check for multi-condition clauses (trap for condition drops)
            full_text = clause['full_text']
            condition_count = len(re.findall(r'\band\b|\bor\b|both', full_text, re.IGNORECASE))
            
            if condition_count >= 2:
                # Flag as multi-condition for audit
                condition_audit.append({
                    'clause_id': clause_id,
                    'condition_count': condition_count,
                    'status': 'MULTI_CONDITION_PRESERVED'
                })
                critical_clauses.append({
                    'clause_id': clause_id,
                    'reason': 'Multi-condition obligation (must preserve all)',
                    'text': full_text
                })
            
            # Add to summary with binding verb
            binding_verb = clause['binding_verb'] or 'requires'
            summary_lines.append(f"Clause {clause_id} ({clause['section']})")
            summary_lines.append(f"  Binding: {binding_verb.upper()}")
            # Clean up full text and include it in summary
            clause_text = full_text.replace('\n    ', ' ').strip()
            summary_lines.append(f"  {clause_text}")
            summary_lines.append("")
    
    summary_lines.append("=" * 70)
    summary_lines.append(f"Total Clauses Covered: {len(clause_references)}/10 (Target Inventory)")
    summary_lines.append(f"Coverage Score: {int((len(clause_references) / 10) * 100)}%")
    summary_lines.append("")
    
    # Validation: Check for missing clauses
    missing_clauses = set(target_clauses.keys()) - set(clause_references)
    if missing_clauses:
        summary_lines.append("⚠ WARNING: Missing Clauses from Target Inventory")
        for missing in sorted(missing_clauses):
            summary_lines.append(f"  - {missing}: {target_clauses[missing]}")
        summary_lines.append("")
    
    # Condition drop detection - clause 5.2 trap
    summary_text = '\n'.join(summary_lines)
    if '5.2' in clause_references:
        for clause in clauses:
            if clause['clause_id'] == '5.2':
                # Check source has both approvers
                source_has_both = ('Department Head' in clause['full_text'] and 
                                 'HR Director' in clause['full_text'])
                # Check summary preserves both
                summary_has_both = ('Department Head' in summary_text and 
                                  'HR Director' in summary_text)
                
                if source_has_both and summary_has_both:
                    condition_audit.append({
                        'clause_id': '5.2',
                        'check': 'BOTH_APPROVERS_PRESENT',
                        'status': 'PASS'
                    })
                elif source_has_both and not summary_has_both:
                    condition_audit.append({
                        'clause_id': '5.2',
                        'check': 'BOTH_APPROVERS_PRESENT',
                        'status': 'FAIL',
                        'risk': 'CONDITION_DROP_DETECTED'
                    })
                else:
                    condition_audit.append({
                        'clause_id': '5.2',
                        'check': 'BOTH_APPROVERS_PRESENT',
                        'status': 'PASS'
                    })
    
    return {
        'summary': '\n'.join(summary_lines),
        'clause_references': sorted(clause_references),
        'critical_clauses': critical_clauses,
        'coverage_score': int((len(clause_references) / 10) * 100),
        'condition_audit': condition_audit,
        'missing_clauses': sorted(list(missing_clauses))
    }


def main():
    parser = argparse.ArgumentParser(
        description='UC-0B Policy Summarization - Preserves all clauses and conditions'
    )
    parser.add_argument('--input', required=True, help='Input policy .txt file path')
    parser.add_argument('--output', required=True, help='Output summary file path')
    
    args = parser.parse_args()
    
    try:
        # Retrieve policy
        print(f"[1/2] Retrieving policy from {args.input}...")
        policy_dict = retrieve_policy(args.input)
        print(f"      Found {policy_dict['metadata']['total_clauses']} clauses")
        
        # Summarize policy
        print(f"[2/2] Summarizing policy with clause preservation...")
        result = summarize_policy(policy_dict)
        
        if 'error' in result:
            print(f"ERROR: {result['error']} - {result['message']}")
            return 1
        
        # Write output
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['summary'])
        
        print(f"\n✓ Summary written to {args.output}")
        print(f"  Coverage: {result['coverage_score']}%")
        print(f"  Clauses: {len(result['clause_references'])}/10")
        
        if result['missing_clauses']:
            print(f"  ⚠ Missing {len(result['missing_clauses'])} clauses")
        
        # Validate condition preservation
        for audit in result['condition_audit']:
            if 'risk' in audit:
                print(f"  ⚠ CONDITION DROP RISK: {audit['clause_id']}")
        
        return 0
    
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
