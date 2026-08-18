import argparse
import re


REQUIRED_CLAUSES = [
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
]


def retrieve_policy(path):
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    sections = {}

    for clause in REQUIRED_CLAUSES:
        pattern = rf"^{re.escape(clause)}\s+(.*?)(?=^(?:\d+\.\d+\s|[═]+|\d+\.\s)|\Z)"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

        if match:
            sections[clause] = " ".join(match.group(1).split())

    return sections


def summarize_policy(sections):
    summary = []

    for clause in REQUIRED_CLAUSES:
        if clause in sections:
            summary.append(f"{clause}: {sections[clause]}")
        else:
            summary.append(
                f"{clause}: [REVIEW REQUIRED - clause not found in source]"
            )

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Leave Policy Summarizer"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary)
        file.write("\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()