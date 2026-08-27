import argparse
import os
import re

def retrieve_policy(file_path: str):
    """Loads .txt policy file, returns content as structured numbered sections"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Could not find policy file at {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    sections = {}
    # Extracting numbered clauses (e.g., "2.3", "5.2") to ensure none are missed
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Check if line starts with a number like 2.3
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            sections[match.group(1)] = line
        else:
            sections[f"text_{len(sections)}"] = line
            
    return sections if sections else [line for line in content.split('\n') if line.strip()]

def summarize_policy(structured_sections):
    """Takes structured sections, produces compliant summary with clause references"""
    summary = ["HR LEAVE POLICY SUMMARY", "="*30]
    
    if isinstance(structured_sections, dict):
        for key, text in structured_sections.items():
            # Apply enforcement rules: If it has complex conditions, quote it verbatim
            if re.match(r'^\d+\.\d+', key):
                lower_text = text.lower()
                if "and" in lower_text or "requires" in lower_text or "must" in lower_text or "forfeited" in lower_text:
                    summary.append(f"[VERBATIM] {text}")
                else:
                    summary.append(f"[SUMMARY] {text}")
            else:
                summary.append(text)
    else:
        summary.extend(structured_sections)
        
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Document Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()
    
    print(f"Reading policy from {args.input}...")
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Success! Compliant summary written to {args.output}")
    except Exception as e:
        print(f"Execution failed: {e}")

if __name__ == "__main__":
    main()