import argparse
import re


def retrieve_policy(input_path):
    with open(input_path, "r", encoding="utf-8") as file:
        return file.read()


def summarize_policy(policy_text):
    summary = []
    clause_pattern = r"^\d+\.\d+"

    for line in policy_text.splitlines():
        line = line.strip()
        if not line:
            continue

        if re.match(clause_pattern, line):
            summary.append(line)
        else:
            summary.append(line)

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Summary saved to {args.output}")


if __name__ == "__main__":
    main()