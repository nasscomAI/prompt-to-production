"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse


def retrieve_policy(path):
    """
    Reads the policy file and extracts numbered clauses.
    """
    clauses = []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Detect numbered clause patterns like "2.3 ..."
        if line and line[0].isdigit() and "." in line:
            clauses.append(line)

    return clauses


def summarize_policy(clauses):
    """
    Generate summary while preserving obligations and conditions.
    """
    summary = []
    summary.append("Summary of HR Leave Policy\n")

    for clause in clauses:
        summary.append(clause)

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary written to", args.output)


if __name__ == "__main__":
    main()