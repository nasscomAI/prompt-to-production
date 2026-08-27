"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def main():

    parser = argparse.ArgumentParser(description="UC-0B Policy Summary")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    with open(args.input, "r") as infile:
        text = infile.readlines()

    summary_lines = []

    for line in text:
        if line.strip() != "":
            summary_lines.append(line.strip())

    summary = "\n".join(summary_lines[:5])

    with open(args.output, "w") as outfile:
        outfile.write(summary)

    print("Summary written to", args.output)


if __name__ == "__main__":
    main()

