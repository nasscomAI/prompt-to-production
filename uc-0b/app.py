"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re


def retrieve_policy(input_path: str):
    """
    Loads policy file and extracts numbered clauses.
    Returns dictionary {clause_number: clause_text}
    """

    clauses = {}

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match patterns like 2.3, 5.2, etc.
    matches = re.split(r"\n(?=\d+\.\d+)", content)

    for clause in matches:
        match = re.match(r"(\d+\.\d+)\s+(.*)", clause.strip(), re.DOTALL)
        if match:
            number = match.group(1)
            text = match.group(2).strip()
            clauses[number] = text

    return clauses


def summarize_policy(clauses: dict):
    """
    Produces summary ensuring every clause appears.
    Preserves conditions from original clause.
    """

    summary_lines = []

    for number, text in sorted(clauses.items()):

        # simple summarization: preserve key sentence
        first_sentence = text.split(".")[0].strip()

        # if clause is complex, quote full clause
        if len(text.split()) > 25:
            summary = f"{number}: \"{text}\""
        else:
            summary = f"{number}: {first_sentence}."

        summary_lines.append(summary)

    return "\n".join(summary_lines)


def main():

    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write summary file"
    )

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()