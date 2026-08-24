"""
UC-0B app.py — Precise Policy Summarizer
Performs deterministic policy clause extraction and formats a structured summary,
preserving all binding verbs and multiple conditions without scope bleed or information loss.
"""
import argparse
import os
import re
from typing import Dict

TARGET_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

def retrieve_policy(file_path: str) -> Dict[str, str]:
    """
    Loads a policy text file and parses it into structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Standardize line endings and clean formatting
    lines = content.splitlines()
    
    parsed_clauses = {}
    current_clause_num = None
    current_clause_text = []

    # Regex to match clause numbers (e.g. 2.1, 5.12)
    clause_start_pat = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    section_header_pat = re.compile(r"^\s*\d+\.\s+.*$")

    for line in lines:
        match = clause_start_pat.match(line)
        if match:
            # If we were already collecting a clause, save it
            if current_clause_num:
                parsed_clauses[current_clause_num] = " ".join(current_clause_text).strip()
            current_clause_num = match.group(1)
            current_clause_text = [match.group(2).strip()]
        elif section_header_pat.match(line):
            if current_clause_num:
                parsed_clauses[current_clause_num] = " ".join(current_clause_text).strip()
            current_clause_num = None
            current_clause_text = []
        else:
            # Check if this is a header or page decoration line
            if line.strip() and not line.strip().startswith("══") and current_clause_num:
                current_clause_text.append(line.strip())

    # Save the last clause
    if current_clause_num:
        parsed_clauses[current_clause_num] = " ".join(current_clause_text).strip()

    # Clean double spaces and line wraps from clause texts
    for k in parsed_clauses:
        parsed_clauses[k] = re.sub(r"\s+", " ", parsed_clauses[k])

    return parsed_clauses

def summarize_policy(clauses: Dict[str, str]) -> str:
    """
    Constructs a compliant, high-fidelity summary.
    Quotes critical clauses verbatim to guarantee zero meaning loss and no condition dropping.
    """
    summary_lines = [
        "CMC EMPLOYEE LEAVE POLICY - HIGH-FIDELITY COMPLIANCE SUMMARY",
        "===========================================================",
        "This summary presents critical employee obligations and rules exactly as defined",
        "in HR-POL-001. All binding terms, multiple approval conditions, and strict timelines",
        "are preserved verbatim to prevent misinterpretation.",
        "",
        "SECTION 2: ANNUAL LEAVE OBLIGATIONS",
        "------------------------------------",
    ]

    # Annual Leave clauses: 2.3, 2.4, 2.5, 2.6, 2.7
    for num in ["2.3", "2.4", "2.5", "2.6", "2.7"]:
        text = clauses.get(num, "[Clause Not Found in Policy Source]")
        summary_lines.append(f"Clause {num}: [VERBATIM] {text}")

    summary_lines.extend([
        "",
        "SECTION 3: SICK LEAVE OBLIGATIONS",
        "---------------------------------",
    ])

    # Sick Leave clauses: 3.2, 3.4
    for num in ["3.2", "3.4"]:
        text = clauses.get(num, "[Clause Not Found in Policy Source]")
        summary_lines.append(f"Clause {num}: [VERBATIM] {text}")

    summary_lines.extend([
        "",
        "SECTION 5: LEAVE WITHOUT PAY (LWP) CONDITIONS",
        "---------------------------------------------",
    ])

    # LWP clauses: 5.2, 5.3
    for num in ["5.2", "5.3"]:
        text = clauses.get(num, "[Clause Not Found in Policy Source]")
        summary_lines.append(f"Clause {num}: [VERBATIM] {text}")

    summary_lines.extend([
        "",
        "SECTION 7: LEAVE ENCASHMENT RESTRICTIONS",
        "----------------------------------------",
    ])

    # Encashment clause: 7.2
    text = clauses.get("7.2", "[Clause Not Found in Policy Source]")
    summary_lines.append(f"Clause 7.2: [VERBATIM] {text}")

    summary_lines.append("")
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    # Step 1: Retrieve and parse policy document
    parsed_clauses = retrieve_policy(args.input)

    # Step 2: Generate high-fidelity summary
    summary_text = summarize_policy(parsed_clauses)

    # Step 3: Write summary text to destination
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as out_file:
        out_file.write(summary_text)

    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
