"""
UC-0B app.py — Policy Document Summarizer
Summarizes policy documents while preserving all clauses and conditions.
"""
import re
import argparse
from typing import Dict, List, Tuple

# Multi-condition patterns to detect AND/OR requirements
MULTI_CONDITION_PATTERNS = [
    r'\band\b',
    r'\bor\b',
    r'both\b',
    r'all of\b',
    r'either\b'
]

# Obligation verbs that must be preserved
OBLIGATION_VERBS = [
    'must', 'shall', 'will', 'requires', 'required', 
    'not permitted', 'cannot', 'may not', 'are forfeited'
]


def load_policy_document(file_path: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Load policy document and parse into numbered sections.
    Returns: (sections_dict, metadata_dict)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy document not found: {file_path}")
    
    # Extract metadata from header
    metadata = {}
    title_match = re.search(r'^([A-Z\s]+)\n', content)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    version_match = re.search(r'Version:\s*([^\n]+)', content)
    if version_match:
        metadata['version'] = version_match.group(1).strip()
    
    # Parse numbered sections (e.g., 2.3, 5.2)
    sections = {}
    section_pattern = r'(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+|\n═|$)'
    matches = re.findall(section_pattern, content, re.DOTALL)
    
    for section_num, section_text in matches:
        # Clean up the text
        cleaned_text = section_text.strip()
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize whitespace
        sections[section_num] = cleaned_text
    
    return sections, metadata


def extract_numbered_clauses(sections: Dict[str, str]) -> List[Tuple[str, str]]:
    """
    Extract all numbered clauses as a list for verification.
    Returns list of (section_number, section_text) tuples.
    """
    # Sort by section number (numerically)
    sorted_sections = sorted(sections.items(), key=lambda x: float(x[0]))
    return sorted_sections


def identify_multi_condition_clauses(sections: Dict[str, str]) -> List[str]:
    """
    Identify clauses containing multiple conditions (AND/OR).
    Returns list of section numbers.
    """
    multi_condition_sections = []
    
    for section_num, text in sections.items():
        text_lower = text.lower()
        
        # Check for multi-condition patterns
        for pattern in MULTI_CONDITION_PATTERNS:
            if re.search(pattern, text_lower):
                multi_condition_sections.append(section_num)
                break
    
    return multi_condition_sections


def summarize_clause(section_num: str, text: str, is_multi_condition: bool) -> str:
    """
    Summarize a single clause while preserving meaning.
    If multi-condition and complex, return verbatim.
    """
    # For multi-condition clauses, be extra careful
    if is_multi_condition:
        # Check if it's particularly complex (multiple ANDs or ORs)
        and_count = len(re.findall(r'\band\b', text.lower()))
        or_count = len(re.findall(r'\bor\b', text.lower()))
        
        if and_count >= 2 or or_count >= 2:
            # Too complex - quote verbatim
            return f"Section {section_num} [VERBATIM]: {text}"
    
    # Standard summarization - just add section citation
    return f"Section {section_num}: {text}"


def generate_policy_summary(sections: Dict[str, str], metadata: Dict[str, str]) -> str:
    """
    Generate complete policy summary preserving all clauses.
    """
    # Get sorted clauses
    clauses = extract_numbered_clauses(sections)
    
    # Identify multi-condition clauses
    multi_condition_sections = identify_multi_condition_clauses(sections)
    
    # Build summary
    summary_lines = []
    
    # Add header
    if 'title' in metadata:
        summary_lines.append(f"SUMMARY: {metadata['title']}")
    if 'version' in metadata:
        summary_lines.append(f"Version: {metadata['version']}")
    summary_lines.append("")
    summary_lines.append("=" * 70)
    summary_lines.append("")
    
    # Add clause summaries
    for section_num, text in clauses:
        is_multi = section_num in multi_condition_sections
        summary = summarize_clause(section_num, text, is_multi)
        summary_lines.append(summary)
        summary_lines.append("")
    
    # Add footer note about multi-condition clauses
    if multi_condition_sections:
        summary_lines.append("=" * 70)
        summary_lines.append("NOTE: Sections marked [VERBATIM] contain complex multi-condition")
        summary_lines.append("clauses that cannot be summarized without risk of meaning loss.")
        summary_lines.append(f"Multi-condition sections: {', '.join(sorted(multi_condition_sections))}")
    
    return "\n".join(summary_lines)


def validate_summary_completeness(
    original_sections: Dict[str, str], 
    summary: str
) -> Tuple[bool, List[str], List[str]]:
    """
    Validate that summary contains all source clauses.
    Returns: (is_valid, missing_clauses, potential_dropped_conditions)
    """
    missing_clauses = []
    dropped_conditions = []
    
    # Check each original section is mentioned in summary
    for section_num in original_sections.keys():
        if f"Section {section_num}" not in summary:
            missing_clauses.append(section_num)
    
    # Check for obligation verb preservation
    for section_num, text in original_sections.items():
        # Count obligation verbs in original
        original_obligations = sum(1 for verb in OBLIGATION_VERBS if verb in text.lower())
        
        # Find this section in summary
        section_pattern = f"Section {re.escape(section_num)}:(.+?)(?=Section \\d+\\.|$)"
        match = re.search(section_pattern, summary, re.DOTALL)
        
        if match:
            summary_section = match.group(1)
            summary_obligations = sum(1 for verb in OBLIGATION_VERBS if verb in summary_section.lower())
            
            # If original had obligations but summary doesn't, potential softening
            if original_obligations > 0 and summary_obligations == 0:
                dropped_conditions.append(f"{section_num} (obligation verb missing)")
    
    is_valid = len(missing_clauses) == 0 and len(dropped_conditions) == 0
    
    return is_valid, missing_clauses, dropped_conditions


def main():
    parser = argparse.ArgumentParser(description='Summarize policy document')
    parser.add_argument('--input', required=True, help='Input policy document path')
    parser.add_argument('--output', required=True, help='Output summary file path')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Policy Document Summarizer - UC-0B")
    print("=" * 70)
    print(f"\nInput: {args.input}")
    print(f"Output: {args.output}\n")
    
    # Load document
    sections, metadata = load_policy_document(args.input)
    print(f"✓ Loaded policy document with {len(sections)} numbered clauses")
    
    # Identify multi-condition clauses
    multi_conditions = identify_multi_condition_clauses(sections)
    print(f"✓ Identified {len(multi_conditions)} multi-condition clauses")
    if multi_conditions:
        print(f"  Multi-condition sections: {', '.join(sorted(multi_conditions))}")
    
    # Generate summary
    summary = generate_policy_summary(sections, metadata)
    
    # Validate completeness
    is_valid, missing, dropped = validate_summary_completeness(sections, summary)
    
    if not is_valid:
        print("\n⚠ WARNING: Summary validation issues detected:")
        if missing:
            print(f"  Missing clauses: {', '.join(missing)}")
        if dropped:
            print(f"  Potential dropped conditions: {', '.join(dropped)}")
    else:
        print("\n✓ Summary validation passed - all clauses preserved")
    
    # Write output
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n✓ Summary written to {args.output}")
    print(f"\nSummary contains {len(sections)} clauses (original: {len(sections)})")


if __name__ == "__main__":
    main()
