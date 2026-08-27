
import argparse
import re
import sys

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured numbered sections to prevent omission of any clause.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find file at {filepath}")
        sys.exit(1)
        
    structured_sections = {}
    current_clause = ""
    current_text = []
    
    CLAUSE_PATTERN = r'^(\d+\.\d+)\s+(.*)'
    
    for line in lines:
        line_clean = line.strip()
        # Skip empty lines, decorative borders like ════, and main section headers
        if not line_clean or line_clean.startswith("═") or re.match(r'^\d+\.\s+[A-Z\s\(\)]+$', line_clean):
            continue
            
        regex_match = re.match(CLAUSE_PATTERN, line_clean)
        if regex_match:
            # Finalize previous clause
            if current_clause:
                structured_sections[current_clause] = ' '.join(current_text)
            
            # Start new clause tracking
            current_clause = regex_match.group(1)
            current_text = [regex_match.group(2)]
        else:
            # Continuation of the current clause
            if current_clause:
                # Remove extra spaces but keep single spaces for join
                current_text.append(line_clean)
                
    # Save the final clause
    if current_clause:
        structured_sections[current_clause] = ' '.join(current_text)
        
    if not structured_sections:
        print("Error: Failed to identify numbered sections in the document.")
        sys.exit(1)
        
    return structured_sections

def summarize_policy(structured_sections: dict) -> str:
    """
    Produces a compliant summary with explicit references, preserving complex multi-condition obligations.
    """
    summary_lines = []
    summary_lines.append("# Human Resources Leave Policy - Compliant Summary\n")
    
    # Strict matching keywords as highlighted by the RICE context
    strict_triggers = ["must", "requires", "will", "forfeited", "not permitted", "cannot", "only after"]
    
    for clause_id, text in structured_sections.items():
        text_lower = text.lower()
        
        # Test if it binds conditions or triggers strict constraints
        is_complex = any(trigger in text_lower for trigger in strict_triggers)
        
        # Additionally enforce multi-condition preservation explicitly
        if "and" in text_lower and ("requires" in text_lower or "approval" in text_lower):
            is_complex = True
            
        summary_lines.append(f"### Clause {clause_id}")
        
        if is_complex:
            summary_lines.append(f"> [FLAG: Complex obligation preserved verbatim to prevent omission or condition drop]")
            summary_lines.append(f"> \"{text}\"\n")
        else:
            # Simple summarization output context
            summary_lines.append(f"- **Summary**: {text}\n")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document .txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()
    
    print(f"Loading policy document from {args.input}...")
    structured_sections = retrieve_policy(args.input)
    
    print("Generating compliant summary...")
    summary = summarize_policy(structured_sections)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Compliant summary written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()
