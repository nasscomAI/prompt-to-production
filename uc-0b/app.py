# -*- coding: utf-8 -*-
"""
UC-0B - Summary That Changes Meaning
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    sections = {}
    current_section = "General"
    sections[current_section] = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('══'):
                continue
            
            # Check if it's a new main heading (e.g., "1. PURPOSE AND SCOPE")
            heading_match = re.match(r'^(\d+)\.\s+([A-Z\s\(\)]+)$', line)
            if heading_match:
                current_section = line
                sections[current_section] = []
                continue
            
            # Otherwise it's a clause or continuation
            sections[current_section].append(line)
            
    return sections

def summarize_policy(sections: dict) -> str:
    # We must explicitly include clauses: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2
    target_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=======================")
    summary_lines.append("The following summary outlines the critical leave obligations. Every numbered clause listed below is preserved verbatim or without loss of conditions to ensure strict compliance.\n")
    
    # Extract clauses directly from text to avoid any hallucination or condition dropping
    all_text = " ".join([" ".join(lines) for lines in sections.values()])
    
    for clause_num in target_clauses:
        # Regex to capture from "X.Y" up to the next "X.Z" or end of paragraph
        pattern = rf"({clause_num}\s+.*?)(?=\s+\d+\.\d+\s+|$)"
        match = re.search(pattern, all_text)
        if match:
            clause_text = match.group(1).strip()
            # Clean up extra spaces
            clause_text = re.sub(r'\s+', ' ', clause_text)
            summary_lines.append(f"Clause {clause_num}: {clause_text}")
        else:
            summary_lines.append(f"Clause {clause_num}: [Clause missing from source document]")
            
    return "\n".join(summary_lines)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UC-0B Policy Summarizer')
    parser.add_argument('--input',  required=True, help='Path to policy_hr_leave.txt')
    parser.add_argument('--output', required=True, help='Path to write summary_hr_leave.txt')
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Done. Summary written to {args.output}")
