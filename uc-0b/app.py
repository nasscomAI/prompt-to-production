"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def main():
    import argparse

def summarize(text):

    sentences = text.split(".")
    summary = ". ".join(sentences[:5])

    return summary


def run(input_file, output_file):

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    summary = summarize(text)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary generated")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    run(args.input, args.output)
if __name__ == "__main__":
    main()
