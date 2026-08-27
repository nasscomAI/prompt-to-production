"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def summarize(text):
    sentences = text.split(".")
    return ".".join(sentences[:2]) + "."

def main(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    summary = summarize(text)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print("Summary generated:", output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    main(args.input, args.output)