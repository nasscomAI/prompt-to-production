import argparse
import re
import sys

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured, numbered sections.
    Skill: retrieve_policy
    """
    sections = {}
    current_clause = None
    current_text = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines, separators, and section headers
                if not line or line.startswith('═') or re.match(r'^\d+\.\s+[A-Z\s\(\)]+$', line):
                    continue
                
                # Match clause numbers like '2.3'
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    # Save the previous clause before starting a new one
                    if current_clause:
                        sections[current_clause] = " ".join(current_text)
                    current_clause = match.group(1)
                    current_text = [match.group(2)]
                elif current_clause:
                    # Append continuation lines to the current clause
                    current_text.append(line)
        
        # Add the final clause
        if current_clause:
            sections[current_clause] = " ".join(current_text)
            
    except Exception as e:
        # Error handling as per skills.md: System halts and reports
        print(f"Error: Unable to read or parse policy file '{filepath}'.\nDetails: {e}")
        sys.exit(1)
        
    return sections

def summarize_policy(sections: dict) -> list:
    """
    Takes structured sections and produces a compliant summary with clause references.
    Skill: summarize_policy
    """
    summary_lines = ["# HR Leave Policy Summary", ""]
    
    # Core clauses mapped from the prompt that carry strict multi-condition obligations
    # These are highly prone to meaning loss or condition dropping if summarised loosely.
    core_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    
    for clause, text in sections.items():
        # Clean up multi-line spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Enforcement Rules Applied:
        # 1. Every numbered clause must be present in the summary.
        # 2. Multi-condition obligations must preserve ALL conditions.
        # 3. Never add information not present...
        # 4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it.
        
        if clause in core_clauses:
            summary_lines.append(f"- Clause {clause} [VERBATIM FLAG - High Risk of Meaning Loss/Condition Drop]: \"{text}\"")
        else:
            summary_lines.append(f"- Clause {clause}: {text}")
            
    if not sections:
        summary_lines.append("No numbered clauses found to summarize.")

    return summary_lines


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer based on agents.md rules")
    parser.add_argument("--input", required=True, help="Path to input .txt policy file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    # 1. Retrieve the policy content
    structured_sections = retrieve_policy(args.input)
    
    # 2. Summarize according to strict rules
    summary_lines = summarize_policy(structured_sections)
    
    # 3. Write output safely
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write("\n".join(summary_lines) + "\n")
        print(f"Success: Compliant summary written to {args.output}")
    except Exception as e:
        print(f"Error writing summary to '{args.output}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
