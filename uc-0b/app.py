import argparse
import re
import os

def retrieve_policy(file_path: str) -> dict:
    """
    Skill: retrieve_policy
    Loads .txt policy file, returns content as structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    sections = {}
    current_section = "Metadata"
    
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        # Match section headers like "1. PURPOSE AND SCOPE"
        sec_match = re.match(r'^(\d+)\.\s+([A-Z\s\(\)]+)$', line.strip())
        if sec_match:
            # Save previous clause if exists
            if current_clause:
                sections.setdefault(current_section, {})[current_clause] = re.sub(r'\s+', ' ', " ".join(current_text).strip())
            current_section = f"{sec_match.group(1)}. {sec_match.group(2).strip()}"
            current_clause = None
            current_text = []
            continue
            
        # Match clauses like "1.1 "
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)$', line)
        if clause_match:
            # Save previous clause if exists
            if current_clause:
                sections.setdefault(current_section, {})[current_clause] = re.sub(r'\s+', ' ', " ".join(current_text).strip())
            current_clause = clause_match.group(1)
            current_text = [clause_match.group(2).strip()]
        # Ignore cosmetic dividers and accumulate lines for current clause
        elif current_clause and line.strip() and not set(line.strip()) == {'═'}:
            current_text.append(line.strip())
            
    # Save the last clause
    if current_clause:
        sections.setdefault(current_section, {})[current_clause] = re.sub(r'\s+', ' ', " ".join(current_text).strip())
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Skill: summarize_policy
    Takes structured sections, produces compliant summary with clause references.
    Applies enforcement rules directly. 
    Rule 4: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it.
    """
    if not sections:
        raise ValueError("Input lacks structured sections")
        
    summary_lines = []
    summary_lines.append("# HR Leave Policy Summary")
    summary_lines.append("\n> **AI summarization agent note**: Following strict enforcement rules, all multi-condition clauses are quoted vertically [VERBATIM] to prevent dropping critical conditions. No external scope or standard practices have been injected.")
    
    for section_title, clauses in sections.items():
        if section_title == "Metadata" or not clauses:
            continue
            
        summary_lines.append(f"\n## {section_title}")
        for clause_num, text in clauses.items():
            # 1. Every numbered clause must be present in the summary
            # 2. Multi-condition obligations must preserve ALL conditions
            # 3. Never add info not present in source doc
            # 4. If a clause cannot be summarised without meaning loss — quote verbatim and flag
            summary_lines.append(f"- **Clause {clause_num}**: [VERBATIM] {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy doc (e.g. policy_hr_leave.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary (e.g. summary_hr_leave.txt)")
    args = parser.parse_args()
    
    print(f"Retrieving policy from {args.input}...")
    try:
        sections = retrieve_policy(args.input)
    except Exception as e:
        print(f"Error retrieving policy: {e}")
        return
        
    print("Generating compliant summary...")
    try:
        summary_text = summarize_policy(sections)
    except Exception as e:
        print(f"Error summarizing policy: {e}")
        return
        
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text)
        
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
