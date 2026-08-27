"""
UC-0B — Summary That Changes Meaning
HR Policy Summarizer — enforces clause preservation and condition integrity.
"""
import argparse
import sys
import re

# Key clauses to verify (from README)
KEY_CLAUSES = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward, forfeited on 31 Dec",
    "2.7": "Carry-forward days used Jan-Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service not permitted under any circumstances"
}

def retrieve_policy(file_path):
    """Load policy file and return content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"ERROR: Policy file not found: {file_path}", file=sys.stderr)
        raise

def extract_clauses(content):
    """Parse policy content into clause dictionary."""
    clauses = {}
    current_section = None
    
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Match section headers (e.g., "2. ANNUAL LEAVE")
        section_match = re.match(r'^(\d+)\.\s+[A-Z\s]+$', line)
        if section_match:
            current_section = section_match.group(1)
            clauses[current_section] = {}
            i += 1
            continue
        
        # Match clause headers (e.g., "2.1 Each permanent employee...")
        clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line)
        if clause_match and current_section:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2)
            
            # Collect continuation lines
            i += 1
            while i < len(lines):
                next_line = lines[i]
                # Stop if we hit a new clause or section
                if re.match(r'^\d+\.\d+\s+', next_line) or re.match(r'^═+$', next_line):
                    break
                if next_line.strip() and not next_line.startswith('═'):
                    clause_text += " " + next_line.strip()
                i += 1
            
            clauses[current_section][clause_num] = clause_text.strip()
            continue
        
        i += 1
    
    return clauses

def generate_summary(clauses):
    """Generate structured summary preserving all clause conditions."""
    summary_lines = []
    summary_lines.append("=" * 70)
    summary_lines.append("HR LEAVE POLICY — STRUCTURED SUMMARY")
    summary_lines.append("Source: policy_hr_leave.txt (HR-POL-001, Version 2.3)")
    summary_lines.append("=" * 70)
    summary_lines.append("")
    
    # Track which key clauses were found
    found_clauses = set()
    
    for section_num in sorted(clauses.keys(), key=int):
        section_clauses = clauses[section_num]
        if not section_clauses:
            continue
        
        # Add section header
        section_title = {
            "1": "PURPOSE AND SCOPE",
            "2": "ANNUAL LEAVE",
            "3": "SICK LEAVE",
            "4": "MATERNITY AND PATERNITY LEAVE",
            "5": "LEAVE WITHOUT PAY (LWP)",
            "6": "PUBLIC HOLIDAYS",
            "7": "LEAVE ENCASHMENT",
            "8": "GRIEVANCES"
        }.get(section_num, f"SECTION {section_num}")
        
        summary_lines.append(f"\n{section_num}. {section_title}")
        summary_lines.append("-" * 70)
        
        for clause_num in sorted(section_clauses.keys(), key=lambda x: float(x)):
            clause_text = section_clauses[clause_num]
            
            # Check if this is a key clause
            if clause_num in KEY_CLAUSES:
                found_clauses.add(clause_num)
            
            # Format clause with full text
            summary_lines.append(f"\nClause {clause_num}:")
            summary_lines.append(f"  {clause_text}")
    
    # Add verification section
    summary_lines.append("\n" + "=" * 70)
    summary_lines.append("VERIFICATION — KEY CLAUSE CHECKLIST")
    summary_lines.append("=" * 70)
    
    for clause_key, clause_desc in sorted(KEY_CLAUSES.items()):
        status = "✓ FOUND" if clause_key in found_clauses else "✗ MISSING"
        summary_lines.append(f"{clause_key}: {status} — {clause_desc}")
    
    summary_lines.append("")
    summary_lines.append(f"Total key clauses found: {len(found_clauses)}/10")
    
    if len(found_clauses) < 8:
        summary_lines.append("\n⚠ WARNING: Fewer than 8 key clauses found. Summary may be incomplete.")
    
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()
    
    try:
        # Load policy
        policy_content = retrieve_policy(args.input)
        
        # Extract clauses
        clauses = extract_clauses(policy_content)
        
        # Generate summary
        summary = generate_summary(clauses)
        
        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✓ Done. Summary written to {args.output}")
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

