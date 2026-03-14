"""
UC-0B app.py
Reads a policy document and writes a clause-preserving summary.
"""

import argparse
import re


def retrieve_policy(file_path):
    """Load policy text"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_clauses(text):
    """
    Extract numbered clauses like 2.3, 2.4 etc.
    """
    pattern = r"(\d+\.\d+)\s+(.*)"
    clauses = re.findall(pattern, text)

    clause_dict = {}
    for number, content in clauses:
        clause_dict[number] = content.strip()

    return clause_dict


def summarize_policy(clauses):
    """
    Create a clause-by-clause summary without dropping conditions.
    """
    summary_lines = []

    for clause_num, content in clauses.items():
        summary_lines.append(f"Clause {clause_num}")
        summary_lines.append(content)
        summary_lines.append("")

    return "\n".join(summary_lines)


def write_output(output_path, summary):
    """Write summary to file"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Policy input file")
    parser.add_argument("--output", required=True, help="Summary output file")

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)
    clauses = extract_clauses(policy_text)
    summary = summarize_policy(clauses)

    write_output(args.output, summary)

    print("Summary generated successfully.")


if __name__ == "__main__":
    main()