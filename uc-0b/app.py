import os

INPUT_FILE = "../data/policy-documents/policy_hr_leave.txt"
OUTPUT_FILE = "summary_hr_leave.txt"


def summarize_policy(text):
    lines = text.split("\n")
    summary_lines = []

    for line in lines:
        line = line.strip()

        # keep numbered clauses
        if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            summary_lines.append(line)

    return "\n".join(summary_lines)


def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        policy_text = f.read()

    summary = summarize_policy(policy_text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary generated →", OUTPUT_FILE)


if __name__ == "__main__":
    main()