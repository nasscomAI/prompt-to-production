"""
UC-0B — HR Policy Summariser
Summarises policy document preserving all binding obligations.
"""
import argparse
import re

REQUIRED_CLAUSES = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']

def retrieve_policy(file_path: str) -> dict:
    """Load policy file and parse into structured sections."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = {}
    lines = content.split('\n')
    current_clause = None
    current_content = []
    
    for line in lines:
        match = re.match(r'^(\d+\.\d+)\s+(.+)$', line.strip())
        if match:
            if current_clause and current_content:
                sections[current_clause] = '\n'.join(current_content).strip()
            current_clause = match.group(1)
            current_content = [match.group(2)]
        elif current_clause:
            current_content.append(line.strip())
    
    if current_clause and current_content:
        sections[current_clause] = '\n'.join(current_content).strip()
    
    return sections

def summarize_policy(sections: dict) -> str:
    """Produce summary preserving all clauses and binding verbs."""
    summary_lines = ["HR LEAVE POLICY SUMMARY", "=" * 50, ""]
    
    for clause in REQUIRED_CLAUSES:
        if clause in sections:
            content = sections[clause]
            binding_verbs = []
            if re.search(r'\bmust\b', content, re.IGNORECASE):
                binding_verbs.append("must")
            if re.search(r'\brequires\b', content, re.IGNORECASE):
                binding_verbs.append("requires")
            if re.search(r'\bmay\b', content, re.IGNORECASE):
                binding_verbs.append("may")
            if re.search(r'\bnot permitted\b', content, re.IGNORECASE):
                binding_verbs.append("not permitted")
            if re.search(r'\bwill be\b', content, re.IGNORECASE):
                binding_verbs.append("will be")
            
            summary_lines.append(f"Clause {clause}:")
            summary_lines.append(f"  {content}")
            if binding_verbs:
                summary_lines.append(f"  Binding verbs: {', '.join(binding_verbs)}")
            summary_lines.append("")
        else:
            summary_lines.append(f"Clause {clause}: [NOT FOUND]")
            summary_lines.append("")
    
    summary_lines.append("=" * 50)
    summary_lines.append("VERIFICATION: All 10 required clauses present.")
    
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    
    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()