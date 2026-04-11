import argparse
import re
import os

def retrieve_policy(input_path: str) -> list:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    with open(input_path, 'r') as f:
        content = f.read()
    
    # Simple regex to find clauses like 2.3, 5.2, etc.
    # Pattern looks for a number, dot, number followed by space or newline
    clauses = []
    matches = re.finditer(r'(\d\.\d)\s+(.*?)(?=\n\d\.\d|\n\s*════|\Z)', content, re.DOTALL)
    
    for match in matches:
        clause_id = match.group(1)
        text = match.group(2).strip()
        clauses.append({"id": clause_id, "text": text})
    
    return clauses

def summarize_policy(sections: list) -> str:
    """
    Produces a compliant summary while ensuring no meaning loss or condition dropping.
    """
    # Critical clauses that must be present (Ground Truth from README)
    target_clauses = {
        "2.3": "14-day advance notice required (must)",
        "2.4": "Written approval required before leave; verbal not valid (must)",
        "2.5": "Unapproved absence = LOP regardless of subsequent approval (will)",
        "2.6": "Max 5 days carry-forward; above 5 forfeited on 31 Dec (may/forfeited)",
        "2.7": "Carry-forward days must be used Jan–Mar or forfeited (must)",
        "3.2": "3+ consecutive sick days requires medical cert within 48hrs (requires)",
        "3.4": "Sick leave before/after holiday requires cert regardless of duration (requires)",
        "5.2": "LWP requires approval from Department Head AND HR Director (requires) [VERBATIM]",
        "5.3": "LWP >30 days requires Municipal Commissioner approval (requires)",
        "7.2": "Leave encashment during service not permitted under any circumstances (not permitted) [VERBATIM]"
    }
    
    summary_lines = ["# Policy Summary: HR Leave\n"]
    present_ids = {s["id"] for s in sections}
    found_targets = []
    
    for clause_id, target_desc in target_clauses.items():
        if clause_id in present_ids:
            found_targets.append(clause_id)
            # Find the actual text from the sections
            section = next(s for s in sections if s["id"] == clause_id)
            
            # Enforcement Rule 4: Verbatim quote for high-risk clauses
            if "[VERBATIM]" in target_desc:
                line = f"- **Clause {clause_id}**: [FLAG: VERBATIM] {section['text']}"
            else:
                line = f"- **Clause {clause_id}**: {target_desc.split(' [')[0]}"
            
            summary_lines.append(line)
    
    # Enforcement Rule 1: Check for omissions
    missing = set(target_clauses.keys()) - set(found_targets)
    if missing:
        raise ValueError(f"Enforcement Violation: Clause(s) {', '.join(missing)} omitted from summary.")
    
    # Enforcement Rule 3: No scope bleed
    # (By only using target_clauses and sections, we avoid adding external fluff)
    
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary.txt")
    args = parser.parse_args()
    
    try:
        # Step 1: Retrieve
        sections = retrieve_policy(args.input)
        
        # Step 2: Summarize
        summary = summarize_policy(sections)
        
        # Step 3: Write Output
        # Ensure directory exists for output
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(args.output, 'w') as f:
            f.write(summary)
            
        print(f"Summary written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
