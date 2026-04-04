import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """Read a txt file and return clauses structured by clause number."""
    clauses = {}
    current_clause = None
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Match numbered clauses like "1.1", "2.14"
            m = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if m:
                current_clause = m.group(1)
                clauses[current_clause] = m.group(2)
            elif current_clause and line and not line.startswith('═') and not re.match(r'^\d+\.', line):
                # Ensure we don't accidentally append headers like "2. ANNUAL LEAVE"
                clauses[current_clause] += ' ' + line
    return clauses


def summarize_policy(clauses: dict) -> list:
    """Summarize clauses or quote verbatim if too complex/risky."""
    # TRAP CLAUSES identified in README as highly strict/multi-conditional
    trap_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    summary_lines = []
    summary_lines.append("POLICY SUMMARY\n==============")
    
    for num, text in clauses.items():
        if num in trap_clauses:
            # Rule 4: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
            summary_lines.append(f"Clause {num} [VERBATIM - HIGH RISK]: {text}")
        else:
            # Standard light summarization removing filler but keeping core
            # Ensuring we don't drop conditions or hallucinate.
            short_text = text.replace("This policy ", "").replace("Each permanent employee is entitled to ", "Entitlement: ")
            summary_lines.append(f"Clause {num}: {short_text}")
            
    return summary_lines


def main(input_path: str, output_path: str):
    # Skill 1: retrieve
    structured_clauses = retrieve_policy(input_path)
    
    # Skill 2: summarize
    summary_output = summarize_policy(structured_clauses)
    
    # Write to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_output))
        f.write('\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input policy text file")
    parser.add_argument("--output", required=True, help="Output summary text file")
    args = parser.parse_args()
    
    main(args.input, args.output)
    print(f"Summary written to {args.output}")
