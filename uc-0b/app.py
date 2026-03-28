import argparse
import re

MANDATORY_CLAUSES = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']

def retrieve_policy(filepath: str) -> dict:
    """Reads the raw HR leave policy document and returns its contents structured into numbered sections."""
    sections = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_clause = None
    current_text = []
    
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in content.split('\n'):
        # Just use strip() to handle weird spacing but keep line contents
        line_stripped = line.strip()
        
        # Skip empty lines or decorative lines
        if not line_stripped or line_stripped.startswith('═'):
            continue
            
        # Check if line looks like "1. PURPOSE AND SCOPE"
        if re.match(r'^\d+\.\s+[A-Z\s]+$', line_stripped):
            # It's a header like "3. SICK LEAVE", not a clause like "3.1"
            continue
            
        match = clause_pattern.match(line_stripped)
        if match:
            # We found a new clause like "2.3"
            if current_clause:
                sections[current_clause] = ' '.join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause:
            # Continuation of the current clause
            current_text.append(line_stripped)
            
    # Save the last one
    if current_clause:
        sections[current_clause] = ' '.join(current_text).strip()
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Analyzes structured policy sections and produces a compliant summary containing all mandatory clauses,
    ensuring no conditions are lost or external scope is injected.
    """
    summary_lines = [
        "HR LEAVE POLICY - STRICT COMPLIANCE SUMMARY",
        "===========================================\n",
        "The following represents the binding obligations extracted strictly verbatim to avoid condition drop:",
        ""
    ]
    
    for clause_id in MANDATORY_CLAUSES:
        if clause_id in sections:
            text = sections[clause_id]
            # Since summarizing accurately without losing terms like "Department Head AND HR Director" 
            # is complex without LLMs, we append [VERBATIM] as required by rule 4 in our plan.
            summary_lines.append(f"[{clause_id}] {text} [VERBATIM]\n")
        else:
            summary_lines.append(f"[{clause_id}] MISSING IN SOURCE TEXT!\n")
            
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Summary successfully extracted and saved to {args.output}")

if __name__ == "__main__":
    main()
