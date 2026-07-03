"""
UC-0B app.py — HR Leave Policy Summarizer
"""
import argparse
import re

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a plain text policy file and extracts structured numbered sections and clauses.
    Returns: dict mapping clause numbers (e.g. '2.3') to their exact text.
    """
    clauses = {}
    current_clause = None
    current_text = []
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        stripped = line.strip()
        # Match a clause number at the start, e.g., "2.3 " or "2.3\t"
        match = re.match(r'^(\d+\.\d+)\s+(.*)', stripped)
        if match:
            # Save the previous clause if any
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause is not None:
            # Check if this is a divider line or section header
            if stripped.startswith("══") or stripped.startswith("════") or re.match(r'^\d+\.\s+[A-Z]+', stripped):
                clauses[current_clause] = " ".join(current_text).strip()
                current_clause = None
                current_text = []
            elif stripped == "":
                # Keep current clause going, but ignore double whitespace line
                pass
            else:
                current_text.append(stripped)
                
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    return clauses


def summarize_policy(clauses: dict) -> str:
    """
    Takes structured clauses and produces a compliant summary preserving all binding constraints.
    """
    target_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    summary_lines = [
        "═══════════════════════════════════════════════════════════",
        "CMC LEAVE POLICY SUMMARY — BINDING OBLIGATIONS",
        "═══════════════════════════════════════════════════════════\n"
    ]
    
    for num in target_clauses:
        if num not in clauses:
            raise ValueError(f"Required critical clause {num} is missing from the source document.")
        
        clause_text = clauses[num]
        
        # Rule 4: Legal obligations cannot be compressed without meaning loss.
        # We quote them verbatim and flag them with [VERBATIM] to ensure 100% compliance.
        summary_lines.append(f"Clause {num} [VERBATIM]:")
        summary_lines.append(f"  {clause_text}\n")
        
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary TXT")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, "w", encoding="utf-8") as out_file:
            out_file.write(summary)
            
        print(f"Summary successfully written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
