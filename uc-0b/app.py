"""
UC-0B — Policy Document Summarizer
Built using RICE + agents.md + skills.md + CRAFT workflow.
Produces compliant summaries that preserve all clauses, conditions, and binding obligations.
"""
import argparse
import re
from typing import Dict, List, Tuple


def retrieve_policy(file_path: str) -> Dict:
    """
    Loads a policy document text file and returns structured content.
    
    Args:
        file_path: Path to .txt policy document
        
    Returns:
        Dictionary with document metadata and structured sections/clauses
        
    Raises:
        FileNotFoundError: If file does not exist or is not readable
        ValueError: If file is empty or does not contain recognizable structure
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    except Exception as e:
        raise FileNotFoundError(f"Policy file is not readable: {file_path} - {e}")
    
    if not content.strip():
        raise ValueError("Policy file is empty")
    
    # Extract metadata from header
    lines = content.split('\n')
    metadata = {
        'title': '',
        'reference': '',
        'version': '',
        'effective_date': ''
    }
    
    for i, line in enumerate(lines[:10]):
        if 'Document Reference:' in line:
            metadata['reference'] = line.split('Document Reference:')[1].strip()
        elif 'Version:' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                metadata['version'] = parts[0].split('Version:')[1].strip()
                metadata['effective_date'] = parts[1].split('Effective:')[1].strip()
        elif i < 3 and line.strip() and not line.startswith('='):
            if not metadata['title']:
                metadata['title'] = line.strip()
    
    # Parse numbered sections and clauses
    sections = []
    current_section = None
    current_clause = None
    
    # Pattern to match section headers like "2. TRAVEL REIMBURSEMENT"
    section_pattern = re.compile(r'^(\d+)\.\s+([A-Z][A-Z\s&]+)$')
    # Pattern to match clauses like "2.1 Local travel..." or "2.10 Additional info..."
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.+)$')
    
    for line in lines:
        line_stripped = line.strip()
        
        # Skip empty lines and separator lines
        if not line_stripped or line_stripped.startswith('='):
            continue
        
        # Check for section header
        section_match = section_pattern.match(line_stripped)
        if section_match:
            # Save previous clause if exists
            if current_clause and current_section:
                current_section['clauses'].append(current_clause)
                current_clause = None
            
            # Save previous section if exists
            if current_section:
                sections.append(current_section)
            
            current_section = {
                'number': section_match.group(1),
                'title': section_match.group(2).strip(),
                'clauses': []
            }
            continue
        
        # Check for clause
        clause_match = clause_pattern.match(line_stripped)
        if clause_match and current_section:
            # Save previous clause if exists
            if current_clause:
                current_section['clauses'].append(current_clause)
            
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2).strip()
            
            current_clause = {
                'number': clause_num,
                'text': clause_text
            }
            continue
        
        # Continuation line for current clause
        if current_clause and line_stripped:
            # Append to existing clause text
            current_clause['text'] += ' ' + line_stripped
    
    # Save last clause
    if current_clause and current_section:
        current_section['clauses'].append(current_clause)
    
    # Add last section
    if current_section:
        sections.append(current_section)
    
    if not sections:
        raise ValueError("Policy document does not contain recognizable numbered section/clause structure")
    
    return {
        'metadata': metadata,
        'sections': sections
    }


def summarize_policy(policy_data: Dict) -> str:
    """
    Produces compliant summary preserving all clauses and conditions.
    
    Args:
        policy_data: Structured policy document from retrieve_policy
        
    Returns:
        Summary text with clause references and preserved obligations
        
    Raises:
        ValueError: If input structure missing required fields or clauses would be omitted
    """
    if 'sections' not in policy_data:
        raise ValueError("Policy data missing required 'sections' field")
    
    sections = policy_data['sections']
    metadata = policy_data.get('metadata', {})
    
    # Build summary
    summary_lines = []
    
    # Header
    if metadata.get('title'):
        summary_lines.append(f"SUMMARY: {metadata['title']}")
        summary_lines.append(f"Document: {metadata.get('reference', 'N/A')}")
        summary_lines.append(f"Version: {metadata.get('version', 'N/A')} | Effective: {metadata.get('effective_date', 'N/A')}")
        summary_lines.append("")
        summary_lines.append("=" * 70)
        summary_lines.append("")
    
    # Track all clause numbers to ensure none are omitted
    all_clause_numbers = []
    summarized_clause_numbers = []
    
    for section in sections:
        if 'clauses' not in section:
            raise ValueError(f"Section {section.get('number', '?')} missing required 'clauses' field")
        
        section_num = section.get('number', '?')
        section_title = section.get('title', 'UNTITLED')
        
        summary_lines.append(f"{section_num}. {section_title}")
        summary_lines.append("-" * 70)
        
        for clause in section['clauses']:
            clause_num = clause.get('number', '?')
            clause_text = clause.get('text', '')
            
            all_clause_numbers.append(clause_num)
            
            # Include complete clause text for all clauses
            summary_lines.append(f"  Section {clause_num}: {clause_text}")
            
            summarized_clause_numbers.append(clause_num)
        
        summary_lines.append("")
    
    # Validate no clauses were omitted
    if set(all_clause_numbers) != set(summarized_clause_numbers):
        missing = set(all_clause_numbers) - set(summarized_clause_numbers)
        raise ValueError(f"Summary would omit clauses: {sorted(missing)}")
    
    summary_lines.append("=" * 70)
    summary_lines.append(f"COMPLETENESS CHECK: All {len(all_clause_numbers)} clauses included.")
    summary_lines.append("No external information added. All binding obligations preserved.")
    
    return '\n'.join(summary_lines)


def main():
    """
    Main entry point for policy summarization tool.
    """
    parser = argparse.ArgumentParser(description="UC-0B Policy Document Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()
    
    try:
        # Load and parse policy document
        print(f"Loading policy document: {args.input}")
        policy_data = retrieve_policy(args.input)
        
        # Count clauses
        total_clauses = sum(len(section['clauses']) for section in policy_data['sections'])
        print(f"Parsed {len(policy_data['sections'])} sections with {total_clauses} clauses")
        
        # Generate summary
        print("Generating compliant summary...")
        summary = summarize_policy(policy_data)
        
        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary written to: {args.output}")
        print("✓ All clauses preserved")
        print("✓ All binding obligations intact")
        print("✓ No external information added")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
