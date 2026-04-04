import argparse

def summarize_policy(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    summary = []

    for line in lines:
        line = line.strip()
        if line:  # keep all non-empty lines
            summary.append(line)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary))

    print("Summary generated successfully!")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    summarize_policy(args.input, args.output)

if __name__ == "__main__":
    main()