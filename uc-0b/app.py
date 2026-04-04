"""
UC-0B app.py — Policy Summarization Agent.
Summarizes HR leave policy documents while preserving all binding obligations and conditions.
See README.md for run command and expected behaviour.
"""
import argparse
import json
from pathlib import Path

def retrieve_policy(filepath):
    """
    Loads and parses a .txt policy file, returning content as structured numbered sections.
    
    Args:
        filepath (str): Path to policy document
        
    Returns:
        dict: Dictionary with numbered sections (e.g., "2.3", "2.4") as keys and full clause text as values.
        
    Raises:
        FileNotFoundError: If file not found
        ValueError: If file cannot be parsed as structured numbered sections
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Cannot read policy file: {e}")
    
    # Parse numbered sections (e.g., "2.3", "3.4", "5.2")
    sections = {}
    lines = content.split('\n')
    current_section = None
    current_text = []
    
    for line in lines:
        # Match pattern like "2.3", "5.2", etc.
        stripped = line.strip()
        if stripped and any(c.isdigit() for c in stripped[:3]):
            # Try to identify section header
            if current_section and current_text:
                sections[current_section] = '\n'.join(current_text).strip()
            current_section = stripped.split()[0] if stripped[0].isdigit() else None
            current_text = [line]
        elif current_section:
            current_text.append(line)
    
    if current_section and current_text:
        sections[current_section] = '\n'.join(current_text).strip()
    
    if not sections:
        raise ValueError("Cannot parse policy file as structured numbered sections")
    
    return sections


def summarize_policy(sections, clause_inventory):
    """
    Takes structured policy sections and produces a clause-complete summary with explicit 
    references to source clause numbers.
    
    Args:
        sections (dict): Structured policy sections from retrieve_policy
        clause_inventory (list): List of required clause IDs to include in summary
        
    Returns:
        str: Summary text preserving all clauses and conditions with clause number references.
        
    Raises:
        ValueError: If any required clauses are missing from summary
    """
    missing_clauses = [c for c in clause_inventory if c not in sections]
    if missing_clauses:
        raise ValueError(f"Missing required clauses in policy: {', '.join(missing_clauses)}")
    
    summary_lines = ["# Policy Summary\n"]
    
    for clause_id in clause_inventory:
        if clause_id in sections:
            summary_lines.append(f"## Clause {clause_id}\n")
            summary_lines.append(sections[clause_id])
            summary_lines.append("\n")
    
    return '\n'.join(summary_lines)


def main():
    parser = argparse.ArgumentParser(
        description='Summarize HR leave policy documents while preserving all binding obligations.'
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
    
    args = parser.parse_args()
    
    # Required clauses from the policy (clause inventory)
    required_clauses = [
        "2.3", "2.4", "2.5", "2.6", "2.7", 
        "3.2", "3.4", 
        "5.2", "5.3", 
        "7.2"
    ]
    
    # Retrieve policy
    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error retrieving policy: {e}")
        return
    
    # Summarize policy
    try:
        summary = summarize_policy(sections, required_clauses)
    except ValueError as e:
        print(f"Error summarizing policy: {e}")
        return
    
    # Write output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")
        return


if __name__ == "__main__":
    main()
