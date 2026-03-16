import argparse


def summarize_policy(input_file, output_file):

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    sentences = text.split(".")
    summary = sentences[:5]

    summary_text = ".".join(summary)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary_text)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    summarize_policy(args.input, args.output)
