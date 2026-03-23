"""
UC-0B — Summary That Changes Meaning
Preserves all numbered clauses and their binding conditions without omission or softening.
"""
import argparse
import re
import sys
from typing import List, Tuple

def extract_clauses(document_path: str) -> List[Tuple[str, str, str]]:
    """
    Extract all numbered clauses from policy document.
    Returns list of (clause_number, full_text, binding_verb).
    """
    try:
        with open(document_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Document not found: {document_path}")
        sys.exit(1)
    
    clauses = []
    current_clause = None
    current_text = []
    
    # Regex to match clause numbers like 2.3, 5.2
    clause_num_pattern = re.compile(r'^(\d+\.\d+)\s')
    
    for line in lines:
        line = line.rstrip()
        
        # Check if this line starts a new clause
        match = clause_num_pattern.match(line.strip())
        
        if match:
            # Save previous clause if exists
            if current_clause is not None:
                clause_num, clause_text = current_clause
                clause_text = clause_text.strip()
                # Clean up whitespace
                clause_text = re.sub(r'\s+', ' ', clause_text)
                
                # Extract binding verb
                binding_verb = extract_binding_verb(clause_text)
                clauses.append((clause_num, clause_text, binding_verb))
            
            # Start new clause
            clause_num = match.group(1)
            clause_content = line.strip()[len(clause_num):].strip()
            current_clause = (clause_num, clause_content)
            current_text = []
        
        elif current_clause is not None and line.strip() and not line.startswith('═'):
            # Continue current clause
            current_text.append(line.strip())
            current_clause = (current_clause[0], current_clause[1] + ' ' + line.strip())
    
    # Save last clause
    if current_clause is not None:
        clause_num, clause_text = current_clause
        clause_text = clause_text.strip()
        clause_text = re.sub(r'\s+', ' ', clause_text)
        binding_verb = extract_binding_verb(clause_text)
        clauses.append((clause_num, clause_text, binding_verb))
    
    return clauses


def extract_binding_verb(text: str) -> str:
    """Extract the binding verb from clause text."""
    binding_verbs = [
        'must not',
        'not permitted',
        'are forfeited',
        'must',
        'cannot',
        'requires',
        'require',
        'may',
        'will',
    ]
    
    text_lower = text.lower()
    for verb in binding_verbs:
        if verb in text_lower:
            return verb.upper()
    
    return ""


def preserve_multi_conditions(clause_text: str) -> str:
    """
    Ensure multi-condition obligations are preserved with all conditions.
    Identifies patterns like "approval from X and Y" and preserves both.
    """
    # Look for patterns with multiple entities
    multi_entity_patterns = [
        r'(approval\s+from\s+[^.]+(?:and|&)[^.]+)',
        r'(requires?\s+[^.]+(?:and|&)[^.]+)',
        r'(must\s+be\s+[^.]+(?:and|&)[^.]+)',
    ]
    
    result = clause_text
    
    for pattern in multi_entity_patterns:
        matches = re.finditer(pattern, clause_text, re.IGNORECASE)
        for match in matches:
            # Replace ampersand with "and" for clarity
            condition = match.group(1)
            condition = condition.replace('&', 'and')
            result = result.replace(match.group(0), condition)
    
    return result


def generate_summary(clauses: List[Tuple[str, str, str]]) -> str:
    """
    Generate summary preserving all clauses and conditions.
    """
    if not clauses:
        return "No clauses found in document."
    
    summary_lines = []
    summary_lines.append("POLICY SUMMARY - NUMBERED CLAUSES PRESERVED")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    
    current_section = None
    
    for clause_num, clause_text, binding_verb in clauses:
        # Extract section number (first digit before the dot)
        section_match = re.match(r'(\d+)', clause_num)
        section = section_match.group(1) if section_match else ""
        
        # Add section header if changed
        if section != current_section:
            current_section = section
            section_headers = {
                "2": "ANNUAL LEAVE",
                "3": "SICK LEAVE",
                "4": "MATERNITY AND PATERNITY LEAVE",
                "5": "LEAVE WITHOUT PAY (LWP)",
                "6": "PUBLIC HOLIDAYS",
                "7": "LEAVE ENCASHMENT"
            }
            if section in section_headers:
                summary_lines.append("")
                summary_lines.append(f"--- {section_headers[section]} ---")
        
        # Preserve multi-conditions
        preserved_text = preserve_multi_conditions(clause_text)
        
        # Output clause with its binding verb in uppercase for clarity
        if binding_verb:
            summary_lines.append(f"{clause_num}: [{binding_verb.upper()}] {preserved_text}")
        else:
            summary_lines.append(f"{clause_num}: {preserved_text}")
    
    summary_lines.append("")
    summary_lines.append("=" * 60)
    summary_lines.append("END OF SUMMARY")
    
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input",  required=True, help="Path to policy document text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()
    
    try:
        # Extract clauses from document
        clauses = extract_clauses(args.input)
        
        if not clauses:
            print(f"Warning: No numbered clauses found in {args.input}")
        else:
            print(f"Extracted {len(clauses)} clauses from document.")
        
        # Generate summary
        summary = generate_summary(clauses)
        
        # Write summary to output file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary written to {args.output}")
        
        # Print first 50 lines to show progress
        lines = summary.split('\n')
        print("\nFirst 20 lines of summary:")
        print("\n".join(lines[:20]))
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
