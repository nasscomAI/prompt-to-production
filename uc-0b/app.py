import argparse

def summarize_policy(text):
    lines = text.split("\n")
    summary = []

    for line in lines:
        if line.strip() != "":
            summary.append(line.strip())

    return "\n".join(summary[:5])


def main(input_path, output_path):

    with open(input_path, "r") as infile:
        text = infile.read()

    summary = summarize_policy(text)

    with open(output_path, "w") as outfile:
        outfile.write(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    main(args.input, args.output)

    print("Summary written to", args.output)