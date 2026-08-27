"""
UC-0B app.py

Implements:
1. retrieve_policy
2. summarize_policy

Based on:
- agents.md
- skills.md
- README.md
"""

import argparse
import os
import re


def retrieve_policy(file_path: str):
    """
    Loads a policy text file and returns its content as structured numbered sections.

    Returns:
        tuple(dict, error_message)

        Example:
        (
            {
                "2.3": "...",
                "2.4": "..."
            },
            None
        )
    """
    if not file_path:
        return {}, "Input file path is empty."

    if not file_path.lower().endswith(".txt"):
        return {}, "Input file must be a .txt document."

    if not os.path.exists(file_path):
        return {}, f"Policy file not found: {file_path}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return {}, f"Unable to read policy file: {e}"

    sections = {}
    
    # Robust regex matching clause numbers like 2.3, 5.12 followed by optional punctuation/whitespace
    clause_pattern = re.compile(r"^(\d+\.\d+)\b[.:\s-]*\s*(.*)$")
    current_clause = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = clause_pattern.match(line)
        if match:
            current_clause = match.group(1)
            sections[current_clause] = match.group(2).strip()
        elif current_clause:
            sections[current_clause] = (sections[current_clause] + " " + line).strip()

    # Clean up multi-whitespace sequences within parsed sections
    for clause in sections:
        sections[clause] = re.sub(r"\s+", " ", sections[clause]).strip()

    if not sections:
        return {}, "No numbered clauses found in policy."

    return sections, None


def is_complex_clause(text: str):
    """
    Detect clauses that may lose meaning if summarized.
    """
    keywords = [
        " and ",
        " or ",
        " unless ",
        " except ",
        " before ",
        " after ",
        " within ",
        " both ",
        " regardless ",
        ";"
    ]
    lower = text.lower()
    return any(k in lower for k in keywords)


def summarize_policy(sections: dict):
    """
    Produce a compliant summary from structured sections.

    Enforcement:
    - Every numbered clause must appear.
    - Never invent information.
    - Preserve all conditions.
    - Quote complex clauses verbatim and flag them.
    """
    if sections is None or not isinstance(sections, dict) or len(sections) == 0:
        return "ERROR: The input structured sections are invalid or empty."

    summary = []

    def clause_sort_key(value):
        return [int(x) for x in value.split(".")]

    for clause in sorted(sections.keys(), key=clause_sort_key):
        text = sections[clause].strip()

        if is_complex_clause(text):
            summary.append(
                f"{clause}: {text}\n"
                "[FLAG] Clause preserved verbatim to avoid meaning loss."
            )
        else:
            summary.append(f"{clause}: {text}")

    return "\n\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summary Generator"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input policy text file"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output summary text file"
    )
    args = parser.parse_args()

    sections, error = retrieve_policy(args.input)
    if error:
        print(f"Error retrieving policy: {error}")
        return

    summary = summarize_policy(sections)
    if summary.startswith("ERROR:"):
        print(summary)
        return

    # Create directories recursively if the destination path requires it
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            print(f"Unable to create output directory {output_dir}: {e}")
            return

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Unable to write output file: {e}")


if __name__ == "__main__":
    main()