"""
UC-0B Policy Summarizer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import re

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a policy text file and parses it into structured sections and clauses.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found at {file_path}")
        
    clauses = {}
    current_clause_num = None
    current_clause_lines = []
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # Match lines starting with a clause number like "2.3 " or "5.2 "
            match = re.match(r"^(\d+\.\d+)\s+(.*)", stripped)
            if match:
                if current_clause_num:
                    clauses[current_clause_num] = " ".join(current_clause_lines).strip()
                current_clause_num = match.group(1)
                current_clause_lines = [match.group(2)]
            elif current_clause_num:
                # If we encounter section divider lines or a main section number like "2. ", stop appending
                if not stripped or "═══" in stripped or re.match(r"^\d+\.\s+", stripped):
                    clauses[current_clause_num] = " ".join(current_clause_lines).strip()
                    current_clause_num = None
                    current_clause_lines = []
                else:
                    current_clause_lines.append(stripped)
                    
        if current_clause_num:
            clauses[current_clause_num] = " ".join(current_clause_lines).strip()
            
    return clauses


def summarize_policy(clauses: dict) -> str:
    """
    Compiles a summary of the policy document, ensuring all critical clauses
    are accounted for and no conditions are softened.
    """
    # Verify presence of all required clauses
    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        raise ValueError(f"Missing required clauses for summarization: {', '.join(missing)}")
        
    summary_lines = [
        "EMPLOYEE LEAVE POLICY SUMMARY (HR-POL-001)",
        "=========================================",
        "This summary covers the key binding clauses and obligations in the Employee Leave Policy.",
        "Under the policy's enforcement rules, to prevent any meaning loss or condition softening,",
        "critical clauses are cited verbatim below.",
        ""
    ]
    
    for clause_num in REQUIRED_CLAUSES:
        clause_text = clauses[clause_num]
        summary_lines.append(f"Clause {clause_num} [FLAG: VERBATIM]:")
        summary_lines.append(f"  \"{clause_text}\"")
        summary_lines.append("")
        
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()
    
    print(f"Retrieving policy from {args.input}...")
    clauses = retrieve_policy(args.input)
    
    print("Generating summary...")
    summary = summarize_policy(clauses)
    
    # Write to output file
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
        
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
