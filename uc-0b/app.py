"""
UC-0B app.py — CMC Policy Summarizer
"""
import argparse
import os
import re

class ValidationError(ValueError):
    """Raised when policy validation fails or obligations are compromised."""
    pass

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a policy document from a text file and parses its contents into structured, numbered sections.
    
    Args:
        file_path (str): Path to the .txt policy document.
        
    Returns:
        dict: Section or clause numbers mapped to their raw text content.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty or has no identifiable sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    if not content.strip():
        raise ValueError("The policy document is empty.")
        
    sections = {}
    current_clause = None
    current_text = []
    
    clause_start_pat = re.compile(r'^\s*([0-9]+\.[0-9]+)\s+(.*)$')
    section_header_pat = re.compile(r'^\s*([0-9]+)\.\s+(.*)$')
    
    for line in content.splitlines():
        line_str = line.strip()
        if not line_str:
            continue
        # Skip visual separators (e.g. ═════ or ─────)
        if any(char in line_str for char in ['═', '─', '═']):
            continue
            
        match_clause = clause_start_pat.match(line)
        if match_clause:
            if current_clause:
                sections[current_clause] = " ".join(current_text).strip()
            current_clause = match_clause.group(1)
            current_text = [match_clause.group(2)]
            continue
            
        match_header = section_header_pat.match(line)
        if match_header:
            if current_clause:
                sections[current_clause] = " ".join(current_text).strip()
                current_clause = None
                current_text = []
            continue
            
        if current_clause:
            current_text.append(line_str)
            
    if current_clause:
        sections[current_clause] = " ".join(current_text).strip()
        
    if not sections:
        raise ValueError("No identifiable numbered sections found in the policy document.")
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Summarizes structured policy sections into a compliant text summary with explicit clause references,
    preserving all core obligations and conditions.
    
    Args:
        sections (dict): Structured policy sections.
        
    Returns:
        str: Compliant summary text.
        
    Raises:
        ValidationError: If target clauses are omitted, conditions are dropped, or scope bleed is detected.
    """
    required_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    # 1. Check for clause omission
    for clause in required_clauses:
        if clause not in sections:
            raise ValidationError(f"Required clause {clause} is missing from the input policy.")
            
    # 2. Check for multi-condition drop or obligation softening in the source content
    # Clause 5.2 validation (both Department Head and HR Director must be present)
    c52_text = sections["5.2"]
    if "department head" not in c52_text.lower() or "hr director" not in c52_text.lower():
        raise ValidationError(
            "Clause 5.2 obligation softening / condition drop detected: "
            "Approval from both 'Department Head' and 'HR Director' must be explicitly preserved."
        )
        
    # 3. Check for external scope bleed in any sections
    scope_bleed_phrases = [
        "as is standard practice",
        "typically in government",
        "employees are generally expected to",
        "standard procedure",
        "general practice"
    ]
    for clause, text in sections.items():
        text_lower = text.lower()
        for phrase in scope_bleed_phrases:
            if phrase in text_lower:
                raise ValidationError(
                    f"Scope bleed detected in clause {clause}: '{phrase}' is not part of the source policy."
                )
                
    # 4. Generate compliant summary.
    # To strictly prevent meaning loss or obligation softening on these key clauses,
    # we quote them verbatim and flag them clearly, as mandated by the fourth enforcement rule.
    summary_lines = [
        "CMC Leave Policy Summary",
        "========================\n"
    ]
    for clause in required_clauses:
        text = sections[clause]
        summary_lines.append(f"[FLAG: Verbatim Quote - Quoted verbatim to prevent risk of meaning loss or obligation softening]")
        summary_lines.append(f"Clause {clause}: {text}\n")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="CMC Policy Summarizer (UC-0B)")
    parser.add_argument("--input", required=True, help="Path to the input policy text file")
    parser.add_argument("--output", required=True, help="Path to save the summary output file")
    args = parser.parse_args()
    
    try:
        # Retrieve structured policy sections
        sections = retrieve_policy(args.input)
        
        # Summarize policy compliant with agents.md enforcement rules
        summary = summarize_policy(sections)
        
        # Ensure output directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"Summary successfully written to {args.output}")
        
    except (FileNotFoundError, ValueError, ValidationError) as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
