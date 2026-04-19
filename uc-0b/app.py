#!/usr/bin/env python3
"""
UC-0B HR Policy Summarizer
Parse CMC Employee Leave Policy into structured Markdown summary.
"""

import argparse
import re
import sys

def retrieve_policy(input_path):
    """
    Skill: Load policy file.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {input_path}")
    except Exception:
        return ''

def preprocess_policy(raw_text):
    """
    Replace separator lines (═+) with newline, keep structure.
    """
    lines = raw_text.splitlines(keepends=True)
    processed = []
    for line in lines:
        if re.match(r'^═+$', line.strip()):
            processed.append('\n')
        else:
            processed.append(line)
    return processed

def extract_clauses(lines):
    """
    Line-by-line clause extraction. Group by section prefix.
    """
    sections = {
        'Purpose': [],
        'Annual Leave': [],
        'Sick Leave': [],
        'Maternity/Paternity': [],
        'LWP': [],
        'Holidays': [],
        'Encashment': [],
        'Grievance': []
    }
    section_map = {
        '1': 'Purpose',
        '2': 'Annual Leave',
        '3': 'Sick Leave',
        '4': 'Maternity/Paternity',
        '5': 'LWP',
        '6': 'Holidays',
        '7': 'Encashment',
        '8': 'Grievance'
    }
    
    current_clause = None
    current_text = ''
    current_prefix = '0'
    clause_count = 0
    
    for line in lines:
        lstripped = line.lstrip()
        if not lstripped.strip():
            continue
        if re.match(r'^\d+\.\s+[A-Z]{2,}', lstripped):
            continue
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', lstripped)
        if clause_match:
            # Save previous
            if current_clause is not None:
                current_text = re.sub(r'\s+', ' ', current_text).strip()
                sections[section_map.get(current_prefix, 'Other')].append((current_clause, current_text))
            clause_count += 1
            
            current_clause = clause_match.group(1)
            current_prefix = current_clause.split('.')[0]
            current_text = clause_match.group(2)
        elif current_clause is not None:
            stripped = lstripped
            if stripped:
                if current_text:
                    current_text += '\n' + stripped
                else:
                    current_text = stripped
            else:
                current_text += '\n'
    
    # Last clause
    if current_clause is not None:
        sections[section_map.get(current_prefix, 'Other')].append((current_clause, current_text.rstrip()))
        clause_count += 1
    
    if clause_count < 20:
        raise ValueError(f"Insufficient clauses detected: {clause_count}. Expected >20.")
    
    return sections

def render_markdown(sections):
    """
    Render sections to Markdown.
    """
    md = """# Summary: CITY MUNICIPAL CORPORATION HUMAN RESOURCES DEPARTMENT EMPLOYEE LEAVE POLICY
Effective: 1 April 2024

"""
    for section_name, clauses in sections.items():
        if clauses:
            md += f'## {section_name}\n'
            for num, text in clauses:
                md += f'- {num}: {text}\n'
            md += '\n'
    return md

def summarize_policy(raw_text):
    """
    Skill: Parse and summarize policy.
    """
    if not raw_text.strip():
        raise ValueError("Empty policy text")
    
    processed_lines = preprocess_policy(raw_text)
    sections = extract_clauses(processed_lines)
    return render_markdown(sections)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument('--input', required=True, help="Path to input policy .txt")
    parser.add_argument('--output', required=True, help="Path to output summary .md")
    args = parser.parse_args()
    
    raw_policy = retrieve_policy(args.input)
    summary = summarize_policy(raw_policy)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    # For print
    processed = preprocess_policy(raw_policy)
    total_clauses = sum(len(c) for c in extract_clauses(processed).values())
    
    print("UC-0B implementation ready")
    print(f"Summary written to {args.output}")
    print(f"Clauses processed: {total_clauses}")

if __name__ == "__main__":
    main()

