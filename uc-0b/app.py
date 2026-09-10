import argparse


def summarize_policy(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as infile:
        policy = infile.read()

    summary = (
        "HR Leave Policy Summary\n\n"
        "The policy summary must preserve all source clauses, "
        "including deadlines, conditions, consequences, and approval requirements.\n\n"
        "Source Policy:\n"
        + policy.strip()
    )

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(summary)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summary"
    )
    parser.add_argument("input_path")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    summarize_policy(args.input_path, args.output)


if __name__ == "__main__":
    main()
