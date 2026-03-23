import argparse
import os


def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Input file not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    clauses = []

    for line in lines:
        line = line.strip()
        if line and any(char.isdigit() for char in line[:3]):
            clauses.append(line)

    if not clauses:
        raise ValueError("No clauses found in document")

    return clauses


def summarize_policy(clauses):
    summary = []
    for clause in clauses:
        summary.append(clause)
    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Summary generated successfully!")

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    main()
