import argparse
import re

def retrieve_policy(input_path: str) -> dict:
    sections = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex to find "X.Y [text]"
    matches = re.finditer(r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z|\n═)', content, re.MULTILINE | re.DOTALL)
    for m in matches:
        sections[m.group(1)] = m.group(2).strip().replace('\n', ' ')
    
    return sections

def summarize_policy(sections: dict) -> str:
    required_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    for clause in required_clauses:
        if clause in sections:
            # We quote verbatim to avoid meaning loss and preserve conditions completely
            text = sections[clause]
            # remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            summary_lines.append(f"Clause {clause}: {text} [VERBATIM]")
        else:
            summary_lines.append(f"Clause {clause}: MISSING")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
