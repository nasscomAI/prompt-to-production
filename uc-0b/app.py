import argparse
import re


def retrieve_policy(path):
    clauses = []

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # find numbered clauses like 2.3, 3.4 etc
    pattern = r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)"

    matches = re.findall(pattern, text, re.S)

    for num, content in matches:
        clauses.append((num.strip(), content.strip()))

    return clauses


def summarize_policy(clauses):

    summary_lines = []

    for num, text in clauses:
        # preserve obligations but shorten wording
        short = text.strip()

        # simple cleanup
        short = short.replace("\n", " ")

        summary_lines.append(f"Clause {num}: {short}")

    return "\n".join(summary_lines)


def main():

    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    if not clauses:
        raise Exception("No clauses found in policy document")

    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()