import argparse
import re


REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2"
]


def retrieve_policy(path):
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    clauses = {}

    for clause in REQUIRED_CLAUSES:
        pattern = rf"(?m)^\s*{re.escape(clause)}\s+.*?(?=^\s*\d+\.\d+\s+|\Z)"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            clauses[clause] = " ".join(match.group(0).split())

    return clauses


def summarize_policy(clauses):
    lines = []

    for clause in REQUIRED_CLAUSES:
        if clause in clauses:
            lines.append(f"{clause}: {clauses[clause]}")
        else:
            lines.append(
                f"{clause}: [REVIEW REQUIRED - clause missing from source]"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="HR Leave Policy Summarizer"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        with open(args.output, "w", encoding="utf-8") as file:
            file.write(summary + "\n")

        print(f"Done. Summary written to {args.output}")

    except Exception as exc:
        print(f"Error: {exc}")
        raise


if __name__ == "__main__":
    main()