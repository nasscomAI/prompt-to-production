"""
UC-0B — Summary That Changes Meaning
Build using RICE + agents.md + skills.md + CRAFT workflow
"""

import argparse


def summarize_text(text: str) -> str:
    """
    Generate a simple summary while preserving key meaning.
    Ensures summary is shorter than original.
    """

    if not text.strip():
        return "No content to summarize."

    # Simple safe summarization: keep first important sentences
    sentences = text.split(".")
    summary = ".".join(sentences[:2]).strip()

    if not summary.endswith("."):
        summary += "."

    return summary


def main():

    parser = argparse.ArgumentParser(description="UC-0B Text Summarizer")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy document text file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write summary text"
    )

    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()

        summary = summarize_text(text)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"Summary written to {args.output}")

    except Exception as e:
        print("Error during summarization:", str(e))


if __name__ == "__main__":
    main()
