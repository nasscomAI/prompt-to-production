import sys
import argparse

def summarize_policy(text):
    # Example summarizer: splits text into sentences and keeps the first 3 as summary
    sentences = text.split(".")
    summary = ". ".join(sentences[:3]) + "."
    return summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to save summary")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    # Read the policy document
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Generate summary
    summary = summarize_policy(text)

    # Save summary to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary completed! Output saved to {output_file}")

if __name__ == "__main__":
    main()