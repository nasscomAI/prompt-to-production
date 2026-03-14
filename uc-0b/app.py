"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import argparse

def summarize_policy(text):
    lines = text.split("\n")
    summary = []

    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            summary.append(line)

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        policy_text = f.read()

    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary saved to:", args.output)


if __name__ == "__main__":
    main()
