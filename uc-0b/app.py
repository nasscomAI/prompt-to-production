import argparse
import re
import sys


def retrieve_policy(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

    # Extract clauses like 2.3, 2.4 etc.
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        raise ValueError("No clauses found in document")

    clauses = {}
    for num, content in matches:
        clauses[num.strip()] = content.strip()

    return clauses


def summarize_policy(clauses):
    expected_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

    summary_lines = []

    for clause in expected_clauses:
        if clause not in clauses:
            raise ValueError(f"Missing clause: {clause}")

        text = clauses[clause]

        # Enforcement: preserve meaning strictly
        # If clause has multiple conditions (like AND), keep verbatim
        if " and " in text.lower() or " or " in text.lower():
            summary = text  # do not summarize
        else:
            summary = text  # simple safe fallback (no aggressive summarization)

        # Prevent scope bleed (basic filter)
        forbidden_phrases = [
            "typically", "generally", "standard practice",
            "usually", "in most cases"
        ]
        for phrase in forbidden_phrases:
            if phrase in summary.lower():
                raise ValueError("Scope bleed detected")

        summary_lines.append(f"{clause}: {summary}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Summary generated successfully.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()