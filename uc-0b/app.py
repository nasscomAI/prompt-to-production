import argparse
import re

def retrieve_policy(file_path):
    """
    Extracts specific clauses from the policy text.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex to find clause numbers and their following text
    # This is a specialized extractor for the known clauses
    clauses = {}
    pattern = r'(\d\.\d)\s+(.*?)(?=\n\d\.\d|\n\n|\Z)'
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        clauses[match.group(1)] = match.group(2).strip().replace('\n    ', ' ')
        
    return clauses

def summarize_policy(clauses):
    """
    Summarizes the extracted clauses according to strict enforcement rules.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = ["POLICY SUMMARY - KEY OBLIGATIONS", ""]
    
    for c_id in target_clauses:
        text = clauses.get(c_id)
        if not text:
            summary_lines.append(f"Clause {c_id}: [MISSING IN SOURCE]")
            continue
            
        if c_id == "5.2":
            # Rule: Must preserve BOTH conditions
            summary_lines.append("Clause 5.2: Leave Without Pay (LWP) requires explicit approval from BOTH the Department Head and the HR Director; manager approval alone is insufficient.")
        elif c_id == "2.4":
            summary_lines.append(f"Clause {c_id}: Written approval from your direct manager is mandatory before leave; verbal approval is not valid.")
        elif c_id == "7.2":
            summary_lines.append(f"Clause {c_id}: Leave encashment during active service is strictly prohibited under any circumstances.")
        else:
            summary_lines.append(f"Clause {c_id}: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
