"""
UC-0B app.py — Policy Summarization with Meaning Preservation
Implements RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def retrieve_policy(file_path: str) -> Optional[Dict]:
    """
    Skill: retrieve_policy
    Loads a policy document and returns structured numbered sections.
    
    Args:
        file_path: Path to the .txt policy document
        
    Returns:
        Dictionary with 'raw_text', 'clauses', and 'metadata' or None on error
    """
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"ERROR: File not found: {file_path}", file=sys.stderr)
            return None
            
        if not path.is_file():
            print(f"ERROR: Path is not a file: {file_path}", file=sys.stderr)
            return None
            
        with open(path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
        if not raw_text.strip():
            print(f"ERROR: File is empty: {file_path}", file=sys.stderr)
            return None
            
        # Extract metadata from document header (first few lines)
        lines = raw_text.split('\n')
        metadata = {}
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            if 'Document Reference:' in line:
                metadata['reference'] = line.split(':', 1)[1].strip()
            if 'Version:' in line:
                # Handle "Version: X.Y | Effective: Date" format
                version_part = line.split('Version:', 1)[1]
                if '|' in version_part:
                    metadata['version'] = version_part.split('|')[0].strip()
                    # Also extract effective date from same line
                    if 'Effective:' in version_part:
                        metadata['effective'] = version_part.split('Effective:', 1)[1].strip()
                else:
                    metadata['version'] = version_part.strip()
            elif 'Effective:' in line and 'effective' not in metadata:
                # Only if not already captured from version line
                metadata['effective'] = line.split('Effective:', 1)[1].strip()
                
        # Parse numbered clauses (format: X.Y clause text)
        # Split by clause numbers first, then clean each clause
        clause_pattern = r'^(\d+\.\d+)\s+(.+?)$'
        clauses = []
        
        # Process line by line to avoid capturing separator lines
        lines = raw_text.split('\n')
        current_clause = None
        current_text = []
        
        for line in lines:
            # Check if line starts with a clause number
            match = re.match(r'^(\d+\.\d+)\s+(.+)', line)
            if match:
                # Save previous clause if exists
                if current_clause:
                    text = ' '.join(current_text).strip()
                    # Remove any trailing separator artifacts
                    text = re.sub(r'\s*═+.*$', '', text)
                    # Clean up extra spaces before punctuation
                    text = re.sub(r'\s+([.,;:])', r'\1', text)
                    clauses.append((current_clause, text))
                # Start new clause
                current_clause = match.group(1)
                current_text = [match.group(2)]
            elif current_clause and line.strip() and not re.match(r'^═+', line) and not re.match(r'^\d+\.\s+[A-Z]', line):
                # Continue current clause (ignore separator lines and section headers)
                current_text.append(line.strip())
        
        # Don't forget the last clause
        if current_clause:
            text = ' '.join(current_text).strip()
            text = re.sub(r'\s*═+.*$', '', text)
            # Clean up extra spaces before punctuation
            text = re.sub(r'\s+([.,;:])', r'\1', text)
            clauses.append((current_clause, text))
            
        if not clauses:
            print(f"ERROR: No recognizable numbered clause structure found in: {file_path}", file=sys.stderr)
            return None
            
        return {
            'raw_text': raw_text,
            'clauses': clauses,
            'metadata': metadata
        }
        
    except Exception as e:
        print(f"ERROR: Failed to read policy file: {str(e)}", file=sys.stderr)
        return None


def summarize_policy(policy_data: Dict) -> str:
    """
    Skill: summarize_policy
    Creates a compliance-preserving summary with clause references.
    
    Args:
        policy_data: Dictionary from retrieve_policy with 'clauses' and 'metadata'
        
    Returns:
        Formatted summary string with clause references and preserved obligations
    """
    if not policy_data or not isinstance(policy_data, dict):
        return "ERROR: Invalid policy data structure"
        
    clauses = policy_data.get('clauses', [])
    metadata = policy_data.get('metadata', {})
    
    if not clauses:
        return "ERROR: No clauses found in policy data"
        
    # Check for duplicate clause numbers
    clause_numbers = [c[0] for c in clauses]
    if len(clause_numbers) != len(set(clause_numbers)):
        return "AMBIGUOUS SOURCE: Duplicate clause numbers detected"
        
    # Build summary with enforcement rules applied
    summary_lines = []
    summary_lines.append("POLICY SUMMARY")
    summary_lines.append("=" * 70)
    
    if metadata:
        if 'reference' in metadata:
            summary_lines.append(f"Document Reference: {metadata['reference']}")
        if 'version' in metadata:
            summary_lines.append(f"Version: {metadata['version']}")
        if 'effective' in metadata:
            summary_lines.append(f"Effective Date: {metadata['effective']}")
        summary_lines.append("")
        
    # Critical binding verbs that must be preserved
    binding_verbs = ['must', 'will', 'requires', 'required', 'not permitted', 
                     'shall', 'cannot', 'are forfeited', 'entitled to']
    
    # Multi-condition patterns that need special attention
    multi_condition_patterns = [
        r'(requires|require)\s+(?:approval\s+from\s+)?(.+?)\s+and\s+(.+?)(?:\.|$)',
        r'(both|all)\s+(.+?)\s+and\s+(.+?)(?:\.|$)',
    ]
    
    # Group clauses by section (first digit of clause number)
    current_section = None
    section_names = {
        '1': 'PURPOSE AND SCOPE',
        '2': 'ANNUAL LEAVE',
        '3': 'SICK LEAVE',
        '4': 'MATERNITY AND PATERNITY LEAVE',
        '5': 'LEAVE WITHOUT PAY (LWP)',
        '6': 'PUBLIC HOLIDAYS',
        '7': 'LEAVE ENCASHMENT',
        '8': 'GRIEVANCES'
    }
    
    for clause_num, clause_text in clauses:
        section = clause_num.split('.')[0]
        
        # Add section header if new section
        if section != current_section:
            if current_section is not None:
                summary_lines.append("")
            summary_lines.append(f"{section}. {section_names.get(section, 'OTHER')}")
            summary_lines.append("-" * 70)
            current_section = section
            
        # Check if clause needs verbatim preservation
        needs_verbatim = False
        
        # Check for complex multi-conditions
        for pattern in multi_condition_patterns:
            if re.search(pattern, clause_text, re.IGNORECASE):
                # Verify all conditions are complex
                if len(clause_text) > 150 or clause_text.count('and') > 1:
                    needs_verbatim = True
                    
        # Check for multiple binding verbs indicating complexity
        verb_count = sum(1 for verb in binding_verbs if verb in clause_text.lower())
        if verb_count > 2:
            needs_verbatim = True
            
        if needs_verbatim:
            summary_lines.append(f"[{clause_num}] [VERBATIM] {clause_text}")
        else:
            # Create condensed version while preserving key elements
            summary = condense_clause(clause_num, clause_text, binding_verbs)
            summary_lines.append(summary)
            
    return '\n'.join(summary_lines)


def condense_clause(clause_num: str, clause_text: str, binding_verbs: List[str]) -> str:
    """
    Helper function to condense a clause while preserving obligations.
    
    Args:
        clause_num: The clause number (e.g., "2.3")
        clause_text: The full clause text
        binding_verbs: List of verbs that must be preserved
        
    Returns:
        Condensed clause with preserved obligations
    """
    # Preserve the binding verb structure
    preserved_text = clause_text
    
    # Remove redundant phrases but keep meaning intact
    condensed = preserved_text
    
    # Remove certain verbose patterns while keeping obligation
    condensed = re.sub(r'of the City Municipal Corporation \(CMC\)', '', condensed)
    condensed = re.sub(r'from a registered medical practitioner', 'from a medical practitioner', condensed)
    # Clean up double spaces and spaces before punctuation
    condensed = re.sub(r'\s+', ' ', condensed).strip()
    condensed = re.sub(r'\s+([.,;:])', r'\1', condensed)
    
    # Ensure we haven't removed binding verbs
    for verb in binding_verbs:
        if verb in clause_text.lower() and verb not in condensed.lower():
            # Restoration needed - use original
            condensed = clause_text
            break
            
    return f"[{clause_num}] {condensed}"


def main():
    """
    Main application entry point.
    Orchestrates policy retrieval and summarization with enforcement rules.
    """
    parser = argparse.ArgumentParser(
        description='UC-0B: Policy Summarization with Meaning Preservation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
        """
    )
    
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input policy document (.txt file)'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='Path to output summary file (.txt file)'
    )
    
    args = parser.parse_args()
    
    # Validate input file extension
    if not args.input.endswith('.txt'):
        print("ERROR: Input file must be a .txt file", file=sys.stderr)
        sys.exit(1)
        
    # Step 1: Retrieve policy using retrieve_policy skill
    print(f"Loading policy document: {args.input}")
    policy_data = retrieve_policy(args.input)
    
    if policy_data is None:
        print("ERROR: Failed to retrieve policy document", file=sys.stderr)
        sys.exit(1)
        
    print(f"Successfully loaded {len(policy_data['clauses'])} clauses")
    
    # Step 2: Summarize policy using summarize_policy skill
    print("Generating compliance-preserving summary...")
    summary = summarize_policy(policy_data)
    
    if summary.startswith("ERROR:") or summary.startswith("AMBIGUOUS SOURCE"):
        print(f"\n{summary}", file=sys.stderr)
        sys.exit(1)
        
    # Step 3: Write summary to output file
    try:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary written to: {args.output}")
        print(f"\nSummary contains {len(summary.splitlines())} lines")
        
        # Verification report
        clause_refs = re.findall(r'\[(\d+\.\d+)\]', summary)
        print(f"Clause references preserved: {len(set(clause_refs))}")
        
        verbatim_count = summary.count('[VERBATIM]')
        if verbatim_count > 0:
            print(f"Clauses requiring verbatim preservation: {verbatim_count}")
            
    except Exception as e:
        print(f"ERROR: Failed to write output file: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
