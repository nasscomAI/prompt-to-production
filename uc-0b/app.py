import argparse


def summarize_policy(text: str) -> str:
    """
    Generate a summary while preserving every numbered clause.
    """

    lines = text.split("\n")
    summary_lines = []

    for line in lines:
        line = line.strip()

        # Keep numbered clauses like "1.", "2.", etc.
        if line and line[0].isdigit():
            summary_lines.append(line)

    if not summary_lines:
        return "No numbered clauses found in policy document."

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to write summary")

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    summary = summarize_policy(text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()