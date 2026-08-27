"""
UC-0B app.py — Implemented file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import os

def retrieve_policy(file_path: str) -> dict:
    """
    Loads a plaintext policy file and extracts its content into structured, numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    sections = {}
    current_key = None
    # Matches "X.Y" section pattern at the start of a line
    pattern = re.compile(r"^\s*([0-9]+\.[0-9]+)\s+(.*)")

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.rstrip("\n")
            match = pattern.match(line_str)
            if match:
                current_key = match.group(1)
                sections[current_key] = match.group(2).strip()
            elif current_key is not None:
                # If line starts with whitespace, it's a continuation of the current clause
                if line_str.startswith(" ") or line_str.startswith("\t"):
                    sections[current_key] += " " + line_str.strip()
                elif not line_str.strip():
                    continue
                else:
                    # Non-indented non-empty line resets context (e.g. heading, separator)
                    current_key = None

    # Clean up excess spaces in extracted text
    for k, v in sections.items():
        sections[k] = re.sub(r"\s+", " ", v)

    return sections

def summarize_policy(sections: dict) -> str:
    """
    Process structured policy sections and generate a compliant summary that preserves all
    obligations, conditions, and clause references.
    """
    required_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    # Enforcement check: Verify that every required numbered clause is present in the sections
    missing_clauses = [clause for clause in required_clauses if clause not in sections]
    if missing_clauses:
        raise ValueError(f"Missing required policy clauses: {', '.join(missing_clauses)}")

    summary_lines = [
        "CMC EMPLOYEE LEAVE POLICY SUMMARY",
        "=================================",
        ""
    ]

    # Rule 1 & 2: Process each required clause, preserving all conditions and binding obligations.
    # Clause 2.3
    summary_lines.append(f"Clause 2.3: {sections['2.3']}")
    
    # Clause 2.4
    summary_lines.append(f"Clause 2.4: {sections['2.4']}")
    
    # Clause 2.5
    summary_lines.append(f"Clause 2.5: {sections['2.5']}")
    
    # Clause 2.6
    summary_lines.append(f"Clause 2.6: {sections['2.6']}")
    
    # Clause 2.7
    summary_lines.append(f"Clause 2.7: {sections['2.7']}")
    
    # Clause 3.2
    summary_lines.append(f"Clause 3.2: {sections['3.2']}")
    
    # Clause 3.4
    summary_lines.append(f"Clause 3.4: {sections['3.4']}")
    
    # Clause 5.2 (Multi-condition obligation: must check and preserve Department Head and HR Director)
    raw_5_2 = sections['5.2']
    if "Department Head" not in raw_5_2 or "HR Director" not in raw_5_2:
         raise ValueError("Clause 5.2: Multi-condition obligation has been corrupted or conditions dropped.")
    summary_lines.append(f"Clause 5.2: {raw_5_2}")
    
    # Clause 5.3
    summary_lines.append(f"Clause 5.3: {sections['5.3']}")
    
    # Clause 7.2 (Quote verbatim and flag, as it cannot be summarized without risk of losing its absolute restriction)
    raw_7_2 = sections['7.2']
    summary_lines.append(f"Clause 7.2 [VERBATIM]: {raw_7_2}")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarization Tool")
    parser.add_argument("--input", required=True, help="Path to input HR policy text file")
    parser.add_argument("--output", required=True, help="Path to write the compliant summary")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        # Ensure the output directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            f.write("\n")
        print(f"Summary successfully written to {args.output}")

    except Exception as e:
        print(f"Error executing UC-0B summarizer: {e}")
        exit(1)

if __name__ == "__main__":
    main()
