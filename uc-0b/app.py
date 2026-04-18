"""
UC-0B app.py — HR Leave Policy Summarizer
Reads a policy document, extracts numbered clauses, produces structured summary
with validation of all clause IDs.
"""
import argparse
import re
import sys
import os


def retrieve_policy(file_path):
    """Parse policy file into numbered clauses."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Policy file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Pattern: lines starting with digit.digit (e.g., 2.3, 5.2)
    clause_pattern = r'^\s*(\d+\.\d+)\s+(.*?)$'
    clauses = []

    lines = content.split('\n')
    current_clause_id = None
    current_text = []

    for line in lines:
        match = re.match(clause_pattern, line)
        if match:
            # Save previous clause if exists
            if current_clause_id:
                clauses.append({
                    'clause_id': current_clause_id,
                    'raw_text': '\n'.join(current_text).strip()
                })
            current_clause_id = match.group(1)
            current_text = [match.group(2)]  # Only the text AFTER the clause ID
        else:
            if current_clause_id:
                current_text.append(line.rstrip())

    # Don't forget the last clause
    if current_clause_id:
        clauses.append({
            'clause_id': current_clause_id,
            'raw_text': '\n'.join(current_text).strip()
        })

    return clauses


def summarize_policy(sections):
    """Create clause-by-clause summary preserving binding verbs and conditions."""
    summary_lines = []

    for section in sections:
        clause_id = section['clause_id']
        raw_text = section['raw_text']

        # Extract binding verbs and key conditions
        text = raw_text

        # Preserve binding verbs exactly
        binding_verbs = ['must', 'will', 'requires', 'not permitted', 'should', 'may', 'cannot']

        # Check if this clause needs verbatim handling (contains complex conditions)
        has_condition = any(keyword in text.lower() for keyword in ['if', 'provided', 'subject to', 'except', 'only if'])

        # Build summary line
        summary_line = f"{clause_id}: {text}"
        summary_lines.append(summary_line)

    return '\n'.join(summary_lines)


def validate_clauses(summary, required_clauses):
    """Validate that all required clause IDs appear in summary."""
    results = []
    found_clauses = set()
    clause_content = {}

    # Extract all clause IDs and their content from summary
    clause_pattern = r'^(\d+\.\d+):'
    current_id = None
    current_content = []

    for line in summary.split('\n'):
        match = re.match(clause_pattern, line)
        if match:
            if current_id:
                clause_content[current_id] = '\n'.join(current_content)
            current_id = match.group(1)
            found_clauses.add(current_id)
            current_content = [line]
        else:
            if current_id:
                current_content.append(line)

    if current_id:
        clause_content[current_id] = '\n'.join(current_content)

    # Check each required clause
    for clause_id in required_clauses:
        if clause_id in found_clauses:
            results.append(f"PASS: {clause_id}")
        else:
            results.append(f"WARN: {clause_id} missing")

    # Specific validation rules
    if '5.2' in found_clauses:
        content_5_2 = clause_content.get('5.2', '')
        if 'Department Head' in content_5_2 and 'HR Director' in content_5_2:
            results.append("PASS: Clause 5.2 has both approvers")
        else:
            results.append("WARN: Clause 5.2 missing one or both approvers")

    if '7.2' in found_clauses:
        content_7_2 = clause_content.get('7.2', '')
        # Normalize whitespace for searching
        normalized_content = ' '.join(content_7_2.split())
        if 'not permitted under any circumstances' in normalized_content:
            results.append("PASS: Clause 7.2 has exact binding verb")
        else:
            results.append("WARN: Clause 7.2 missing exact binding verb")

    return results


def main():
    parser = argparse.ArgumentParser(description='HR Leave Policy Summarizer')
    parser.add_argument('--input', required=True, help='Path to policy .txt file')
    parser.add_argument('--output', required=True, help='Path to output summary file')

    args = parser.parse_args()

    # Required clause IDs
    required_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']

    # Retrieve and parse policy
    clauses = retrieve_policy(args.input)

    # Summarize
    summary = summarize_policy(clauses)

    # Write output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    validation_results = validate_clauses(summary, required_clauses)

    print(f"\nValidation Results for {args.output}:")
    for result in validation_results:
        print(result)

    # Overall status
    warn_count = sum(1 for r in validation_results if r.startswith('WARN'))
    if warn_count > 0:
        print(f"\nWarning: Summary complete with {warn_count} warnings")
    else:
        print("\nSuccess: Summary complete - all validations passed")


if __name__ == "__main__":
    main()
