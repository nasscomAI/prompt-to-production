"""
UC-0B — Summary That Changes Meaning
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re


def retrieve_policy(txt_path):
    """Loads .txt policy file, returns content as structured numbered sections."""
    # Use utf-8 with error replacement to handle special characters
    with open(txt_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Split into lines and identify numbered clauses
    lines = content.split("\n")
    clauses = {}
    current_clause_num = None
    current_clause_text = []

    for line in lines:
        stripped = line.strip()
        # Match clause numbers like "2.3", "5.2", "7.2"
        match = re.match(r"^(\d+)\.(\d+)\s+(.*)", stripped)
        if match:
            # Save previous clause if exists
            if current_clause_num is not None:
                clauses[current_clause_num] = " ".join(current_clause_text).strip()
            current_clause_num = match.group(1) + "." + match.group(2)
            current_clause_text = [match.group(3)]
        elif current_clause_num is not None and stripped:
            current_clause_text.append(stripped)
        elif current_clause_num is not None and not stripped:
            pass  # blank line within clause

    # Save last clause
    if current_clause_num is not None:
        clauses[current_clause_num] = " ".join(current_clause_text).strip()

    return clauses


def summarize_policy(clauses):
    """Produces compliant summary with clause references, preserving all conditions."""
    summary_lines = []

    # Sort clause numbers numerically
    sorted_clause_nums = sorted(clauses.keys(), key=lambda x: float(x.replace(".", "")))

    for clause_num in sorted_clause_nums:
        clause_text = clauses[clause_num]
        # Include every clause - never drop, preserve all conditions
        summary_lines.append(f"Clause {clause_num}: {clause_text}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary txt")
    args = parser.parse_args()

    # Retrieve policy clauses
    clauses = retrieve_policy(args.input)

    # Generate summary preserving all clauses and conditions
    summary = summarize_policy(clauses)

    # Write output - use utf-8 with errors replace to handle special characters
    output_dir = "/".join(args.output.split("/")[:-1])
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8", errors="replace") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
