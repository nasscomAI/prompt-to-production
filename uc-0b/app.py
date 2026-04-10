import argparse
import sys


def retrieve_policy(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: Policy file not found.")
        sys.exit(1)


def summarize_policy(text):
    lines = text.split("\n")
    summary = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Always keep numbered clauses (robust check)
        if line[:2].replace(".", "").isdigit():
            summary.append(line)
            continue

        # Keep obligation lines
        if any(
            keyword in line.lower()
            for keyword in ["must", "requires", "not permitted", "will"]
        ):
            summary.append(line)

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    text = retrieve_policy(args.input)
    summary = summarize_policy(text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary saved to {args.output}")


if __name__ == "__main__":
    main()
