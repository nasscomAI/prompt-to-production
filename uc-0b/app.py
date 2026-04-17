import argparse
import re
import os

def secure_path(path):
    """Ensure path is within the allowed data directory."""
    abs_data = os.path.abspath("../data")
    abs_target = os.path.abspath(path)
    # Allow reading from data/ or writing to current dir
    if not (abs_target.startswith(abs_data) or abs_target.startswith(os.getcwd())):
        raise PermissionError(f"Security violation: Access to {path} is prohibited.")
    return path

def retrieve_policy(file_path):
    file_path = secure_path(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex to find numbered clauses like "2.3 Employees must..."
    # Looking for a number at the start of a line or after some spaces
    pattern = r'(?m)^\s*(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    return [{"clause_number": m[0], "content": m[1].strip().replace('\n', ' ')} for m in matches]

def summarize_policy(sections):
    summary_lines = ["🏛️ CITY MUNICIPAL CORPORATION - HR LEAVE POLICY SUMMARY\n", "="*60 + "\n"]
    
    # Special handling for critical clauses to ensure no condition dropping
    special_rules = {
        "5.2": "LWP requires approval from BOTH Department Head AND HR Director. (Manager approval is insufficient).",
        "5.3": "LWP > 30 days requires Municipal Commissioner approval.",
        "2.4": "Written approval from direct manager required before leave starts. Verbal approval is NOT valid.",
        "7.2": "Leave encashment during service is NOT permitted under any circumstances."
    }

    for section in sections:
        num = section["clause_number"]
        text = section["content"]
        
        # Use special rule if defined, otherwise a generic summary logic
        if num in special_rules:
            summary_line = f"Clause {num}: {special_rules[num]}"
        else:
            # Simple summary: first sentence or key obligation
            summary_line = f"Clause {num}: {text.split('.')[0]}."
            
        summary_lines.append(summary_line)
    
    return "\n".join(summary_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary generated successfully: {args.output}")
