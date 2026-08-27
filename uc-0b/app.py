import argparse

def retrieve_policy(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clauses = {}
    for line in lines:
        if "." in line[:5]:
            parts = line.split(" ",1)
            if len(parts) > 1:
                clause = parts[0]
                text = parts[1].strip()
                clauses[clause] = text
    return clauses


def summarize_policy(clauses):

    summary_lines = []

    for clause, text in clauses.items():
        summary_lines.append(f"{clause}: {text}")

    return "\n".join(summary_lines)


def main(input_file, output_file):

    clauses = retrieve_policy(input_file)

    summary = summarize_policy(clauses)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    main(args.input, args.output)
