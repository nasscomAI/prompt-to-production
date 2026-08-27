"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import argparse

def summarize_text(text: str) -> str:
    """Create a short summary of the text."""
    if not text.strip():
        return "summary unavailable"
    # naive summary: first 20 words
    words = text.split()
    return " ".join(words[:20]) + ("..." if len(words) > 20 else "")

def detect_bias(original: str, summary: str) -> str:
    """Check if summary changes meaning of original text."""
    if not original.strip() or not summary.strip():
        return "uncertain"
    # naive check: if summary contains fewer than half the words, flag
    if len(summary.split()) < len(original.split()) / 2:
        return "possible bias"
    return "no bias detected"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to input text file")
    parser.add_argument("--output", required=True, help="Path to output text file")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as infile:
        original = infile.read()

    summary = summarize_text(original)
    bias_flag = detect_bias(original, summary)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write("Original:\n" + original + "\n\n")
        outfile.write("Summary:\n" + summary + "\n\n")
        outfile.write("Bias Check:\n" + bias_flag + "\n")

    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
