import argparse

def summarize_policy(input_file, output_file):

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    summary = []

    for line in lines:
        line = line.strip()

        if line:
            summary.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        for line in summary:
            f.write(line + "\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    summarize_policy(args.input, args.output)