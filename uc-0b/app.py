import argparse
import os


def summarize_policy(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "Error: Input policy document is empty."

    summary_points = []
    for line in lines:
        if len(line) > 20:
            summary_points.append(f"- {line}")

    if not summary_points:
        return "Error: No meaningful policy content found."

    intro = "Summary of HR Leave Policy:\n\n"
    return intro + "\n".join(summary_points[:10])


def main():
    parser = argparse.ArgumentParser(description="Summarize HR leave policy")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file not found: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        policy_text = f.read()

    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
