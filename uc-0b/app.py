import argparse

def retrieve_policy(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clauses = []
    for line in lines:
        line = line.strip()
        if line:
            clauses.append(line)

    return clauses


def summarize_policy(clauses):
    summary = []

    for clause in clauses:
        # SAFE: do not remove meaning
        summary.append(clause)

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    print("Reading policy...")

    clauses = retrieve_policy(args.input)
    print("Total clauses:", len(clauses))

    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary written to:", args.output)


if __name__ == "__main__":
    main()