import argparse

def retrieve_policy(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.readlines()

    clauses = []
    for line in text:
        line = line.strip()
        if line and line[0].isdigit():
            clauses.append(line)

    return clauses


def summarize_policy(clauses):
    summary_lines = []

    for clause in clauses:
        summary_lines.append(clause)

    return "\n".join(summary_lines)


def main(input_path, output_path):
    clauses = retrieve_policy(input_path)

    summary = summarize_policy(clauses)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    main(args.input, args.output)

    print(f"Summary written to {args.output}")