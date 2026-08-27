import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """Loads a .txt policy file, returns content as structured numbered sections."""
    sections = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_clause = None
    buffer = []
    
    for line in content.split('\n'):
        if "════" in line or not line.strip():
            continue
        
        # Skip top document headers
        if "CITY MUNICIPAL" in line or "HUMAN RESOURCES" in line or "EMPLOYEE LEAVE" in line or "Document Reference" in line or "Version" in line:
            continue
            
        clause_match = re.match(r'^(\d+\.\d+|\d+\.)\s+(.*)', line.strip())
        if clause_match:
            if current_clause is not None:
                sections[current_clause] = " ".join(buffer).strip()
            
            current_clause = clause_match.group(1).strip()
            buffer = [clause_match.group(2).strip()]
        elif current_clause is not None and line.startswith("    "):
            buffer.append(line.strip())
            
    if current_clause is not None:
        sections[current_clause] = " ".join(buffer).strip()
        
    return sections

def summarize_policy(sections: dict) -> str:
    """Takes structured sections, produces compliant summary with clause references."""
    summary_lines = []
    summary_lines.append("COMPLIANT HR LEAVE POLICY SUMMARY")
    summary_lines.append("─────────────────────────────────\n")
    
    for clause, text in sections.items():
        if clause.endswith('.'):
            summary_lines.append(f"\n{clause} {text}")
        else:
            summary_lines.append(f"[{clause}] {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to summary output (.txt)")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Policy successfully summarized and saved to {args.output}")
    except Exception as e:
        print(f"Error processing policy: {e}")

if __name__ == "__main__":
    main()
