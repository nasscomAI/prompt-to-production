import argparse

# Function to summarize policy text
def summarize(text):
    lines = text.split("\n")

    important_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Keep lines with numbers or key rules
        if any(char.isdigit() for char in line):
            important_lines.append(line)
        elif "must" in line.lower() or "only" in line.lower() or "required" in line.lower():
            important_lines.append(line)

    summary = " ".join(important_lines)
    return summary


def process_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    summary = summarize(text)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    process_file(args.input, args.output)

    print("Summary generated and saved to:", args.output)