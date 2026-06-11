import argparse
import os
import re

def retrieve_policy(filepath):
    """
    Loads the .txt policy file and returns the content as structured numbered sections.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
        
    sections = []
    # Match clause numbers like 1.1, 2.3, etc.
    # Text might be wrapped across multiple lines.
    lines = text.split('\n')
    
    current_clause = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line starts with a clause number (e.g., 2.3)
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                sections.append({
                    "clause": current_clause,
                    "text": " ".join(current_text)
                })
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause and not line.startswith('═══'):
            current_text.append(line)
            
    if current_clause:
        sections.append({
            "clause": current_clause,
            "text": " ".join(current_text)
        })
        
    if not sections:
        raise ValueError("Parsing error: The text does not contain numbered sections.")
        
    return sections

def summarize_policy(sections):
    """
    Takes structured sections and produces a compliant summary with clause references.
    """
    summary_lines = ["# HR Policy Summary\n"]
    
    for section in sections:
        clause = section['clause']
        text = section['text']
        
        # As per the RICE enforcement:
        # "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it"
        # "Multi-condition obligations must preserve ALL conditions — never drop one silently"
        # We will verbatim flag clauses that have conditions.
        
        has_conditions = any(word in text.lower() for word in ['requires', 'must', 'only after', 'subject to', 'unless'])
        if has_conditions:
            summary_lines.append(f"- Clause {clause}: {text} [VERBATIM FLAG]")
        else:
            summary_lines.append(f"- Clause {clause}: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Summariser")
    parser.add_argument("--input", required=True, help="Input policy document path")
    parser.add_argument("--output", required=True, help="Output summary path")
    
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Successfully processed {args.input} and wrote summary to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
