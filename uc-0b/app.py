"""
UC-0B app.py — HR Policy Summarizer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import sys
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Reads the raw policy text file and parses it line-by-line into structured sections.
    Returns: dict mapping clause numbers (e.g. "2.3") to their cleaned text.
    """
    clauses = {}
    current_clause = None
    current_text = []

    # Regex to identify a clause line, e.g. "2.3 Employees must submit..."
    clause_start_re = re.compile(r'^\s*(\d+\.\d+)\s+(.*)$')
    # Regex to identify section dividers or headings to terminate accumulation
    section_divider_re = re.compile(r'^[═════=\-_]{5,}')
    section_heading_re = re.compile(r'^\s*\d+\.\s+[A-Z]')

    with open(input_path, mode="r", encoding="utf-8") as f:
        for line in f:
            line_str = line.rstrip('\n')
            
            # Check if this line starts a new clause
            match = clause_start_re.match(line_str)
            if match:
                # Save previous clause
                if current_clause and current_text:
                    clauses[current_clause] = " ".join(current_text)
                current_clause = match.group(1)
                current_text = [match.group(2).strip()]
            else:
                # Check if we should terminate the current clause
                if current_clause:
                    if section_divider_re.match(line_str) or section_heading_re.match(line_str):
                        clauses[current_clause] = " ".join(current_text)
                        current_clause = None
                        current_text = []
                    else:
                        stripped = line_str.strip()
                        if stripped:
                            current_text.append(stripped)

        # Save the final clause
        if current_clause and current_text:
            clauses[current_clause] = " ".join(current_text)

    # Clean up whitespace
    for clause_num in list(clauses.keys()):
        text = clauses[clause_num]
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        clauses[clause_num] = cleaned_text

    return clauses


def summarize_policy(clauses: dict, output_path: str):
    """
    Extracts the 10 target clauses, formats them verbatim with verification flags,
    and writes them to the output path.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    # Validation: Ensure all target clauses were successfully parsed
    missing_clauses = [num for num in target_clauses if num not in clauses]
    if missing_clauses:
        raise ValueError(f"Failed to parse target clauses: {', '.join(missing_clauses)}")

    summary_lines = []
    for num in target_clauses:
        verbatim_text = clauses[num]
        summary_lines.append(f"Clause {num} [FLAGGED - QUOTED VERBATIM]: {verbatim_text}")

    try:
        with open(output_path, mode="w", encoding="utf-8") as f:
            f.write("\n".join(summary_lines) + "\n")
    except Exception as e:
        print(f"Error writing to output file {output_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summarize_policy(clauses, args.output)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error executing policy summarizer: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
