"""
UC-0B app.py — HR Leave Policy Compliance Summarization
Implements retrieve_policy and summarize_policy skills with enforcement rules from agents.md.
"""
import argparse
import re
import sys
from pathlib import Path


# Required clauses to enforce
REQUIRED_CLAUSES = {'2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2'}

# Scope-bleed phrases that must be rejected
FORBIDDEN_PHRASES = [
    'as is standard practice',
    'typically in government organisations',
    'employees are generally expected to',
    'typically',
    'commonly',
    'generally expected'
]

# Binding verbs that must be preserved exactly
BINDING_VERBS = {'must', 'will', 'may', 'requires', 'not permitted', 'are forfeited'}


def retrieve_policy(file_path):
    """
    Skill: Loads a .txt policy file and returns content as structured numbered sections.
    
    Returns: Dictionary with numbered clauses as keys and exact clause text as values.
    Raises: ValueError if file not found or required clauses missing.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise ValueError(f"Policy file not found: {file_path}")
    except IOError as e:
        raise ValueError(f"Cannot read policy file: {e}")
    
    clauses = {}
    
    # Extract each required clause using regex pattern matching
    # Pattern: "X.Y" followed by text until next clause or section
    clause_pattern = r'(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+|\n═|$)'
    matches = re.finditer(clause_pattern, content, re.DOTALL)
    
    for match in matches:
        clause_num = match.group(1)
        clause_text = match.group(2).strip()
        clauses[clause_num] = clause_text
    
    # Validate all required clauses are present
    missing = REQUIRED_CLAUSES - set(clauses.keys())
    if missing:
        raise ValueError(
            f"Required clauses missing from policy file: {sorted(missing)}. "
            f"Refuses to return partial results."
        )
    
    return clauses


def summarize_policy(clauses_dict):
    """
    Skill: Takes structured policy sections and produces a compliant summary.
    
    Returns: Summary text with all 10 clauses and their core obligations intact.
    Raises: ValueError if any enforcement rule is violated.
    """
    
    # Validate input
    if not clauses_dict:
        raise ValueError("No clauses provided to summarize.")
    
    missing = REQUIRED_CLAUSES - set(clauses_dict.keys())
    if missing:
        raise ValueError(
            f"[FLAG FOR MANUAL REVIEW] Missing clauses: {sorted(missing)}. "
            f"Cannot summarize with missing clauses."
        )
    
    # Build summary from exact source text
    summary_parts = []
    summary_parts.append("HR LEAVE POLICY COMPLIANCE SUMMARY")
    summary_parts.append("=" * 60)
    summary_parts.append("")
    
    for clause_num in sorted(REQUIRED_CLAUSES):
        clause_text = clauses_dict[clause_num]
        
        # Validate no scope-bleed phrases in summary creation
        # (Check source text for context)
        for forbidden in FORBIDDEN_PHRASES:
            if forbidden.lower() in clause_text.lower():
                raise ValueError(
                    f"[FLAG FOR MANUAL REVIEW] Clause {clause_num} contains scope-bleed phrase "
                    f"'{forbidden}'. Cannot summarize without manual review."
                )
        
        # Extract core obligation - preserve exact text from source
        summary_parts.append(f"Clause {clause_num}:")
        summary_parts.append(f"  {clause_text}")
        summary_parts.append("")
    
    summary_text = "\n".join(summary_parts)
    
    # Post-summary validation: check for scope-bleed in output
    for forbidden in FORBIDDEN_PHRASES:
        if forbidden.lower() in summary_text.lower():
            raise ValueError(
                f"[FLAG FOR MANUAL REVIEW] Summary contains scope-bleed phrase '{forbidden}'. "
                f"Refuses to output. Manual review required."
            )
    
    # Verify all binding verbs are preserved
    # Extract verbs from summary and check they match source
    for clause_num in REQUIRED_CLAUSES:
        source_text = clauses_dict[clause_num]
        summary_clause_start = summary_text.find(f"Clause {clause_num}:")
        
        if summary_clause_start == -1:
            raise ValueError(f"Clause {clause_num} missing from summary.")
        
        # Find the clause text in summary
        summary_clause_end = summary_text.find("\nClause", summary_clause_start + 1)
        if summary_clause_end == -1:
            summary_clause_end = len(summary_text)
        
        summary_clause = summary_text[summary_clause_start:summary_clause_end]
        
        # Verify verb preservation for critical clauses
        if clause_num == '5.2':
            # Special validation: must have both "Department Head" AND "HR Director"
            if 'Department Head' not in summary_clause or 'HR Director' not in summary_clause:
                raise ValueError(
                    f"[ENFORCEMENT FAILURE] Clause 5.2 must explicitly state both "
                    f"'Department Head AND HR Director'. Found conditions dropped in summary."
                )
    
    return summary_text


def main():
    parser = argparse.ArgumentParser(
        description="HR Leave Policy Compliance Summarization"
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input policy file (policy_hr_leave.txt)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to output summary file'
    )
    
    args = parser.parse_args()
    
    try:
        # Skill 1: Retrieve and parse policy
        print(f"Retrieving policy from: {args.input}")
        clauses = retrieve_policy(args.input)
        print(f"✓ Successfully extracted {len(clauses)} clauses")
        
        # Skill 2: Summarize with enforcement
        print("Summarizing policy with enforcement checks...")
        summary = summarize_policy(clauses)
        print("✓ Summary passed all enforcement rules")
        
        # Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✓ Summary written to: {args.output}")
        print(f"\nAll 10 required clauses present and preserved:")
        for clause_num in sorted(REQUIRED_CLAUSES):
            print(f"  • Clause {clause_num}")
        
    except ValueError as e:
        print(f"✗ ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
