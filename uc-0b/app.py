import argparse


def retrieve_policy(file_path):
    clauses = []

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # keep only numbered clauses
        if line and line[0].isdigit():
            clauses.append(line)

    return clauses


def summarize_policy(clauses):
    summary = []

    for clause in clauses:
        # For UC-0B we preserve the clause to avoid losing conditions
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

    print("Summary generated successfully.")


if __name__ == "__main__":
    main()