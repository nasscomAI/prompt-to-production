import argparse
import re
import os
import sys

CLAUSE_PATTERNS = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2"
]

def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError("Input policy file is empty.")

    return content


def extract_clause(content, clause_number):
    pattern = rf"({re.escape(clause_number)}\s+.*?)(?=\n\d+\.\d+|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def summarize_clause(clause_number, clause_text):
    if not clause_text:
        return f"{clause_number}: [MISSING CLAUSE - review required]"

    # For sensitive clauses where meaning must be preserved, quote verbatim
    critical_clauses = ["2.4", "2.5", "5.2", "5.3", "7.2"]
    if clause_number in critical_clauses:
        return f"{clause_number}: {clause_text} [VERBATIM]"

    # Otherwise preserve clause closely
    return f"{clause_number}: {clause_text}"


def summarize_policy(content):
    summary_lines = []
    missing = []

    for clause in CLAUSE_PATTERNS:
        clause_text = extract_clause(content, clause)
        if clause_text is None:
            missing.append(clause)
        summary_lines.append(summarize_clause(clause, clause_text))

    if missing:
        summary_lines.append("")
        summary_lines.append("FLAG: The following required clauses were not found in the source document:")
        for m in missing:
            summary_lines.append(f"- {m}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="HR Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()

    try:
        policy_text = retrieve_policy(args.input)
        summary = summarize_policy(policy_text)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"Summary generated successfully: {args.output}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()