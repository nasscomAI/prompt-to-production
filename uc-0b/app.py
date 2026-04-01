import argparse

def retrieve_policy(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def summarize_policy(policy_text):
    summary = []
    lines = policy_text.split("\n")

    for line in lines:
        line = line.strip()
        if line.startswith(("2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2")):
            summary.append(line)

    if not summary:
        summary.append("No clauses detected — NEEDS_REVIEW")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    policy_text = retrieve_policy(args.input)

    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()