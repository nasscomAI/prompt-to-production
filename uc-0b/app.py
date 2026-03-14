import os

INPUT_FILE = "../data/policy-documents/policy_hr_leave.txt"
OUTPUT_FILE = "summary_hr_leave.txt"


def summarize(text):
    """
    Simple rule-based summary ensuring numbered clauses are preserved.
    """

    lines = text.split("\n")

    summary = []
    for line in lines:
        line = line.strip()
        if line.startswith(("1.", "2.", "3.", "4.", "5.")):
            summary.append(line)

    if not summary:
        summary = lines[:5]

    return "\n".join(summary)


def main():

    with open(INPUT_FILE, "r") as f:
        text = f.read()

    summary = summarize(text)

    with open(OUTPUT_FILE, "w") as f:
        f.write(summary)

    print("Summary written to", OUTPUT_FILE)


if __name__ == "__main__":
    main()