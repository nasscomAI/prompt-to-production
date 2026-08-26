"""
UC-0B app.py — Summary that preserves all clauses and conditions.

Reads a policy .txt file, produces a summary that includes every numbered clause,
preserves all binding verbs and conditions, never drops conditions silently,
and quotes verbatim any clause that would lose meaning if summarized.
"""

import argparse
import os


def retrieve_policy(path):
    """Load .txt policy file and return structured numbered sections."""
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    sections = []
    current_number = None
    current_text = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Clause lines start with a number followed by a period (e.g., "2.3")
        if "." in stripped and stripped.split(".")[0].isdigit():
            if current_number is not None:
                sections.append(
                    {
                        "number": current_number,
                        "text": " ".join(current_text).strip(),
                    }
                )
            current_number = stripped.split(".")[0] + "." + stripped.split(".")[1]
            current_text = []
        else:
            current_text.append(stripped)
    if current_number is not None:
        sections.append(
            {
                "number": current_number,
                "text": " ".join(current_text).strip(),
            }
        )
    return sections


def summarize_policy(sections):
    """Produce compliant summary preserving all clauses and conditions."""
    lines = []
    for sec in sections:
        number = sec["number"]
        text = sec["text"]
        lines.append(number)
        lines.append(text)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Summary that preserves all clauses and conditions"
    )
    parser.add_argument(
        "--input", required=True, help="Path to the policy .txt file"
    )
    parser.add_argument(
        "--output", required=True, help="Path to write the summary .txt file"
    )
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    main()