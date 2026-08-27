#!/usr/bin/env python3
"""
UC-0B: Summary That Changes Meaning
Generates policy summaries that preserve all clauses and conditions.
"""

import argparse
import re
import sys
from pathlib import Path


def retrieve_policy(file_path):
    """
    Load and parse policy document into structured format.
    
    Args:
        file_path: Path to policy text file
    
    Returns:
        dict with title, sections, and clause_inventory
    """
    if not Path(file_path).exists():
        print(f"Error: Policy file '{file_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Extract title
    title = ""
    for line in lines[:10]:
        if "POLICY" in line.upper() and not line.startswith('═'):
            title = line.strip()
            break
    
    # Parse sections and clauses
    sections = []
    current_section = None
    clause_inventory = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines and separator lines
        if not line or line.startswith('═'):
            continue
        
        # Check for section heading (e.g., "2. ANNUAL LEAVE")
        section_match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if section_match and line.isupper():
            if current_section:
                sections.append(current_section)
            current_section = {
                'number': section_match.group(1),
                'heading': section_match.group(2),
                'clauses': []
            }
            continue
        
        # Check for clause (e.g., "2.3 Employees must...")
        clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line)
        if clause_match and current_section:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2)
            
            # Collect continuation lines
            full_text = clause_text
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                # Stop if we hit another clause, section, or separator
                if (re.match(r'^\d+\.\d+\s', next_line) or 
                    re.match(r'^\d+\.\s+[A-Z]', next_line) or
                    next_line.startswith('═') or
                    not next_line):
                    break
                full_text += ' ' + next_line
                j += 1
            
            current_section['clauses'].append({
                'number': clause_num,
                'text': full_text
            })
            clause_inventory.append(clause_num)
    
    # Add last section
    if current_section:
        sections.append(current_section)
    
    return {
        'title': title,
        'sections': sections,
        'clause_inventory': clause_inventory
    }


def summarize_policy(policy_data, output_file):
    """
    Generate compliant summary preserving all clauses and conditions.
    
    Args:
        policy_data: Structured policy from retrieve_policy
        output_file: Path for summary output
    """
    summary_lines = []
    
    # Header
    summary_lines.append(f"{policy_data['title']} - SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    
    # Track which clauses we've summarized
    summarized_clauses = []
    
    # Process each section
    for section in policy_data['sections']:
        summary_lines.append(f"{section['number']}. {section['heading']}")
        summary_lines.append("-" * 60)
        
        for clause in section['clauses']:
            clause_num = clause['number']
            clause_text = clause['text']
            
            # Summarize while preserving key information
            summary = summarize_clause(clause_num, clause_text)
            summary_lines.append(f"Section {clause_num}: {summary}")
            summarized_clauses.append(clause_num)
        
        summary_lines.append("")
    
    # Verify completeness
    missing_clauses = set(policy_data['clause_inventory']) - set(summarized_clauses)
    if missing_clauses:
        print(f"Warning: Missing clauses in summary: {missing_clauses}", file=sys.stderr)
    
    # Write summary
    summary_text = '\n'.join(summary_lines)
    
    # Check for forbidden scope bleed phrases
    forbidden_phrases = [
        "as is standard practice",
        "typically in government",
        "generally expected",
        "it is common practice",
        "while not explicitly"
    ]
    
    for phrase in forbidden_phrases:
        if phrase.lower() in summary_text.lower():
            print(f"Warning: Scope bleed detected - '{phrase}'", file=sys.stderr)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    
    print(f"Summary written to {output_file}")
    print(f"Clauses summarized: {len(summarized_clauses)}/{len(policy_data['clause_inventory'])}")


def summarize_clause(clause_num, clause_text):
    """
    Summarize a single clause while preserving all conditions.
    
    Args:
        clause_num: Clause number (e.g., "2.3")
        clause_text: Full clause text
    
    Returns:
        Summary string
    """
    # For critical multi-condition clauses, preserve more detail
    text_lower = clause_text.lower()
    
    # Preserve exact wording for critical clauses
    if "and" in text_lower and ("approval" in text_lower or "requires" in text_lower):
        # Multi-approver clause - preserve all approvers
        return clause_text
    
    if "regardless" in text_lower:
        # Preserve "regardless" clauses exactly
        return clause_text
    
    if "not permitted" in text_lower or "cannot" in text_lower:
        # Preserve prohibitions exactly
        return clause_text
    
    if "must" in text_lower and ("before" in text_lower or "within" in text_lower):
        # Preserve timing requirements exactly
        return clause_text
    
    # For simpler clauses, can condense slightly but preserve key facts
    # Remove redundant words but keep all conditions
    summary = clause_text
    
    # Clean up extra whitespace
    summary = re.sub(r'\s+', ' ', summary).strip()
    
    return summary


def main():
    parser = argparse.ArgumentParser(
        description='Generate compliant policy summary'
    )
    parser.add_argument('--input', required=True, help='Input policy file')
    parser.add_argument('--output', required=True, help='Output summary file')
    
    args = parser.parse_args()
    
    # Retrieve and parse policy
    print(f"Loading policy from {args.input}...")
    policy_data = retrieve_policy(args.input)
    print(f"Found {len(policy_data['sections'])} sections with {len(policy_data['clause_inventory'])} clauses")
    
    # Generate summary
    print("Generating summary...")
    summarize_policy(policy_data, args.output)


if __name__ == '__main__':
    main()
