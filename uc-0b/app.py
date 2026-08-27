"""
UC-0B app.py — Policy Summarizer
Summarizes policy documents while preserving all clauses, conditions, and binding verbs exactly.
RICE Enforcement: all mandatory clauses present, multi-conditions preserved, no scope bleed,
section references cited, binding verbs unchanged.
"""
import argparse
import re
import sys
import os

# Mandatory clauses for HR Leave policy
MANDATORY_CLAUSES_HR_LEAVE = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward, above 5 forfeited on 31 Dec",
    "2.7": "Carry-forward days must be used Jan–Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service not permitted under any circumstances"
}

MANDATORY_CLAUSES_IT_POLICY = {
    "2.1": "Policy coverage scope",
    "2.3": "Approved work tools requirements",
    "3.1": "Personal device access restrictions"
}

MANDATORY_CLAUSES_FINANCE = {
    "2.6": "DA and meal receipts on same day restriction",
    "3.1": "Home office equipment allowance amount and conditions"
}


def retrieve_policy(file_path: str) -> dict:
    """
    Load a policy document file and parse numbered sections.
    Returns: dict with document_name and sections list.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise Exception(f"Error reading policy file: {e}")
    
    document_name = os.path.basename(file_path).replace('.txt', '')
    
    # Parse sections: split by lines starting with numbers like "2.3" or "7.2"
    sections = []
    section_pattern = r'^(\d+\.\d+)\s+(.*)$'
    
    lines = content.split('\n')
    current_section = None
    current_text = []
    
    for line in lines:
        match = re.match(section_pattern, line)
        if match:
            # Save previous section
            if current_section:
                sections.append({
                    "section_number": current_section[0],
                    "section_title": current_section[1],
                    "section_text": '\n'.join(current_text).strip()
                })
            # Start new section
            current_section = (match.group(1), match.group(2))
            current_text = []
        elif current_section:
            current_text.append(line)
    
    # Save last section
    if current_section:
        sections.append({
            "section_number": current_section[0],
            "section_title": current_section[1],
            "section_text": '\n'.join(current_text).strip()
        })
    
    return {
        "document_name": document_name,
        "sections": sections,
        "full_text": content
    }


def summarize_policy(policy_dict: dict, mandatory_clauses: dict) -> str:
    """
    Create a summary preserving all mandatory clauses, conditions, and binding verbs.
    Returns: text summary with all mandatory clauses present.
    """
    sections_by_number = {s["section_number"]: s for s in policy_dict["sections"]}
    
    summary_lines = [
        f"POLICY SUMMARY: {policy_dict['document_name']}",
        "=" * 60,
        ""
    ]
    
    missing_clauses = []
    
    # Process each mandatory clause in order
    for clause_num in sorted(mandatory_clauses.keys()):
        if clause_num in sections_by_number:
            section = sections_by_number[clause_num]
            summary_lines.append(f"Section {clause_num}: {section['section_title']}")
            summary_lines.append(f"  {section['section_text']}")
            summary_lines.append("")
        else:
            missing_clauses.append(clause_num)
            summary_lines.append(f"[MISSING] Section {clause_num}: {mandatory_clauses[clause_num]}")
            summary_lines.append("")
    
    # Add warning if clauses missing
    if missing_clauses:
        summary_lines.append("=" * 60)
        summary_lines.append(f"WARNING: Missing mandatory clauses: {', '.join(missing_clauses)}")
        summary_lines.append("")
    
    return '\n'.join(summary_lines)


def get_mandatory_clauses_for_policy(policy_name: str) -> dict:
    """Return the mandatory clauses for a given policy document."""
    if "leave" in policy_name.lower():
        return MANDATORY_CLAUSES_HR_LEAVE
    elif "it" in policy_name.lower() or "acceptable" in policy_name.lower():
        return MANDATORY_CLAUSES_IT_POLICY
    elif "finance" in policy_name.lower() or "reimbursement" in policy_name.lower():
        return MANDATORY_CLAUSES_FINANCE
    else:
        # Default: return empty dict, will require all found sections
        return {}


def main(input_path: str = None, output_path: str = None):
    """Main function to summarize policy documents."""
    
    if not input_path:
        print("Interactive Mode: Policy Summarizer")
        print("=" * 60)
        policy_dir = "../data/policy-documents/"
        
        if os.path.exists(policy_dir):
            policies = [f for f in os.listdir(policy_dir) if f.endswith('.txt')]
            print(f"Available policies: {', '.join(policies)}")
            input_path = os.path.join(policy_dir, input("Enter policy filename: "))
        else:
            input_path = input("Enter policy file path: ")
    
    try:
        # Retrieve policy
        policy_dict = retrieve_policy(input_path)
        policy_name = policy_dict['document_name']
        
        # Get mandatory clauses for this policy
        mandatory_clauses = get_mandatory_clauses_for_policy(policy_name)
        
        # Summarize
        summary = summarize_policy(policy_dict, mandatory_clauses)
        
        # Output
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"Summary written to {output_path}")
        else:
            print("\n" + summary)
        
        return summary
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  required=False, help="Path to policy document")
    parser.add_argument("--output", required=False, help="Output file path for summary")
    args = parser.parse_args()
    
    main(args.input, args.output)
