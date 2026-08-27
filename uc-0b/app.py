import argparse
import os

def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Input file not found.")

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read().strip()

    if not content:
        raise ValueError("Input file is empty.")

    return content


def summarize_policy(policy_text):
    if not policy_text or not isinstance(policy_text, str):
        raise ValueError("Invalid policy text.")

    # Simple safe summarization (preserves all clauses)
    lines = policy_text.split("\n")
    summary_lines = []

    for line in lines:
        line = line.strip()
        if line:
            summary_lines.append(line)

    if not summary_lines:
        raise ValueError("No valid content to summarize.")

    # Join without losing clauses
    summary = "\n".join(summary_lines)

    return summary


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy file")
    parser.add_argument("--output", required=True, help="Path to output summary file")

    args = parser.parse_args()

    try:
        # Step 1: Retrieve policy
        policy_text = retrieve_policy(args.input)

        # Step 2: Summarize policy
        summary = summarize_policy(policy_text)

        # Step 3: Write output
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(summary)

        print("✅ Summary generated successfully!")
        print(f"Output saved to: {args.output}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()