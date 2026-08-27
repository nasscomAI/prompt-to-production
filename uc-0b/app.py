import argparse
import os
import re
import sys

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

BINDING_VERBS = ["must", "will", "requires", "not permitted", "are forfeited", "may"]

FORBIDDEN_PHRASES = [
    "typically", "generally expected", "standard practice",
    "usually", "commonly", "in most cases"
]


def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        sys.exit(f"Error: File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        sys.exit(f"Error reading file: {e}")

    if not content.strip():
        sys.exit("Error: Policy file is empty.")

    clauses = {}
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        sys.exit("Error: Could not extract numbered clauses.")

    for num, text in matches:
        clauses[num.strip()] = text.strip()

    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        sys.exit(f"Error: Missing required clauses: {missing}")

    return clauses


def preserve_clause_text(clause_num, text):
    original = text.strip()

    # enforce clause 5.2 condition explicitly
    if clause_num == "5.2":
        if not ("department head" in original.lower() and "hr director" in original.lower()):
            return f'{clause_num}: "{original}" [FLAG: POSSIBLE CONDITION LOSS]'
    
    # check binding verb presence
    if not any(verb in original.lower() for verb in BINDING_VERBS):
        return f'{clause_num}: "{original}" [FLAG: VERBATIM DUE TO AMBIGUITY]'

    # return verbatim to avoid meaning loss
    return f"{clause_num}: {original}"


def summarize_policy(clauses):
    # validation
    for c in REQUIRED_CLAUSES:
        if c not in clauses:
            sys.exit(f"Error: Missing clause {c}")

    summary_lines = []

    for clause_num in REQUIRED_CLAUSES:
        text = clauses[clause_num]

        # preserve full meaning (no lossy summarization)
        line = preserve_clause_text(clause_num, text)

        # enforce no scope bleed
        if any(p in line.lower() for p in FORBIDDEN_PHRASES):
            sys.exit(f"Error: Scope bleed detected in clause {clause_num}")

        summary_lines.append(line)

    # final enforcement check
    if len(summary_lines) != len(REQUIRED_CLAUSES):
        sys.exit("Error: Clause omission detected.")

    return "\n".join(summary_lines)


def write_output(output_path, content):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        sys.exit(f"Error writing output: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    write_output(args.output, summary)


if __name__ == "__main__":
    main()