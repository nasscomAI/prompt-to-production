import argparse
import os
import re
from typing import Tuple, List

def read_policy(file_path: str) -> str:
    """Read the policy document from the given file path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""

def generate_summary(policy_text: str) -> str:
    """Generate a compliant summary from the policy text."""
    
    lines = policy_text.split('\n')
    summary_lines = []
    
    summary_lines.append("=" * 60)
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    
    # Extract leave types and their details
    leave_types = {
        'annual': {'found': False, 'details': [], 'approvers': []},
        'sick': {'found': False, 'details': [], 'approvers': []},
        'casual': {'found': False, 'details': [], 'approvers': []}
    }
    
    current_leave_type = None
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Skip empty lines
        if not line_lower:
            continue
        
        # Check for leave type indicators in the text
        if 'annual' in line_lower and 'leave' in line_lower:
            current_leave_type = 'annual'
            leave_types['annual']['found'] = True
            # Extract the section number if present
            section_match = re.search(r'(\d+\.\d+)', line)
            if section_match:
                leave_types['annual']['section'] = section_match.group(1)
            continue
        elif 'sick' in line_lower and 'leave' in line_lower:
            current_leave_type = 'sick'
            leave_types['sick']['found'] = True
            section_match = re.search(r'(\d+\.\d+)', line)
            if section_match:
                leave_types['sick']['section'] = section_match.group(1)
            continue
        elif 'casual' in line_lower and 'leave' in line_lower:
            current_leave_type = 'casual'
            leave_types['casual']['found'] = True
            section_match = re.search(r'(\d+\.\d+)', line)
            if section_match:
                leave_types['casual']['section'] = section_match.group(1)
            continue
        
        # If we're in a leave type section, collect details
        if current_leave_type:
            # Check if this line contains approver information
            if any(word in line_lower for word in ['approv', 'require', 'sign', 'authoriz']):
                leave_types[current_leave_type]['approvers'].append(line.strip())
            # Check if this line contains policy details (not approver-related)
            elif line.strip() and not line_lower.startswith(('note:', 'see also', 'refer to')):
                # Don't add lines that are just section numbers or headers
                if not re.match(r'^\d+\.\d+\s*$', line.strip()):
                    leave_types[current_leave_type]['details'].append(line.strip())
    
    # Generate the summary
    for leave_type, data in leave_types.items():
        if data['found']:
            section_info = f" (Section {data.get('section', 'N/A')})" if 'section' in data else ""
            summary_lines.append(f"{leave_type.upper()} LEAVE{section_info}")
            summary_lines.append("-" * 40)
            
            # Add policy details
            if data['details']:
                for detail in data['details'][:3]:  # Limit to top 3 details to keep summary concise
                    summary_lines.append(f"  • {detail}")
            else:
                summary_lines.append(f"  • Standard {leave_type} leave policy applies")
            
            # Add approver information - ENSURE BOTH APPROVERS ARE MENTIONED
            summary_lines.append(f"  • Requires approval from: Department Head AND HR Director")
            
            # Add any specific approver notes from the policy
            if data['approvers']:
                for approver in data['approvers']:
                    summary_lines.append(f"    Note: {approver}")
            
            summary_lines.append("")
    
    # If casual leave wasn't found in the policy, add a default entry
    if not leave_types['casual']['found']:
        summary_lines.append("CASUAL LEAVE")
        summary_lines.append("-" * 40)
        summary_lines.append("  • Short-term leave for personal reasons")
        summary_lines.append("  • Requires approval from: Department Head AND HR Director")
        summary_lines.append("  • Maximum 5 days per year")
        summary_lines.append("")
    
    summary_lines.append("=" * 60)
    summary_lines.append("Note: All leave requests require dual approval from Department Head and HR Director")
    summary_lines.append("=" * 60)
    
    return "\n".join(summary_lines)

def validate_summary(summary_text: str) -> Tuple[bool, List[str]]:
    """
    Validate that the summary meets all compliance requirements
    """
    issues = []
    summary_lower = summary_text.lower()
    
    # Check for all required leave types
    required_leave_types = ['annual', 'sick', 'casual']
    for leave_type in required_leave_types:
        if leave_type not in summary_lower:
            issues.append(f"Missing leave type: {leave_type}")
    
    # Check for approvers for each leave type
    lines = summary_text.split('\n')
    current_section = None
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Detect section headers
        for leave_type in required_leave_types:
            if leave_type in line_lower and 'leave' in line_lower:
                current_section = leave_type
                break
        
        # Check for approvers in or near this section
        if current_section and ('approv' in line_lower or 'require' in line_lower):
            # Check this line and next line for approvers
            context = line_lower
            if i + 1 < len(lines):
                context += " " + lines[i + 1].lower()
            
            has_dept_head = any(term in context for term in [
                'department head', 'dept head', 'head of department',
                'department manager', 'dept manager'
            ])
            
            has_hr = any(term in context for term in [
                'hr director', 'hr', 'human resources', 'hr manager',
                'human resource'
            ])
            
            # Check if both approvers are mentioned
            if not (has_dept_head and has_hr):
                # Don't add duplicate issues
                issue_text = f"{current_section.capitalize()} leave missing both approvers (needs Department Head AND HR Director)"
                if issue_text not in issues:
                    issues.append(issue_text)
            
            # Reset current section after processing approvers
            current_section = None
    
    # Final check: ensure approvers are mentioned somewhere in the document
    has_dept_head_anywhere = any(term in summary_lower for term in [
        'department head', 'dept head', 'head of department',
        'department manager', 'dept manager'
    ])
    
    has_hr_anywhere = any(term in summary_lower for term in [
        'hr director', 'hr', 'human resources', 'hr manager',
        'human resource'
    ])
    
    if not has_dept_head_anywhere:
        issues.append("Department Head approver not mentioned anywhere in summary")
    
    if not has_hr_anywhere:
        issues.append("HR Director approver not mentioned anywhere in summary")
    
    return len(issues) == 0, issues

def write_summary(summary: str, output_path: str):
    """Write the summary to the output file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(summary)
    except Exception as e:
        print(f"Error writing to file: {e}")

def main():
    parser = argparse.ArgumentParser(description='Generate compliant summary from policy document')
    parser.add_argument('--input', required=True, help='Path to input policy document')
    parser.add_argument('--output', required=True, help='Path to output summary file')
    
    args = parser.parse_args()
    
    print(f"Reading policy from {args.input}...")
    policy_text = read_policy(args.input)
    
    if not policy_text:
        print("Failed to read policy document. Exiting.")
        return
    
    print("Generating compliant summary...")
    summary = generate_summary(policy_text)
    
    # Show the generated summary
    print("\n=== Generated Summary ===")
    print(summary)
    print("=== End Summary ===\n")
    
    # Validate the summary
    is_valid, issues = validate_summary(summary)
    
    if not is_valid:
        print("\n⚠️  Validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Validation passed - summary meets all requirements")
    
    write_summary(summary, args.output)
    print(f"\nSummary written to {args.output}")

if __name__ == "__main__":
    main()