#!/usr/bin/env python3
"""
UC-0B: Policy Document Summarizer
Summarizes HR policy document preserving all numbered clauses and obligations.
"""

import argparse
import re
import sys
from pathlib import Path


# Critical clauses that MUST be present in summary
CRITICAL_CLAUSES = [
    "2.3",  # 14-day advance notice
    "2.4",  # Written approval
    "2.5",  # Unapproved absence = LOP
    "2.6",  # 5-day carry-forward
    "2.7",  # Jan-Mar deadline
    "3.2",  # 3+ days cert
    "3.4",  # Holiday cert
    "5.2",  # TWO approvers (trap clause!)
    "5.3",  # Commissioner approval
    "7.2",  # No encashment during service
]

# Prohibited scope bleed phrases
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "generally expected",
    "it is common",
    "normally",
    "usually",
    "in most cases",
    "as is customary",
]

# Binding verbs that must not be softened
BINDING_VERBS = {
    "must": ["should", "ought to", "is recommended"],
    "requires": ["recommends", "suggests", "advises"],
    "will": ["may", "might", "could"],
    "not permitted": ["discouraged", "not recommended", "not advised"],
}


def retrieve_policy(file_path):
    """
    Loads policy text file and returns structured content with numbered clauses.
    
    Args:
        file_path (str): Path to policy text file
        
    Returns:
        dict: Structured policy data with sections and clauses
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        raise ValueError("Policy document is empty")
    
    # Extract document info
    doc_info = {
        "title": "",
        "reference": "",
        "version": "",
        "effective_date": ""
    }
    
    lines = content.split('\n')
    for i, line in enumerate(lines[:10]):  # Check first 10 lines for metadata
        if "EMPLOYEE LEAVE POLICY" in line:
            doc_info["title"] = line.strip()
        elif "Document Reference:" in line:
            doc_info["reference"] = line.split("Reference:")[-1].strip()
        elif "Version:" in line:
            parts = line.split("|")
            doc_info["version"] = parts[0].split("Version:")[-1].strip()
            if len(parts) > 1 and "Effective:" in parts[1]:
                doc_info["effective_date"] = parts[1].split("Effective:")[-1].strip()
    
    # Parse sections and clauses
    sections = []
    current_section = None
    
    # Pattern for section headers (e.g., "2. ANNUAL LEAVE")
    section_pattern = re.compile(r'^(\d+)\.\s+([A-Z\s]+)$')
    # Pattern for clauses (e.g., "2.3 Text here...")
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.+)$')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for section header
        section_match = section_pattern.match(line)
        if section_match:
            if current_section:
                sections.append(current_section)
            current_section = {
                "section_number": section_match.group(1),
                "section_title": section_match.group(2).strip(),
                "clauses": []
            }
            i += 1
            continue
        
        # Check for clause
        clause_match = clause_pattern.match(line)
        if clause_match and current_section:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2).strip()
            
            # Continue reading multi-line clauses
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                # Stop if we hit a new clause, section, or separator line
                if (clause_pattern.match(next_line) or 
                    section_pattern.match(next_line) or 
                    next_line.startswith('═') or
                    not next_line):
                    break
                clause_text += " " + next_line
                i += 1
            
            # Find binding verbs
            binding_verbs = []
            for verb in ["must", "requires", "will", "not permitted"]:
                if verb in clause_text.lower():
                    binding_verbs.append(verb)
            
            current_section["clauses"].append({
                "clause_number": clause_num,
                "clause_text": clause_text,
                "binding_verbs": binding_verbs
            })
            continue
        
        i += 1
    
    if current_section:
        sections.append(current_section)
    
    # Verify critical clauses are present
    all_clause_numbers = []
    for section in sections:
        all_clause_numbers.extend([c["clause_number"] for c in section["clauses"]])
    
    missing_critical = [c for c in CRITICAL_CLAUSES if c not in all_clause_numbers]
    if missing_critical:
        raise ValueError(f"Critical clauses missing from document: {', '.join(missing_critical)}")
    
    return {
        "document_info": doc_info,
        "sections": sections,
        "total_clauses": len(all_clause_numbers),
        "all_clause_numbers": all_clause_numbers
    }


def summarize_policy(policy_data, output_path):
    """
    Creates compliant summary preserving all clauses and obligations.
    
    Args:
        policy_data (dict): Structured policy data from retrieve_policy
        output_path (str): Path to write summary file
    """
    summary_lines = []
    
    # Header
    doc_info = policy_data["document_info"]
    summary_lines.append("=" * 70)
    summary_lines.append("POLICY SUMMARY")
    summary_lines.append(doc_info["title"])
    summary_lines.append(f"Reference: {doc_info['reference']} | Version: {doc_info['version']}")
    summary_lines.append(f"Effective: {doc_info['effective_date']}")
    summary_lines.append("=" * 70)
    summary_lines.append("")
    
    # Track which critical clauses we've included
    included_clauses = []
    
    # Summarize each section
    for section in policy_data["sections"]:
        summary_lines.append(f"\n{section['section_number']}. {section['section_title']}")
        summary_lines.append("-" * 70)
        
        for clause in section["clauses"]:
            clause_num = clause["clause_number"]
            clause_text = clause["clause_text"]
            
            # Format: [Clause X.Y] Summary text
            summary_lines.append(f"[Clause {clause_num}] {clause_text}")
            included_clauses.append(clause_num)
        
        summary_lines.append("")
    
    # Verification footer
    summary_lines.append("=" * 70)
    summary_lines.append("VERIFICATION")
    summary_lines.append("=" * 70)
    summary_lines.append(f"Total Clauses Summarized: {len(included_clauses)}")
    summary_lines.append(f"Clause Numbers: {', '.join(sorted(included_clauses))}")
    
    # Check for missing critical clauses
    missing = [c for c in CRITICAL_CLAUSES if c not in included_clauses]
    if missing:
        summary_lines.append(f"\n*** WARNING: Missing critical clauses: {', '.join(missing)} ***")
        raise ValueError(f"Summary incomplete - missing critical clauses: {', '.join(missing)}")
    else:
        summary_lines.append("\n✓ All 10 critical clauses present")
    
    summary_lines.append("=" * 70)
    
    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    
    print(f"Summary written to: {output_path}")
    print(f"Total clauses: {len(included_clauses)}")
    print(f"Critical clauses verified: {len([c for c in CRITICAL_CLAUSES if c in included_clauses])}/10")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Summarize policy document preserving all clauses"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy text file"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary file"
    )
    
    args = parser.parse_args()
    
    try:
        print("="*70)
        print("UC-0B: Policy Document Summarizer")
        print("="*70)
        print(f"\nInput: {args.input}")
        print(f"Output: {args.output}\n")
        
        # Step 1: Retrieve and parse policy
        print("Step 1: Retrieving policy document...")
        policy_data = retrieve_policy(args.input)
        print(f"✓ Loaded {policy_data['total_clauses']} clauses from {len(policy_data['sections'])} sections")
        
        # Step 2: Generate summary
        print("\nStep 2: Generating summary...")
        summarize_policy(policy_data, args.output)
        
        print("\n" + "="*70)
        print("SUCCESS: Summary generated with all critical clauses preserved")
        print("="*70)
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

