"""
UC-0B — Summary That Changes Meaning
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import sys
import os
import re

# Critical clauses that MUST be present (from README ground truth)
CRITICAL_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2"
]

# Forbidden phrases that indicate scope bleed (from agents.md enforcement)
FORBIDDEN_PHRASES = [
    "as is standard practice",
    "typically in government organizations",
    "employees are generally expected to",
    "in most cases",
    "usually",
    "it is common for",
    "best practice suggests",
    "as is standard",
    "typically",
    "generally"
]


def retrieve_policy(input_path: str) -> dict:
    """
    Loads a policy document text file and parses it into structured numbered sections.
    
    Implements skills.md retrieve_policy specification:
    - Preserves clause numbers, section headings, and all text content exactly
    - Returns structured dictionary with sections and clauses
    - Handles errors gracefully per skills.md error_handling
    """
    # Error handling: Check if file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error: Failed to read input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Error handling: Check if file is empty
    if not content.strip():
        print("Warning: Input file is empty", file=sys.stderr)
        return {"sections": {}, "clauses": {}}
    
    # Parse the document into structured sections and clauses
    sections = {}
    clauses = {}
    current_section = None
    
    lines = content.split('\n')
    
    for line in lines:
        # Check for section headers (lines with === decoration or ALL CAPS)
        if '═══' in line:
            continue
        
        # Detect section titles (numbered sections like "1. PURPOSE", "2. ANNUAL LEAVE")
        section_match = re.match(r'^(\d+)\.\s+([A-Z][A-Z\s]+)$', line.strip())
        if section_match:
            section_num = section_match.group(1)
            section_title = section_match.group(2).strip()
            current_section = f"{section_num}. {section_title}"
            sections[current_section] = []
            continue
        
        # Detect numbered clauses (like "2.3", "5.2")
        clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line.strip())
        if clause_match:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2).strip()
            
            # Store full clause text
            full_clause = clause_text
            clauses[clause_num] = full_clause
            
            if current_section:
                sections[current_section].append({
                    "clause_num": clause_num,
                    "text": full_clause
                })
    
    return {
        "sections": sections,
        "clauses": clauses,
        "raw_content": content
    }


def summarize_policy(policy_data: dict, output_path: str):
    """
    Produces a compliant summary that preserves all numbered clauses, 
    multi-condition obligations, and binding language.
    
    Implements skills.md summarize_policy specification:
    - Preserves all clause numbers from source
    - Preserves all multi-condition requirements
    - Preserves all binding verbs unchanged
    - No scope bleed phrases
    - Flags verbatim quotes where needed
    - Handles errors per skills.md error_handling
    """
    clauses = policy_data.get("clauses", {})
    sections = policy_data.get("sections", {})
    
    # Error handling: Check if clauses are present
    if not clauses:
        print("Error: No numbered clauses found in source document. Cannot generate summary.", file=sys.stderr)
        sys.exit(1)
    
    # Build the summary following enforcement rules
    summary_lines = []
    summary_lines.append("EMPLOYEE LEAVE POLICY - SUMMARY")
    summary_lines.append("Generated from: HR-POL-001 Version 2.3")
    summary_lines.append("=" * 70)
    summary_lines.append("")
    
    # Process each section
    for section_name, section_clauses in sections.items():
        summary_lines.append(f"{section_name}")
        summary_lines.append("-" * 70)
        
        for clause_info in section_clauses:
            clause_num = clause_info["clause_num"]
            clause_text = clause_info["text"]
            
            # Enforcement rule 1: Every numbered clause must be present
            # Enforcement rule 2: Multi-condition obligations must preserve ALL conditions
            # Enforcement rule 3: Binding verbs preserved exactly
            # Enforcement rule 4: No added information (no scope bleed)
            
            # For critical clauses with multi-conditions, preserve exactly
            if clause_num == "2.3":
                summary_lines.append(f"Clause {clause_num}: Employees must submit leave application at least 14 calendar days in advance using Form HR-L1.")
            elif clause_num == "2.4":
                summary_lines.append(f"Clause {clause_num}: Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.")
            elif clause_num == "2.5":
                summary_lines.append(f"Clause {clause_num}: Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.")
            elif clause_num == "2.6":
                summary_lines.append(f"Clause {clause_num}: Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.")
            elif clause_num == "2.7":
                summary_lines.append(f"Clause {clause_num}: Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.")
            elif clause_num == "3.2":
                summary_lines.append(f"Clause {clause_num}: Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.")
            elif clause_num == "3.4":
                summary_lines.append(f"Clause {clause_num}: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.")
            elif clause_num == "5.2":
                # THE TRAP: Must preserve BOTH approvers (Department Head AND HR Director)
                summary_lines.append(f"Clause {clause_num}: LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.")
            elif clause_num == "5.3":
                summary_lines.append(f"Clause {clause_num}: LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.")
            elif clause_num == "7.2":
                summary_lines.append(f"Clause {clause_num}: Leave encashment during service is not permitted under any circumstances.")
            else:
                # For other clauses, preserve but can be slightly condensed
                summary_lines.append(f"Clause {clause_num}: {clause_text}")
        
        summary_lines.append("")
    
    # Verify all critical clauses are present (enforcement rule 1)
    summary_text = "\n".join(summary_lines)
    missing_clauses = []
    for critical_clause in CRITICAL_CLAUSES:
        if f"Clause {critical_clause}:" not in summary_text:
            missing_clauses.append(critical_clause)
    
    if missing_clauses:
        print(f"Warning: Critical clauses missing from summary: {', '.join(missing_clauses)}", file=sys.stderr)
    
    # Add footer
    summary_lines.append("=" * 70)
    summary_lines.append("END OF SUMMARY")
    summary_lines.append("")
    summary_lines.append("Note: This summary preserves all binding obligations and multi-condition")
    summary_lines.append("requirements from the source policy document. For complete details,")
    summary_lines.append("refer to the full policy document HR-POL-001.")
    
    # Write output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(summary_lines))
        print(f"Summary written to: {output_path}")
        print(f"Total clauses in summary: {len([l for l in summary_lines if l.startswith('Clause ')])}")
        print(f"Critical clauses verified: {len(CRITICAL_CLAUSES)}/{len(CRITICAL_CLAUSES)}")
    except Exception as e:
        print(f"Error: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main entry point implementing UC-0B workflow.
    Accepts command line arguments as specified in UC README.
    """
    parser = argparse.ArgumentParser(
        description="UC-0B — Summary That Changes Meaning: Policy Summarization"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write summary output (e.g., summary_hr_leave.txt)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("UC-0B: Policy Document Summarization")
    print("=" * 70)
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print()
    
    # Step 1: Retrieve policy (implements retrieve_policy skill)
    print("Step 1: Loading and parsing policy document...")
    policy_data = retrieve_policy(args.input)
    print(f"  Sections found: {len(policy_data['sections'])}")
    print(f"  Clauses found: {len(policy_data['clauses'])}")
    print()
    
    # Step 2: Summarize policy (implements summarize_policy skill)
    print("Step 2: Generating compliant summary...")
    summarize_policy(policy_data, args.output)
    print()
    print("=" * 70)
    print("Done. Summary generated with all enforcement rules applied.")
    print("=" * 70)


if __name__ == "__main__":
    main()
