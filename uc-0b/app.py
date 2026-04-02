"""
UC-0B app.py — Policy Summary Generator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def is_clause_header(line: str) -> bool:
    """Check if line is a numbered clause (e.g., 2.3, 5.2)."""
    if not line or not line[0].isdigit():
        return False
    parts = line.split()
    if not parts:
        return False
    first = parts[0]
    if '.' in first:
        section_part = first.split('.')
        return len(section_part) == 2 and section_part[0].isdigit() and section_part[1].isdigit()
    return False

def summarize_policy(input_path: str, output_path: str):
    """
    Read the policy document, generate a summary preserving all clauses without changing meaning.
    Must preserve all numbered clauses and multi-condition obligations intact.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Extract all numbered clauses and their full text
        summary_lines = []
        capture_clause = False
        
        for line in lines:
            stripped = line.strip()
            
            # Start capturing at a clause header
            if is_clause_header(stripped):
                capture_clause = True
                summary_lines.append(line.rstrip())
            # Continue capturing indented content or non-empty continuing lines
            elif capture_clause and stripped and not stripped.startswith('═'):
                summary_lines.append(line.rstrip())
            # Stop at section headers or empty lines after clause content
            elif stripped.startswith('═') or (capture_clause and not stripped):
                capture_clause = False
        
        # Write summary preserving all clauses
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        
        clause_count = sum(1 for line in summary_lines if is_clause_header(line.strip()))
        print(f"Summary written to {output_path} ({clause_count} clauses)")
    except FileNotFoundError:
        print(f"Input file {input_path} not found.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    summarize_policy(args.input, args.output)

if __name__ == "__main__":
    main()
