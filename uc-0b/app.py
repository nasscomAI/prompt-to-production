import argparse

def retrieve_policy(input_path):
    clauses = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # detect numbered clauses
            if line and line[0].isdigit():
                clauses.append(line)

    return clauses


def summarize_policy(clauses):
    summary = []

    for clause in clauses:
        summary.append(clause)

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()