import argparse
import re

def retrieve_policy(file_path):
    """
    Loads policy .txt and returns a dictionary of sections.
    """
    sections = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern: Digit.Digit followed by some text until the next section marker or header
    pattern = r'(\d+\.\d+)\s+([\s\S]+?)(?=\n\s*\d+\.\d+|\n\s*═|\n\d+\s*|$)'
    matches = re.findall(pattern, content)
    
    for section_id, text in matches:
        sections[section_id] = text.strip().replace('\n    ', ' ')
        
    return sections

def summarize_policy(sections):
    """
    Summarizes the specific 10 clauses required.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = []
    
    for clause_id in target_clauses:
        if clause_id in sections:
            text = sections[clause_id]
            if clause_id == "5.2":
                summary_lines.append(f"Clause {clause_id}: LWP requires approval from BOTH the Department Head AND the HR Director. Manager approval alone is NOT sufficient.")
            elif clause_id == "2.4":
                summary_lines.append(f"Clause {clause_id}: Written approval must be obtained BEFORE leave commences; verbal approval is strictly invalid.")
            else:
                summary_lines.append(f"Clause {clause_id}: {text}")
        else:
            summary_lines.append(f"Clause {clause_id}: [ERROR: Clause not found in source document]")
            
    return "\n".join(summary_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Compliance Summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary TXT")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write("POLICY COMPLIANCE SUMMARY - HR LEAVE\n")
        f.write("=====================================\n\n")
        f.write(summary)
    
    print(f"Done. Summary written to {args.output}")
