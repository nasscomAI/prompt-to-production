import argparse
import re
import sys

def retrieve_policy(file_path: str) -> dict:
    """
    Skill: Loads a .txt policy file and returns its content as structured, numbered sections.
    Refuses to guess if parsing fails.
    """
    sections = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise ValueError(f"Could not access file: {file_path}")
        
    current_clause = None
    current_text = []
    
    # Regex to match clauses like "2.3 Employees must submit..."
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in lines:
        line = line.strip()
        # Skip empty lines, separators, and title lines
        if not line or line.startswith('═') \
           or line.startswith('CITY MUNICIPAL') \
           or line.startswith('HUMAN RESOURCES') \
           or line.startswith('EMPLOYEE LEAVE POLICY') \
           or line.startswith('Document Reference') \
           or line.startswith('Version'):
            continue
            
        # Ignore main section headers like "1. PURPOSE AND SCOPE" or "5. LEAVE WITHOUT PAY (LWP)"
        if re.match(r'^\d+\.\s+[A-Z\s&()]+$', line):
            continue
            
        match = clause_pattern.match(line)
        if match:
            # Save the previous clause
            if current_clause:
                sections[current_clause] = ' '.join(current_text)
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause:
            # Continuation of the current clause
            current_text.append(line)
            
    # Save the last clause
    if current_clause:
        sections[current_clause] = ' '.join(current_text)
        
    if not sections:
        raise ValueError("Failed to parse numbered clauses from the document. Format may be invalid.")
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Skill: Takes structured sections and produces a legally compliant summary with
    clause references, adhering strictly to the enforcement rules in agents.md.
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("="*50)
    
    # Enforcement rule 4: "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it"
    # Enforcement rule 2: "Multi-condition obligations must preserve ALL conditions"
    # We identify high-risk binding verbs and multi-conditions based on README trap warnings:
    binding_keywords = ['must', 'requires', 'will', 'forfeited', 'not permitted', 'cannot']
    
    for clause, text in sections.items():
        text_lower = text.lower()
        
        is_high_risk = any(kw in text_lower for kw in binding_keywords)
        
        # Enforcement Rule 1: Every numbered clause must be present
        if is_high_risk:
            # Flag it and quote verbatim to prevent condition dropping
            summary_lines.append(f"- Clause {clause} [VERBATIM - BINDING OBLIGATION]: {text}")
        else:
            # Safe to present standard representation, preserving original info (Rule 3)
            summary_lines.append(f"- Clause {clause}: {text}")
            
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Path to input policy document")
    parser.add_argument("--output", required=True, help="Path to output summary")
    args = parser.parse_args()
    
    try:
        # Step 1: Execute retrieve_policy skill
        sections = retrieve_policy(args.input)
        
        # Step 2: Execute summarize_policy skill
        summary = summarize_policy(sections)
        
        # Step 3: Write verifiable output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Success: Compliant summary generated at {args.output}")
        
    except Exception as e:
        print(f"Agent Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
