"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse


def retrieve_policy(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        return file.readlines()


def summarize_policy(lines):

    summary = []

    for line in lines:

        text = line.strip()

        if not text:
            continue

        summary.append(text)

    return summary


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    policy = retrieve_policy(args.input)

    summary = summarize_policy(policy)

    with open(args.output, "w", encoding="utf-8") as file:

        file.write("HR Leave Policy Summary\n")
        file.write("=" * 30)
        file.write("\n\n")

        for item in summary:
            file.write(f"- {item}\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()