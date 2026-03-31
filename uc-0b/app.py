import argparse
import re
import sys

# UC-0B Submission - Policy Summarizer

def retrieve_policy(file_path):
    """
    Loads the policy file and splits into numbered clauses.
    Returns an ordered list of (clause_num, clause_text) tuples.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError as e:
        raise OSError(f"Error reading file: {e}") from e

    # Remove separator lines and section headers
    content = re.sub(r'^[═=\-]{3,}.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\d+\.\s+[A-Z][A-Z\s]+$', '', content, flags=re.MULTILINE)

    # Match clauses like: 2.3 text OR 2.3: text
    pattern = r'(?m)^(\d+\.\d+)[\.:]?\s+'
    parts = re.split(pattern, content)

    # Ignore preamble silently (no debug print)
    preamble = parts[0].strip()

    if len(parts) < 3 or len(parts) % 2 == 0:
        raise ValueError(
            f"Unexpected parse result (segments={len(parts)}). "
            "Check clause formatting."
        )

    clauses = {}
    for i in range(1, len(parts), 2):
        clause_num = parts[i]
        clause_text = re.sub(r'\s+', ' ', parts[i + 1]).strip()

        if not clause_text:
            raise ValueError(f"Empty clause detected: {clause_num}")
        if clause_num in clauses:
            raise ValueError(f"Duplicate clause number: {clause_num}")

        clauses[clause_num] = clause_text

    if not clauses:
        raise ValueError("No clauses found in policy file.")

    # Sort clauses numerically
    sorted_clauses = sorted(
        clauses.items(),
        key=lambda x: tuple(int(p) for p in x[0].split('.'))
    )

    return sorted_clauses


def summarize_policy(clauses):
    """
    Safe summary:
    - No clause omission
    - No condition loss
    - Keeps full clause text
    """
    summary_lines = []

    for clause_num, text in clauses:
        if not text.strip():
            raise RuntimeError(f"Empty clause detected: {clause_num}")

        summary_lines.append(f"{clause_num}: {text}")

    if len(summary_lines) != len(clauses):
        raise RuntimeError(
            f"Clause omission: {len(clauses)} in, {len(summary_lines)} out."
        )

    return "\n".join(summary_lines)


def write_output(output_path, content):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except OSError as e:
        raise OSError(f"Error writing file: {e}") from e


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument('--input', required=True, help="Input policy file")
    parser.add_argument('--output', required=True, help="Output summary file")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        write_output(args.output, summary)
        print(f"Summary generated successfully ({len(clauses)} clauses).")
    except (OSError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()