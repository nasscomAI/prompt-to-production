import argparse

def summarize_policy(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile:
        content = infile.readlines()

    summary_lines = []
    clause_number = 1

    for line in content:
        line = line.strip()

        if not line:
            continue

        # keep numbered clauses
        if line[0].isdigit():
            summary_lines.append(f"Clause {clause_number}: {line}")
            clause_number += 1
        else:
            summary_lines.append(line)

    with open(output_file, "w", encoding="utf-8") as outfile:
        for line in summary_lines:
            outfile.write(line + "\n")


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary")
    parser.add_argument("--input", required=True, help="Policy text file")
    parser.add_argument("--output", required=True, help="Summary output file")

    args = parser.parse_args()

    summarize_policy(args.input, args.output)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()