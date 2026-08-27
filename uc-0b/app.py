"""
UC-0B app.py — Policy Summarizer with Clause Preservation.

Implements retrieve_policy and summarize_policy skills.
Enforces UC-0B agent rules: all clauses present, no dropped conditions, no scope bleed.
"""
import argparse
import re
import json
import sys
from pathlib import Path


def retrieve_policy(file_path):
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    
    Args:
        file_path (str): Path to policy document
        
    Returns:
        dict: {
            'success': bool,
            'error': str or None,
            'raw_content': str,
            'sections': [
                {
                    'clause_id': str (e.g., '2.3'),
                    'text': str,
                    'binding_verb': str (e.g., 'must', 'requires', 'will')
                },
                ...
            ]
        }
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                'success': False,
                'error': f'FILE_NOT_FOUND: {file_path}',
                'raw_content': None,
                'sections': []
            }
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return {
                'success': False,
                'error': 'FILE_EMPTY: Document contains no content',
                'raw_content': content,
                'sections': []
            }
        
        # Extract numbered clauses (e.g., "2.3", "3.2", "5.2")
        # Pattern: clause number followed by text until next clause
        lines = content.split('\n')
        sections = []
        current_clause = None
        current_text = []
        binding_verbs = ['must', 'will', 'may', 'requires', 'not permitted', 'are forfeited']
        
        for line in lines:
            # Check if line starts with a clause number
            clause_match = re.match(r'^(\d+\.\d+)\s+(.+)', line)
            if clause_match:
                # Save previous clause if exists
                if current_clause:
                    text = '\n'.join(current_text).strip()
                    binding_verb = None
                    for verb in binding_verbs:
                        if verb.lower() in text.lower():
                            binding_verb = verb
                            break
                    sections.append({
                        'clause_id': current_clause,
                        'text': text,
                        'binding_verb': binding_verb
                    })
                
                # Start new clause
                current_clause = clause_match.group(1)
                current_text = [clause_match.group(2)]
            elif current_clause and line.strip():
                # Continuation of current clause
                current_text.append(line.strip())
        
        # Don't forget the last clause
        if current_clause:
            text = '\n'.join(current_text).strip()
            binding_verb = None
            for verb in binding_verbs:
                if verb.lower() in text.lower():
                    binding_verb = verb
                    break
            sections.append({
                'clause_id': current_clause,
                'text': text,
                'binding_verb': binding_verb
            })
        
        if not sections:
            return {
                'success': False,
                'error': 'NO_CLAUSES_FOUND: Document does not contain expected numbered clause structure',
                'raw_content': content,
                'sections': []
            }
        
        return {
            'success': True,
            'error': None,
            'raw_content': content,
            'sections': sections
        }
    
    except IOError as e:
        return {
            'success': False,
            'error': f'FILE_UNREADABLE: {str(e)}',
            'raw_content': None,
            'sections': []
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'UNKNOWN_ERROR: {str(e)}',
            'raw_content': None,
            'sections': []
        }


def summarize_policy(sections, enforcement_mode='strict'):
    """
    Takes structured policy sections and produces a compliant summary.
    
    Args:
        sections (list): List of clause objects from retrieve_policy
        enforcement_mode (str): 'strict' (fail on missing/dropped conditions) or 'permissive'
        
    Returns:
        dict: {
            'success': bool,
            'error': str or None,
            'summary': str,
            'clause_count': int,
            'missing_clauses': [list of expected clause_ids],
            'flagged_clauses': [list of {clause_id, reason, verbatim_quote}],
            'warnings': [list of detected issues]
        }
    """
    if not sections:
        return {
            'success': False,
            'error': 'NO_CLAUSES_PROVIDED: Input sections array is empty',
            'summary': None,
            'clause_count': 0,
            'missing_clauses': [],
            'flagged_clauses': [],
            'warnings': []
        }
    
    # Expected clauses from README.md clause inventory
    expected_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    found_clauses = [s['clause_id'] for s in sections]
    missing_clauses = [c for c in expected_clauses if c not in found_clauses]
    
    warnings = []
    flagged_clauses = []
    
    # Multi-condition clauses that must preserve all conditions
    multi_condition_clauses = {
        '5.2': ['Department Head', 'HR Director'],  # Must have BOTH approvers
        '3.4': ['medical certificate', 'regardless of duration']  # Must have both requirements
    }
    
    # Build summary
    summary_lines = []
    summary_lines.append("# Policy Summary: HR Leave\n")
    summary_lines.append(f"Total clauses found: {len(sections)}\n")
    
    for section in sections:
        clause_id = section['clause_id']
        text = section['text']
        binding_verb = section['binding_verb']
        
        # Normalize whitespace for condition checking (collapse newlines)
        normalized_text = ' '.join(text.split())
        
        # Check for multi-condition preservation
        if clause_id in multi_condition_clauses:
            required_conditions = multi_condition_clauses[clause_id]
            missing_conditions = []
            for condition in required_conditions:
                if condition.lower() not in normalized_text.lower():
                    missing_conditions.append(condition)
            
            if missing_conditions:
                warnings.append(
                    f"CONDITION_DROP: Clause {clause_id} missing: {', '.join(missing_conditions)}"
                )
                flagged_clauses.append({
                    'clause_id': clause_id,
                    'reason': f'Missing conditions: {", ".join(missing_conditions)}',
                    'verbatim_quote': text[:100] + '...' if len(text) > 100 else text
                })
        
        # Check for scope bleed (phrases not in source)
        scope_bleed_phrases = ['as is standard practice', 'typically', 'generally expected', 'usually']
        for phrase in scope_bleed_phrases:
            if phrase.lower() in text.lower():
                warnings.append(f"SCOPE_BLEED: Clause {clause_id} contains: '{phrase}'")
        
        summary_lines.append(f"\n## Clause {clause_id}")
        if binding_verb:
            summary_lines.append(f"**Binding verb:** {binding_verb}")
        summary_lines.append(f"\n{text}\n")
    
    # Determine success status
    success = len(missing_clauses) == 0 and len(warnings) == 0
    
    if enforcement_mode == 'strict' and not success:
        return {
            'success': False,
            'error': f'ENFORCEMENT_FAILED: {len(missing_clauses)} missing clauses, {len(warnings)} warnings',
            'summary': '\n'.join(summary_lines),
            'clause_count': len(sections),
            'missing_clauses': missing_clauses,
            'flagged_clauses': flagged_clauses,
            'warnings': warnings
        }
    
    return {
        'success': True,
        'error': None,
        'summary': '\n'.join(summary_lines),
        'clause_count': len(sections),
        'missing_clauses': missing_clauses,
        'flagged_clauses': flagged_clauses,
        'warnings': warnings
    }


def main():
    parser = argparse.ArgumentParser(
        description='UC-0B Policy Summarizer: Produces compliant summaries with all clauses and conditions preserved.'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input policy document (.txt)'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path to output summary file'
    )
    parser.add_argument(
        '--mode',
        type=str,
        default='strict',
        choices=['strict', 'permissive'],
        help='Enforcement mode: strict (fail on issues) or permissive (log warnings)'
    )
    
    args = parser.parse_args()
    
    # Step 1: Retrieve and structure policy
    print(f"[1/2] Retrieving policy from {args.input}...", file=sys.stderr)
    retrieve_result = retrieve_policy(args.input)
    
    if not retrieve_result['success']:
        print(f"ERROR: {retrieve_result['error']}", file=sys.stderr)
        sys.exit(1)
    
    print(f"SUCCESS: Retrieved {len(retrieve_result['sections'])} clauses", file=sys.stderr)
    
    # Step 2: Summarize with preservation rules
    print(f"[2/2] Summarizing policy with enforcement mode: {args.mode}...", file=sys.stderr)
    summary_result = summarize_policy(retrieve_result['sections'], enforcement_mode=args.mode)
    
    if not summary_result['success'] and args.mode == 'strict':
        print(f"ERROR: {summary_result['error']}", file=sys.stderr)
        if summary_result['missing_clauses']:
            print(f"Missing clauses: {', '.join(summary_result['missing_clauses'])}", file=sys.stderr)
        if summary_result['warnings']:
            print("Warnings:", file=sys.stderr)
            for warning in summary_result['warnings']:
                print(f"  - {warning}", file=sys.stderr)
        sys.exit(1)
    
    # Write output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_result['summary'])
        print(f"SUCCESS: Summary written to {args.output}", file=sys.stderr)
        
        # Log warnings even on success (permissive mode)
        if summary_result['warnings']:
            print(f"\nWARNINGS ({len(summary_result['warnings'])}):", file=sys.stderr)
            for warning in summary_result['warnings']:
                print(f"  - {warning}", file=sys.stderr)
        
        if summary_result['missing_clauses']:
            print(f"\nMissing clauses: {', '.join(summary_result['missing_clauses'])}", file=sys.stderr)
    
    except IOError as e:
        print(f"ERROR: Could not write output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
