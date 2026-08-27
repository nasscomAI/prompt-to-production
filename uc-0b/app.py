import argparse
import os

def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Input file not found")

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read().strip()

    if not content:
        raise ValueError("Policy document is empty")

    return content


def summarize_policy(text):
    # Simple safe summarization (no clause removal)
    lines = text.split("\n")
    summary = []

    for line in lines:
        line = line.strip()
        if line:
            summary.append(line)

    if not summary:
        return "Refusal: Unable to summarize due to insufficient content."

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file path")

    args = parser.parse_args()

    try:
        # Step 1: Retrieve policy
        policy_text = retrieve_policy(args.input)

        # Step 2: Summarize policy
        summary = summarize_policy(policy_text)

        # Step 3: Save output
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(summary)

        print("Summary generated successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()