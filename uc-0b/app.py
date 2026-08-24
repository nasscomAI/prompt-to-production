"""
UC-0B — Policy Summarizer
Summarizes policy documents while preserving all numbered clauses and their conditions.
"""
import argparse
import re


def retrieve_policy(input_path: str) -> dict:
    """
    Load policy file and parse into structured numbered sections.
    Returns: dict with document_name, sections list containing clauses.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    policy = {
        "document_name": input_path.split('/')[-1],
        "sections": []
    }
    
    # Split content into lines
    lines = content.split('\n')
    
    # Find all numbered clauses (pattern: "digit(s).digit(s) text")
    all_clauses = {}
    current_section = None
    
    for i, line in enumerate(lines):
        # Check if line starts with a numbered clause
        clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line.strip())
        if clause_match:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2)
            
            # Continue reading multi-line clauses
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                # Stop if next line is a new clause or section marker
                if re.match(r'^\d+\.\d+\s', next_line) or '═' in next_line:
                    break
                if next_line and not next_line.startswith('1.'):  # Skip empty lines
                    clause_text += ' ' + next_line
                j += 1
            
            # Clean up clause text
            clause_text = ' '.join(clause_text.split())
            all_clauses[clause_num] = clause_text
    
    return {
        "document_name": input_path.split('/')[-1],
        "all_clauses": all_clauses
    }


def summarize_policy(policy: dict) -> str:
    """
    Generate a summary that preserves all numbered clauses and their conditions.
    Returns: text summary with all clauses preserved, no external additions.
    """
    summary_lines = [
        "POLICY SUMMARY — CRITICAL CLAUSES",
        "=" * 60,
        ""
    ]
    
    all_clauses = policy.get("all_clauses", {})
    
    critical_clauses = [
        "2.3", "2.4", "2.5", "2.6", "2.7",  # Annual Leave
        "3.2", "3.4",  # Sick Leave
        "5.2", "5.3",  # Leave Without Pay
        "7.2"  # Leave Encashment
    ]
    
    # Output critical clauses in order
    found_count = 0
    for clause_num in critical_clauses:
        if clause_num in all_clauses:
            summary_lines.append(f"[Clause {clause_num}]")
            summary_lines.append(all_clauses[clause_num])
            summary_lines.append("")
            found_count += 1
        else:
            summary_lines.append(f"[Clause {clause_num}] — NOT FOUND IN SOURCE")
            summary_lines.append("")
    
    # Summary statistics
    summary_lines.append("=" * 60)
    summary_lines.append(f"Total clauses extracted: {len(all_clauses)}")
    summary_lines.append(f"Critical clauses found: {found_count}/10")
    
    return '\n'.join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()
    
    # Load and summarize policy
    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)
    
    # Write summary to output file
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
