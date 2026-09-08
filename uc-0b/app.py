import argparse
import re

def retrieve_policy(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    clauses = {}
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\n═|\Z)', re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(content):
        clause_id = match.group(1)
        clause_text = match.group(2).strip()
        clause_text = re.sub(r'\s+', ' ', clause_text)
        clauses[clause_id] = clause_text
        
    return clauses

def summarize_policy(clauses):
    summary_lines = []
    for clause_id, text in clauses.items():
        # Using VERBATIM since rule-based summarization can't safely compress without meaning loss
        summary_lines.append(f"{clause_id} [VERBATIM] {text}")
    return summary_lines

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summary_lines = summarize_policy(clauses)
    
    key_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    present_clauses = []
    missing_clauses = []
    
    for kc in key_clauses:
        if kc in clauses:
            present_clauses.append(kc)
        else:
            missing_clauses.append(kc)
            
    with open(args.output, 'w') as f:
        for line in summary_lines:
            f.write(line + "\n")
            
        f.write("\n--- VERIFICATION ---\n")
        f.write("Critical Clauses Present:\n")
        for pc in present_clauses:
            f.write(f"- {pc}\n")
            
        if missing_clauses:
            f.write("Critical Clauses Missing:\n")
            for mc in missing_clauses:
                f.write(f"- {mc}\n")
        else:
            f.write("All critical clauses are present.\n")

if __name__ == '__main__':
    main()
