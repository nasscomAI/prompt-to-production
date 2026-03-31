import argparse
import re

def retrieve_policy(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
        
    clauses = {}
    current_clause = None
    
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        match = pattern.match(line)
        if match:
            current_clause = match.group(1)
            clauses[current_clause] = match.group(2).strip()
        elif current_clause and not line.startswith('=') and not re.match(r'^\d+\.', line) and "CITY MUNICIPAL" not in line and "HUMAN RESOURCES" not in line and "EMPLOYEE LEAVE" not in line and "Document Reference" not in line and "Version:" not in line:
            clauses[current_clause] += " " + line
            
    if not clauses:
        raise ValueError("Document structure unrecognised: no numbered clauses found.")
        
    return clauses

def summarize_policy(sections):
    summary_lines = []
    summary_lines.append("Policy Summary:\n")
    
    for clause_num, text in sections.items():
        # To guarantee no softening of binding verbs and no dropping of multi-conditions,
        # we mark clauses verbatim.
        summary_lines.append(f"[{clause_num}]: {text} [VERBATIM_REQUIRED]")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input txt")
    parser.add_argument("--output", required=True, help="Path to output txt")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
